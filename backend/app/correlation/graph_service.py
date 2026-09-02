"""F6: Campaign Memory & Correlation Graph Service.

Maintains a typed property graph:
Nodes: message, sender_email, domain, ip, url, structural_hash, file_hash
Edges: has_sender, has_domain, mentions_domain, contains_url, routed_via_ip, shares_structural_fingerprint
Traverses connections and clusters multi-message incidents into campaigns.
"""
import uuid
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import GraphNode, GraphEdge, Message


def get_or_create_node(db: Session, node_type: str, value: str) -> GraphNode:
    val = value.strip().lower()
    node = db.scalar(select(GraphNode).where(GraphNode.node_type == node_type, GraphNode.value == val))
    if not node:
        node = GraphNode(node_type=node_type, value=val, sighting_count=1)
        db.add(node)
        db.flush()
    else:
        node.sighting_count += 1
    return node


def record_graph_link(
    db: Session,
    from_node_id: uuid.UUID,
    to_node_id: uuid.UUID,
    edge_type: str,
    evidence_reference_id: uuid.UUID,
    weight: float = 1.0,
) -> GraphEdge:
    edge = db.scalar(
        select(GraphEdge).where(
            GraphEdge.from_node == from_node_id,
            GraphEdge.to_node == to_node_id,
            GraphEdge.edge_type == edge_type,
        )
    )
    if not edge:
        edge = GraphEdge(
            from_node=from_node_id,
            to_node=to_node_id,
            edge_type=edge_type,
            weight=weight,
            evidence_reference_id=evidence_reference_id,
        )
        db.add(edge)
        db.flush()
    return edge


def link_message_indicators(
    db: Session,
    message_id: uuid.UUID,
    indicators: list[dict[str, Any]],
    evidence_reference_id: uuid.UUID,
) -> None:
    """Link a message to its extracted indicators in a structured property graph."""
    msg = db.get(Message, message_id)
    msg_label = f"Msg: {msg.subject[:25]}..." if (msg and msg.subject) else f"Message-{str(message_id)[:8]}"
    msg_node = get_or_create_node(db, "message", str(message_id))

    sender_email_node = None

    for ind in indicators:
        t = ind.get("indicator_type", "domain")
        v = ind.get("value", "")
        if not v:
            continue
        ind_node = get_or_create_node(db, t, v)

        if t == "sender_email":
            sender_email_node = ind_node
            record_graph_link(
                db,
                from_node_id=msg_node.id,
                to_node_id=ind_node.id,
                edge_type="has_sender",
                evidence_reference_id=evidence_reference_id,
            )
        elif t == "domain":
            record_graph_link(
                db,
                from_node_id=msg_node.id,
                to_node_id=ind_node.id,
                edge_type="mentions_domain",
                evidence_reference_id=evidence_reference_id,
            )
            if sender_email_node:
                record_graph_link(
                    db,
                    from_node_id=sender_email_node.id,
                    to_node_id=ind_node.id,
                    edge_type="has_domain",
                    evidence_reference_id=evidence_reference_id,
                )
        elif t == "url":
            record_graph_link(
                db,
                from_node_id=msg_node.id,
                to_node_id=ind_node.id,
                edge_type="contains_url",
                evidence_reference_id=evidence_reference_id,
            )
        elif t == "ip":
            record_graph_link(
                db,
                from_node_id=msg_node.id,
                to_node_id=ind_node.id,
                edge_type="routed_via_ip",
                evidence_reference_id=evidence_reference_id,
            )
        elif t == "structural_hash":
            record_graph_link(
                db,
                from_node_id=msg_node.id,
                to_node_id=ind_node.id,
                edge_type="shares_structural_fingerprint",
                evidence_reference_id=evidence_reference_id,
            )
        elif t == "file_hash":
            record_graph_link(
                db,
                from_node_id=msg_node.id,
                to_node_id=ind_node.id,
                edge_type="contains_file_hash",
                evidence_reference_id=evidence_reference_id,
            )
        else:
            record_graph_link(
                db,
                from_node_id=msg_node.id,
                to_node_id=ind_node.id,
                edge_type=f"has_{t}",
                evidence_reference_id=evidence_reference_id,
            )


