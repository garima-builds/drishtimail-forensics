"""Backend Graph & Campaign Clustering Verification Tests (F6 / M5).

Tests:
1. Typed property graph node creation (MESSAGE, SENDER_EMAIL, DOMAIN, IP, URL, STRUCTURAL_HASH).
2. Typed relationship edges (has_sender, has_domain, mentions_domain, contains_url, routed_via_ip).
3. Neighborhood graph exploration for Cytoscape.js.
4. Campaign clustering logic:
   - Returns single isolated baseline when only 1 message exists.
   - Detects real multi-incident coordinated threat campaigns when indicators are shared across messages.
"""
import unittest
import os
import sys
import uuid
from sqlalchemy import select

# Ensure backend package is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base, engine, SessionLocal
from app.models import Message, GraphNode, GraphEdge, EvidenceObject, EvidenceReference
from app.correlation.graph_service import (
    get_or_create_node, record_graph_link,
    link_message_indicators, explore_graph_neighborhood,
    cluster_and_update_campaigns,
)


class TestGraphCampaigns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    def setUp(self):
        self.db = SessionLocal()
        # Create a dummy evidence object & reference
        h = uuid.uuid4().hex
        self.orig = EvidenceObject(sha256=h, storage_key=f"test/{h}.eml", filename="test.eml", byte_size=100)
        self.db.add(self.orig)
        self.db.flush()
        self.ref = EvidenceReference(evidence_object_id=self.orig.id, byte_start=0, byte_end=100, description="Test Ref")
        self.db.add(self.ref)
        self.db.flush()

    def tearDown(self):
        self.db.rollback()
        self.db.close()

    def test_01_typed_node_and_edge_creation(self):
        """Verify typed node creation and edge linking."""
        msg_id = uuid.uuid4()
        msg = Message(
            id=msg_id,
            sender="alert@evil-bank.xyz",
            subject="Urgent Account Verification",
            verdict="Critical",
            score=90,
            confidence="High",
            status="New",
            evidence_reference=str(self.ref.id),
        )
        self.db.add(msg)
        self.db.flush()

        indicators = [
            {"indicator_type": "sender_email", "value": "alert@evil-bank.xyz"},
            {"indicator_type": "domain", "value": "evil-bank.xyz"},
            {"indicator_type": "url", "value": "https://evil-bank.xyz/login"},
            {"indicator_type": "ip", "value": "198.51.100.55"},
            {"indicator_type": "structural_hash", "value": "hash_abc_123"},
        ]

        link_message_indicators(self.db, msg_id, indicators, self.ref.id)
        self.db.commit()

        # Check nodes created
        node_types = self.db.scalars(select(GraphNode.node_type)).all()
        self.assertIn("message", node_types)
        self.assertIn("sender_email", node_types)
        self.assertIn("domain", node_types)
        self.assertIn("url", node_types)
        self.assertIn("ip", node_types)
        self.assertIn("structural_hash", node_types)

        # Check typed edges
        edge_types = self.db.scalars(select(GraphEdge.edge_type)).all()
        self.assertIn("has_sender", edge_types)
        self.assertIn("mentions_domain", edge_types)
        self.assertIn("has_domain", edge_types)
        self.assertIn("contains_url", edge_types)
        self.assertIn("routed_via_ip", edge_types)
        self.assertIn("shares_structural_fingerprint", edge_types)

    def test_02_graph_neighborhood_exploration(self):
        """Verify explore_graph_neighborhood returns Cytoscape-formatted nodes and edges."""
        graph = explore_graph_neighborhood(self.db, "")
        self.assertIn("nodes", graph)
        self.assertIn("edges", graph)
        self.assertIsInstance(graph["nodes"], list)
        self.assertIsInstance(graph["edges"], list)

        if graph["nodes"]:
            sample_node = graph["nodes"][0]
            self.assertIn("id", sample_node)
            self.assertIn("node_type", sample_node)
            self.assertIn("value", sample_node)
            self.assertIn("label", sample_node)

        if graph["edges"]:
            sample_edge = graph["edges"][0]
            self.assertIn("source", sample_edge)
            self.assertIn("target", sample_edge)
            self.assertIn("label", sample_edge)
            self.assertIn("edge_type", sample_edge)

    def test_03_campaign_clustering_multi_incident(self):
        """Verify multi-message campaign clustering when indicators are shared."""
        msg1_id = uuid.uuid4()
        msg2_id = uuid.uuid4()
        shared_domain = f"campaign-target-{uuid.uuid4().hex[:6]}.com"

        # Message 1
        m1 = Message(id=msg1_id, sender=f"phish1@{shared_domain}", subject="Attack 1", verdict="Critical", score=85, confidence="High", status="New", evidence_reference=str(self.ref.id))
        self.db.add(m1)
        link_message_indicators(self.db, msg1_id, [{"indicator_type": "domain", "value": shared_domain}], self.ref.id)

        # Message 2 sharing the same domain
        m2 = Message(id=msg2_id, sender=f"phish2@{shared_domain}", subject="Attack 2", verdict="Critical", score=85, confidence="High", status="New", evidence_reference=str(self.ref.id))
        self.db.add(m2)
        link_message_indicators(self.db, msg2_id, [{"indicator_type": "domain", "value": shared_domain}], self.ref.id)
        self.db.commit()

        campaigns = cluster_and_update_campaigns(self.db)
        self.assertGreater(len(campaigns), 0)
        
        # Check that the shared domain cluster was formed
        matched_cluster = next((c for c in campaigns if shared_domain in c["name"]), None)
        self.assertIsNotNone(matched_cluster, f"Expected cluster for {shared_domain}")
        self.assertGreaterEqual(matched_cluster["message_count"], 2)
        self.assertIn(str(msg1_id), [str(x) for x in matched_cluster.get("connected_message_ids", [])])
        self.assertIn(str(msg2_id), [str(x) for x in matched_cluster.get("connected_message_ids", [])])

    def test_04_no_orphan_or_dangling_edges(self):
        """Verify that explore_graph_neighborhood never returns edges with nonexistent source or target nodes."""
        graph = explore_graph_neighborhood(self.db, "")
        node_ids = {n["id"] for n in graph["nodes"]}

        for edge in graph["edges"]:
            source_id = edge["source"]
            target_id = edge["target"]
            self.assertIn(
                source_id,
                node_ids,
                f"Edge {edge['id']} has dangling source {source_id} not present in graph nodes"
            )
            self.assertIn(
                target_id,
                node_ids,
                f"Edge {edge['id']} has dangling target {target_id} not present in graph nodes"
            )


if __name__ == "__main__":
    unittest.main()
