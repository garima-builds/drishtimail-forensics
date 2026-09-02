"""F6: Structural HTML Tag Skeleton Fingerprinter.

Extracts the invariant structural skeleton of HTML message bodies by stripping all text
and attribute values while preserving tag hierarchy and attribute keys.
Enables detection of reused phishing kits across disparate domains and wording variations.
"""
import hashlib
import re
from bs4 import BeautifulSoup, Comment


def extract_structural_skeleton(html_content: str) -> tuple[str, str]:
    """Extract HTML tag skeleton and compute its SHA-256 structural fingerprint.

    Returns:
        (skeleton_hash, raw_skeleton_string)
    """
    if not html_content or not html_content.strip():
        # Return fallback empty skeleton
        empty_hash = hashlib.sha256(b"empty_structure").hexdigest()
        return empty_hash, "empty_structure"

    try:
        soup = BeautifulSoup(html_content, "html.parser")
        # Remove comments
        for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
            comment.extract()

        tags_skeleton: list[str] = []

        for tag in soup.find_all(True):
            attr_keys = sorted(list(tag.attrs.keys())) if tag.attrs else []
            attr_str = f"[{','.join(attr_keys)}]" if attr_keys else ""
            tags_skeleton.append(f"<{tag.name}{attr_str}>")

        raw_skeleton = "".join(tags_skeleton)
        if not raw_skeleton:
            raw_skeleton = "text_only_structure"

        skeleton_hash = hashlib.sha256(raw_skeleton.encode("utf-8")).hexdigest()
        return skeleton_hash, raw_skeleton
    except Exception:
        fallback_hash = hashlib.sha256(html_content.encode("utf-8", errors="replace")).hexdigest()
        return fallback_hash, "fallback_raw_structure"
