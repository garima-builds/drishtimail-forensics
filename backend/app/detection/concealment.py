"""M2: Concealment Technique & Adversarial Evasion Detector.

Identifies hidden adversarial payload techniques in email bodies: zero-width characters,
hidden CSS styling, font-size 0 text, color matching background, and tracking pixels.
"""
import re
from typing import Any
from bs4 import BeautifulSoup

ZERO_WIDTH_CHARS = [
    ('\u200b', 'Zero-Width Space'),
    ('\u200c', 'Zero-Width Non-Joiner'),
    ('\u200d', 'Zero-Width Joiner'),
    ('\ufeff', 'Zero-Width No-Break Space / BOM'),
    ('\u00ad', 'Soft Hyphen'),
    ('\u2060', 'Word Joiner'),
]

HIDDEN_CSS_PATTERNS = [
    re.compile(r"display\s*:\s*none", re.IGNORECASE),
    re.compile(r"visibility\s*:\s*hidden", re.IGNORECASE),
    re.compile(r"font-size\s*:\s*0(?:px|pt|em)?", re.IGNORECASE),
    re.compile(r"opacity\s*:\s*0", re.IGNORECASE),
    re.compile(r"height\s*:\s*0(?:px)?;\s*width\s*:\s*0(?:px)?", re.IGNORECASE),
    re.compile(r"color\s*:\s*(?:#fff(?:fff)?|white)\s*;\s*background(?:-color)?\s*:\s*(?:#fff(?:fff)?|white)", re.IGNORECASE),
]


def detect_concealment_techniques(
    plain_text: str = "",
    html_body: str = "",
) -> list[dict[str, Any]]:
    """Scan text and HTML bodies for evasion and concealment techniques."""
    findings: list[dict[str, Any]] = []

    full_body = f"{plain_text}\n{html_body}"

    # 1. Zero-width invisible characters
    zw_matches = []
    for char_code, char_name in ZERO_WIDTH_CHARS:
        count = full_body.count(char_code)
        if count > 0:
            zw_matches.append(f"{count}x {char_name}")

    if zw_matches:
        findings.append({
            "type": "zero_width_characters",
            "severity": "High",
            "title": "Adversarial Zero-Width Concealment",
            "details": zw_matches,
            "description": (
                f"Body contains invisible zero-width characters ({', '.join(zw_matches)}) "
                f"often used to bypass automated spam/phishing keyword filters."
            ),
        })

    # 2. Hidden CSS in HTML
    if html_body:
        matched_css = []
        for pat in HIDDEN_CSS_PATTERNS:
            if pat.search(html_body):
                matched_css.append(pat.pattern)

        if matched_css:
            findings.append({
                "type": "hidden_css_elements",
                "severity": "High",
                "title": "Hidden Text Styling (CSS Concealment)",
                "details": matched_css,
                "description": (
                    "HTML body contains hidden element styles (e.g. display:none, font-size:0, or white-on-white text) "
                    "hiding content from the human reader while feeding it to automated parsers."
                ),
            })

        # 3. Tracking pixels / 1x1 images
        try:
            soup = BeautifulSoup(html_body, "html.parser")
            tiny_images = 0
            for img in soup.find_all("img"):
                w = str(img.get("width", "")).strip()
                h = str(img.get("height", "")).strip()
                if (w in {"0", "1"} and h in {"0", "1"}) or "1x1" in str(img.get("src", "")).lower():
                    tiny_images += 1

            if tiny_images > 0:
                findings.append({
                    "type": "tracking_pixel",
                    "severity": "Low",
                    "title": "Embedded Tracking Pixel",
                    "count": tiny_images,
                    "description": f"Found {tiny_images} 1x1 transparent tracking image(s) for email read beaconing.",
                })
        except Exception:
            pass

    return findings
