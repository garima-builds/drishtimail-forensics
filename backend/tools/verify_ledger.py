"""Offline verifier for a JSON export from the DrishtiMail evidence ledger."""
import argparse
import hashlib
import json
import sys


def digest_entry(entry: dict) -> str:
    material = f"{entry.get('previous_hash') or ''}:{entry['event_type']}:{entry['subject_id']}:{entry['evidence_reference_id']}:{entry['payload_hash']}"
    return hashlib.sha256(material.encode()).hexdigest()


def verify(entries: list[dict]) -> tuple[bool, str]:
    prior = None
    for entry in sorted(entries, key=lambda item: item["sequence"]):
        if entry.get("previous_hash") != prior:
            return False, f"sequence {entry['sequence']}: previous hash does not match"
        if digest_entry(entry) != entry.get("entry_hash"):
            return False, f"sequence {entry['sequence']}: entry hash does not match"
        prior = entry["entry_hash"]
    return True, f"PASS: verified {len(entries)} ledger entries"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a DrishtiMail ledger export offline")
    parser.add_argument("ledger_export", help="JSON file containing an array of ledger entries")
    args = parser.parse_args()
    with open(args.ledger_export, encoding="utf-8") as source:
        payload = json.load(source)
    entries = payload.get("entries", payload) if isinstance(payload, dict) else payload
    if not isinstance(entries, list):
        print("FAIL: expected a JSON list or an object with an entries list", file=sys.stderr)
        return 2
    ok, message = verify(entries)
    print(message)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
