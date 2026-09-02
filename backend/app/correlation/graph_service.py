"""F6: Campaign Memory & Correlation Graph Service.

Maintains a typed property graph (nodes: domains, IPs, structural hashes, emails;
edges: shares_ip, shares_domain, shares_fingerprint, contains_url) in PostgreSQL.
Traverses connections using recursive queries and clusters related incidents into campaigns.
"""
import uuid
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from ..models import GraphNode, GraphEdge, Campaign, CampaignMessage, Message


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
    """Link a message to its extracted indicators in the property graph."""
    msg_node = get_or_create_node(db, "message", str(message_id))

    for ind in indicators:
        t = ind.get("indicator_type", "domain")
        v = ind.get("value", "")
        if not v:
            continue
        ind_node = get_or_create_node(db, t, v)
        # Create bidirectional-like typed edge
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
    # Find root node
    node = None
    try:
        val_uuid = uuid.UUID(node_id_or_value)
        node = db.get(GraphNode, val_uuid)
    except ValueError:
        node = db.scalar(select(GraphNode).where(GraphNode.value == node_id_or_value.strip().lower()))

    if not node:
        # Return empty explore structure
        all_nodes = db.scalars(select(GraphNode).limit(50)).all()
        all_edges = db.scalars(select(GraphEdge).limit(100)).all()
        return {
            "nodes": [{"id": str(n.id), "node_type": n.node_type, "value": n.value, "first_seen": n.first_seen.isoformat(), "sighting_count": n.sighting_count} for n in all_nodes],
            "edges": [{"from_node": str(e.from_node), "to_node": str(e.to_node), "edge_type": e.edge_type, "weight": e.weight, "evidence_reference_id": str(e.evidence_reference_id)} for e in all_edges],
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
        "nodes": [{"id": str(n.id), "node_type": n.node_type, "value": n.value, "first_seen": n.first_seen.isoformat(), "sighting_count": n.sighting_count} for n in nodes],
        "edges": [{"from_node": str(e.from_node), "to_node": str(e.to_node), "edge_type": e.edge_type, "weight": e.weight, "evidence_reference_id": str(e.evidence_reference_id)} for e in collected_edges],
    }


def cluster_and_update_campaigns(db: Session) -> list[dict[str, Any]]:
    """Group messages sharing domains, IPs, or structural fingerprints into campaigns."""
    nodes = db.scalars(select(GraphNode).where(GraphNode.node_type.in_(["domain", "ip", "structural_hash"]))).all()
    campaign_results: list[dict[str, Any]] = []

    for n in nodes:
        if n.sighting_count > 1:
            edges = db.scalars(select(GraphEdge).where(GraphEdge.to_node == n.id)).all()
            msg_ids = [str(e.from_node) for e in edges]
            campaign_results.append({
                "campaign_name": f"Campaign: {n.node_type.title()} {n.value[:30]}",
                "shared_indicator": f"{n.node_type}:{n.value}",
                "sighting_count": n.sighting_count,
                "connected_nodes": len(msg_ids),
                "confidence": "Moderate" if n.sighting_count > 2 else "Limited",
            })

    return campaign_results