def explore_graph_neighborhood(
    db: Session,
    node_id_or_value: str,
    max_depth: int = 2,
) -> dict[str, Any]:
    """Explore connected graph nodes and edges around a starting pivot point."""
    node = None
    if node_id_or_value:
        try:
            val_uuid = uuid.UUID(node_id_or_value)
            node = db.get(GraphNode, val_uuid)
        except ValueError:
            node = db.scalar(select(GraphNode).where(GraphNode.value == node_id_or_value.strip().lower()))

    if not node:
        all_nodes = db.scalars(select(GraphNode).order_by(GraphNode.first_seen.desc()).limit(100)).all()
        all_edges = db.scalars(select(GraphEdge).limit(200)).all()
        return {
            "nodes": [
                {
                    "id": str(n.id),
                    "node_type": n.node_type.upper(),
                    "value": n.value,
                    "label": f"{n.node_type.upper()}: {n.value[:30]}",
                    "first_seen": n.first_seen.isoformat(),
                    "sighting_count": n.sighting_count,
                }
                for n in all_nodes
            ],
            "edges": [
                {
                    "id": f"{str(e.from_node)}-{str(e.to_node)}-{e.edge_type}",
                    "source": str(e.from_node),
                    "target": str(e.to_node),
                    "from_node": str(e.from_node),
                    "to_node": str(e.to_node),
                    "edge_type": e.edge_type,
                    "label": e.edge_type.replace("_", " "),
                    "weight": e.weight,
                    "evidence_reference_id": str(e.evidence_reference_id),
                }
                for e in all_edges
            ],
        }

    visited_node_ids = {node.id}
    collected_edges: list[GraphEdge] = []
    current_level = {node.id}

    for _ in range(max_depth):
        if not current_level:
            break
        edges = db.scalars(
            select(GraphEdge).where(
                (GraphEdge.from_node.in_(current_level)) | (GraphEdge.to_node.in_(current_level))
            )
        ).all()
        next_level = set()
        for e in edges:
            collected_edges.append(e)
            for n_id in (e.from_node, e.to_node):
                if n_id not in visited_node_ids:
                    visited_node_ids.add(n_id)
                    next_level.add(n_id)
        current_level = next_level

    nodes = db.scalars(select(GraphNode).where(GraphNode.id.in_(visited_node_ids))).all()

    return {
        "nodes": [
            {
                "id": str(n.id),
                "node_type": n.node_type.upper(),
                "value": n.value,
                "label": f"{n.node_type.upper()}: {n.value[:30]}",
                "first_seen": n.first_seen.isoformat(),
                "sighting_count": n.sighting_count,
            }
            for n in nodes
        ],
        "edges": [
            {
                "id": f"{str(e.from_node)}-{str(e.to_node)}-{e.edge_type}",
                "source": str(e.from_node),
                "target": str(e.to_node),
                "from_node": str(e.from_node),
                "to_node": str(e.to_node),
                "edge_type": e.edge_type,
                "label": e.edge_type.replace("_", " "),
                "weight": e.weight,
                "evidence_reference_id": str(e.evidence_reference_id),
            }
            for e in collected_edges
        ],
    }


def cluster_and_update_campaigns(db: Session) -> list[dict[str, Any]]:
    """Group messages sharing domains, IPs, or structural fingerprints into real multi-message campaigns."""
    nodes = db.scalars(
        select(GraphNode).where(
            GraphNode.node_type.in_(["domain", "ip", "structural_hash", "sender_email", "url", "file_hash"])
        )
    ).all()

    candidate_clusters: dict[str, dict[str, Any]] = {}

    for n in nodes:
        edges = db.scalars(
            select(GraphEdge).where(
                GraphEdge.to_node == n.id,
                GraphEdge.edge_type.in_([
                    "has_sender", "mentions_domain", "contains_url",
                    "routed_via_ip", "shares_structural_fingerprint", "contains_file_hash"
                ])
            )
        ).all()
        
        from_node_ids = {e.from_node for e in edges}
        if len(from_node_ids) >= 2:
            # Map graph node UUIDs to message identifiers
            src_nodes = db.scalars(select(GraphNode).where(GraphNode.id.in_(from_node_ids))).all()
            actual_msg_ids = [sn.value for sn in src_nodes if sn.node_type == "message"]

            if len(actual_msg_ids) >= 2:
                cluster_key = f"{n.node_type}:{n.value}"
                candidate_clusters[cluster_key] = {
                    "id": str(n.id),
                    "name": f"Coordinated Campaign: {n.node_type.replace('_', ' ').title()} [{n.value[:28]}]",
                    "shared_indicators": [f"{n.node_type}:{n.value}"],
                    "message_count": len(actual_msg_ids),
                    "connected_message_ids": actual_msg_ids,
                    "score": 88.0 if n.node_type in ["structural_hash", "url", "file_hash"] else 70.0,
                    "status": "Active Coordinated Threat",
                    "confidence": "High" if len(actual_msg_ids) >= 3 else "Moderate (Shared Infrastructure)",
                    "created_at": n.first_seen.isoformat(),
                }

    if candidate_clusters:
        return sorted(candidate_clusters.values(), key=lambda c: c["message_count"], reverse=True)

    # If no multi-message clusters exist, return honest single baseline if any messages exist
    msg_exists = db.scalar(select(GraphNode).where(GraphNode.node_type == "message"))
    if msg_exists:
        return [{
            "id": "single-incident-cluster",
            "name": "Isolated Incident (Insufficient Correlation Evidence)",
            "shared_indicators": [],
            "message_count": 1,
            "connected_message_ids": [str(msg_exists.id)],
            "score": 20.0,
            "status": "Single Message",
            "confidence": "Insufficient cross-message correlation evidence",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }]

    return []
