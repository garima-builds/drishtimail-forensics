"""M5: Threat Intelligence & IOC Exporter.

Exports extracted indicators in standardized formats:
1. STIX 2.1 JSON
2. MISP JSON
3. CSV
"""
import csv
import io
import json
import uuid
from datetime import datetime, timezone
from typing import Any


def export_indicators_to_csv(indicators: list[dict[str, Any]]) -> str:
    """Export indicator records to CSV string."""
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["indicator_type", "value", "provenance", "first_seen", "sighting_count", "familiarity_band"],
    )
    writer.writeheader()
    for ind in indicators:
        writer.writerow({
            "indicator_type": ind.get("indicator_type", "unknown"),
            "value": ind.get("value", ""),
            "provenance": ind.get("provenance", "unknown"),
            "first_seen": ind.get("first_seen", datetime.now(timezone.utc).isoformat()),
            "sighting_count": ind.get("sighting_count", 1),
            "familiarity_band": ind.get("familiarity_band", "Novel"),
        })
    return output.getvalue()


def export_indicators_to_stix(
    indicators: list[dict[str, Any]],
    case_title: str = "DrishtiMail Forensic Investigation",
) -> dict[str, Any]:
    """Export indicators to a standard STIX 2.1 Bundle JSON."""
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    bundle_id = f"bundle--{uuid.uuid4()}"
    objects: list[dict[str, Any]] = []

    # Create Report Object
    report_id = f"report--{uuid.uuid4()}"
    indicator_refs = []

    for ind in indicators:
        t = ind.get("indicator_type", "domain")
        v = ind.get("value", "")
        ind_id = f"indicator--{uuid.uuid4()}"
        indicator_refs.append(ind_id)

        # STIX 2.1 Pattern mapping
        if t == "domain":
            pattern = f"[domain-name:value = '{v}']"
        elif t == "ip":
            pattern = f"[ipv4-addr:value = '{v}']"
        elif t == "url":
            pattern = f"[url:value = '{v}']"
        elif t == "file_hash":
            pattern = f"[file:hashes.'SHA-256' = '{v}']"
        elif t == "sender_email":
            pattern = f"[email-addr:value = '{v}']"
        else:
            pattern = f"[custom-object:value = '{v}']"

        objects.append({
            "type": "indicator",
            "spec_version": "2.1",
            "id": ind_id,
            "created": now_iso,
            "modified": now_iso,
            "name": f"{t.title()}: {v}",
            "pattern": pattern,
            "pattern_type": "stix",
            "valid_from": now_iso,
            "labels": ["malicious-activity", "email-threat", ind.get("provenance", "extracted")],
        })

    objects.append({
        "type": "report",
        "spec_version": "2.1",
        "id": report_id,
        "created": now_iso,
        "modified": now_iso,
        "name": case_title,
        "published": now_iso,
        "object_refs": indicator_refs,
        "labels": ["forensic-investigation", "drishtimail"],
    })

    return {
        "type": "bundle",
        "id": bundle_id,
        "objects": objects,
    }


def export_indicators_to_misp(
    indicators: list[dict[str, Any]],
    event_info: str = "DrishtiMail Threat Intelligence Export",
) -> dict[str, Any]:
    """Export indicators to MISP Event JSON format."""
    now_ts = int(datetime.now(timezone.utc).timestamp())
    attributes = []

    misp_type_map = {
        "domain": "domain",
        "ip": "ip-dst",
        "url": "url",
        "file_hash": "sha256",
        "sender_email": "email-src",
        "structural_hash": "comment",
    }

    for ind in indicators:
        t = ind.get("indicator_type", "domain")
        v = ind.get("value", "")
        attributes.append({
            "type": misp_type_map.get(t, "text"),
            "category": "Network activity" if t in {"domain", "ip", "url"} else "Payload delivery",
            "value": v,
            "to_ids": True,
            "comment": f"Extracted via {ind.get('provenance', 'forensic_pipeline')}",
        })

    return {
        "Event": {
            "info": event_info,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "threat_level_id": "2",
            "analysis": "2",
            "distribution": "0",
            "timestamp": str(now_ts),
            "Attribute": attributes,
        }
    }
