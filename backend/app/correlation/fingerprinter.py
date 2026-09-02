"""F6: Structural HTML Tag Skeleton Fingerprinter.

Extracts the invariant structural skeleton of HTML message bodies by stripping all text
and attribute values while preserving tag hierarchy and attribute keys.
Enables detection of reused phishing kits across disparate domains and wording variations.
"""
import hashlib
import re

try:
    from bs4 import BeautifulSoup, Comment
    _HAS_BS4 = True
except ImportError:
    _HAS_BS4 = False


def extract_structural_skeleton(html_content: str) -> tuple[str, str]:
    """Extract HTML tag skeleton and compute its SHA-256 structural fingerprint.

    Returns:
        (skeleton_hash, raw_skeleton_string)
    """
    if not html_content or not html_content.strip():
        empty_hash = hashlib.sha256(b"empty_structure").hexdigest()
        return empty_hash, "empty_structure"

    if _HAS_BS4:
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()

            tags_skeleton: list[str] = []
            for tag in soup.find_all(True):
                attr_keys = sorted(list(tag.attrs.keys())) if tag.attrs else []
                attr_str = f"[{','.join(attr_keys)}]" if attr_keys else ""
                tags_skeleton.append(f"<{tag.name}{attr_str}>")

            raw_skeleton = "".join(tags_skeleton) or "text_only_structure"
            skeleton_hash = hashlib.sha256(raw_skeleton.encode("utf-8")).hexdigest()
            return skeleton_hash, raw_skeleton
        except Exception:
            pass

    # Regex-based tag and attribute key extractor fallback
    clean_html = re.sub(r"<!--.*?-->", "", html_content, flags=re.DOTALL)
    tag_matches = re.findall(r"<\s*([a-zA-Z0-9]+)([^>]*)>", clean_html)
    tags_skeleton = []
    for tag_name, attr_block in tag_matches:
        attr_keys = sorted(re.findall(r'([a-zA-Z0-9_-]+)\s*=', attr_block))
        attr_str = f"[{','.join(attr_keys)}]" if attr_keys else ""
        tags_skeleton.append(f"<{tag_name.lower()}{attr_str}>")

    raw_skeleton = "".join(tags_skeleton) or "text_only_structure"
    skeleton_hash = hashlib.sha256(raw_skeleton.encode("utf-8")).hexdigest()
    return skeleton_hash, raw_skeleton

