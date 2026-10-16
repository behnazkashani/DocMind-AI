"""Extraction and quality reporting for machine-readable PDF text."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

import pymupdf

from . import SCHEMA_VERSION

_PERSIAN_LATIN_ADJACENCY = re.compile(r"[A-Za-z][\u0600-\u06ff]|[\u0600-\u06ff][A-Za-z]")
_SPACE_BEFORE_PUNCTUATION = re.compile(r"\s+[،؛.!?:؟]")
_MULTIPLE_SPACES = re.compile(r"[^\S\r\n]{2,}")
_KNOWN_FRAGMENT_HINTS = ("ت صور", "یم کن", "ز ریل", "در و")


def normalize_text(text: str) -> str:
    """Apply conservative NFC and whitespace normalization, preserving ZWNJ."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def inspect_text(text: str) -> list[dict[str, str]]:
    """Return heuristic review findings; none of these proves an error."""
    findings: list[dict[str, str]] = []
    if _MULTIPLE_SPACES.search(text):
        findings.append({"kind": "suspicious_whitespace", "severity": "heuristic", "message": "Repeated horizontal whitespace; review the source layout."})
    if _SPACE_BEFORE_PUNCTUATION.search(text):
        findings.append({"kind": "space_before_punctuation", "severity": "heuristic", "message": "Whitespace before punctuation; may be intentional in mixed-direction text."})
    if _PERSIAN_LATIN_ADJACENCY.search(text):
        findings.append({"kind": "mixed_script_adjacency", "severity": "heuristic", "message": "Persian and Latin characters are adjacent; mixed-script text is common and may be correct."})
    if any(fragment in text for fragment in _KNOWN_FRAGMENT_HINTS):
        findings.append({"kind": "possible_fragmented_word", "severity": "human_review", "message": "A previously observed text fragment occurs; inspect the PDF before changing it."})
    return findings


def _page_warning(page: pymupdf.Page, page_number: int, block_count: int, text_chars: int) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    image_count = len(page.get_images())
    if block_count == 0:
        warnings.append({
            "kind": "no_extractable_text",
            "severity": "human_review",
            "page": page_number,
            "message": "The text extraction method returned no blocks. This page may be blank, image-based, or contain vectorized text.",
            "image_count": image_count,
            "ocr_inspection_recommended": image_count > 0,
        })
    elif text_chars < 20:
        warnings.append({
            "kind": "very_little_text",
            "severity": "heuristic",
            "page": page_number,
            "message": "Fewer than 20 normalized characters were extracted; review this page if substantial text is expected.",
            "character_count": text_chars,
        })
    if block_count > 1:
        warnings.append({
            "kind": "reading_order_unverified",
            "severity": "heuristic",
            "page": page_number,
            "message": "Multiple blocks were extracted in PyMuPDF source order; verify their visual reading order, especially for RTL or multi-column layouts.",
        })
    return warnings


def extract_document(input_pdf: str | Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Extract text blocks and return a versioned document and QC report."""
    source = Path(input_pdf)
    if not source.is_file():
        raise FileNotFoundError(f"Input PDF does not exist or is not a file: {source}")

    pages: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    total_blocks = 0
    total_chars = 0
    empty_text_blocks = 0

    try:
        with pymupdf.open(source) as pdf:
            metadata = {str(key): value for key, value in (pdf.metadata or {}).items() if value is not None}
            total_pages = len(pdf)
            for page_number, page in enumerate(pdf, start=1):
                raw_blocks = page.get_text("blocks", sort=False)
                blocks: list[dict[str, Any]] = []
                page_chars = 0
                for block_number, block in enumerate(raw_blocks, start=1):
                    x0, y0, x1, y1, raw_text = block[:5]
                    normalized = normalize_text(raw_text)
                    page_chars += len(normalized)
                    total_chars += len(normalized)
                    if not normalized:
                        empty_text_blocks += 1
                    text_findings = inspect_text(raw_text)
                    blocks.append({
                        "block_id": block_number,
                        "bbox": {"x0": round(x0, 2), "y0": round(y0, 2), "x1": round(x1, 2), "y1": round(y1, 2)},
                        "block_type": block[6] if len(block) > 6 else None,
                        "raw_text": raw_text,
                        "normalized_text": normalized,
                        "reading_order": block_number,
                        "reading_order_status": "pymupdf_source_order_unverified",
                        "warnings": text_findings,
                    })
                    for finding in text_findings:
                        findings.append({"page": page_number, "block_id": block_number, **finding})

                total_blocks += len(blocks)
                page_entry = {
                    "page_number": page_number,
                    "width": round(page.rect.width, 2),
                    "height": round(page.rect.height, 2),
                    "rotation": page.rotation,
                    "extraction_method": "pymupdf_page_get_text_blocks_sort_false",
                    "block_count": len(blocks),
                    "image_count": len(page.get_images()),
                    "text_character_count": page_chars,
                    "warnings": _page_warning(page, page_number, len(blocks), page_chars),
                    "blocks": blocks,
                }
                pages.append(page_entry)
                findings.extend(page_entry["warnings"])

    except (pymupdf.FileDataError, RuntimeError) as exc:
        raise ValueError(f"Could not read PDF '{source}': {exc}") from exc

    document_output = {
        "schema_version": SCHEMA_VERSION,
        "source_file": source.name,
        "metadata": metadata,
        "total_pages": total_pages,
        "total_blocks": total_blocks,
        "total_normalized_characters": total_chars,
        "extraction_method": "PyMuPDF page.get_text('blocks', sort=False)",
        "reading_order_policy": "Preserve PyMuPDF block source order; RTL and complex layouts are not automatically reconstructed.",
        "pages": pages,
    }
    report = {
        "schema_version": SCHEMA_VERSION,
        "source_file": source.name,
        "total_pages": total_pages,
        "total_blocks": total_blocks,
        "total_normalized_characters": total_chars,
        "pages_without_extractable_text": [p["page_number"] for p in pages if p["block_count"] == 0],
        "pages_with_very_little_text": [p["page_number"] for p in pages if p["block_count"] and p["text_character_count"] < 20],
        "empty_text_blocks": empty_text_blocks,
        "heuristic_or_review_findings": findings,
        "confirmed_failures": [],
        "errors": [],
        "ocr_policy": "OCR is not performed. Pages without extractable text are reported; image-bearing pages are marked for OCR inspection.",
        "finding_counts_by_severity": {
            level: sum(1 for item in findings if item["severity"] == level)
            for level in ("heuristic", "human_review")
        },
    }
    return document_output, report


def write_json(path: Path, data: dict[str, Any], overwrite: bool = False) -> None:
    """Write UTF-8 JSON; refuse to replace an existing file by default."""
    if path.exists() and not overwrite:
        raise FileExistsError(f"Output already exists: {path} (pass --overwrite to replace it)")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()
