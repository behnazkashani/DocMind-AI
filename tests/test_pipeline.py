import json

import pymupdf
import pytest

from pdf_extraction.pipeline import extract_document, inspect_text, normalize_text, write_json


def make_pdf(path, texts):
    doc = pymupdf.open()
    for text in texts:
        page = doc.new_page(width=960, height=540)
        if text is not None:
            page.insert_text((60, 80), text)
    doc.save(path)
    doc.close()


def test_whitespace_and_unicode_normalization():
    assert normalize_text("  سلام\n\tدنیا  ") == "سلام دنیا"
    assert normalize_text("می\u200cروم") == "می\u200cروم"
    assert normalize_text("e\u0301") == "é"


def test_empty_text_and_findings():
    assert normalize_text("") == ""
    assert inspect_text("ت صور")
    assert any(item["kind"] == "mixed_script_adjacency" for item in inspect_text("سلامAI"))
    assert inspect_text("متن  فاصله")


def test_extract_metadata_raw_text_and_empty_page(tmp_path):
    source = tmp_path / "sample.pdf"
    make_pdf(source, ["Hello  AI", None])
    document, report = extract_document(source)
    assert document["schema_version"] == "1.0"
    assert document["total_pages"] == 2
    assert document["pages"][0]["width"] == 960
    assert document["pages"][0]["blocks"][0]["block_id"] == 1
    block = document["pages"][0]["blocks"][0]
    assert block["raw_text"] == "Hello  AI\n"
    assert block["normalized_text"] == "Hello AI"
    assert "corrected_text" not in block
    assert report["pages_without_extractable_text"] == [2]
    assert report["confirmed_failures"] == []


def test_json_utf8_and_repeatability(tmp_path):
    source = tmp_path / "repeat.pdf"
    make_pdf(source, ["Persian text"])
    first, _ = extract_document(source)
    second, _ = extract_document(source)
    assert first == second
    output = tmp_path / "out.json"
    first["test_persian"] = "فارسی"
    write_json(output, first)
    encoded = output.read_text(encoding="utf-8")
    assert "فارسی" in encoded
    assert json.loads(encoded) == first
    with pytest.raises(FileExistsError):
        write_json(output, first)


def test_missing_input():
    with pytest.raises(FileNotFoundError):
        extract_document("missing.pdf")


def test_supplied_pdf_integration_when_configured():
    import os

    source = os.environ.get("PDF_EXTRACTION_TEST_PDF")
    if not source:
        pytest.skip("Set PDF_EXTRACTION_TEST_PDF to run the local supplied-PDF integration test")
    document, report = extract_document(source)
    assert document["total_pages"] > 0
    assert document["total_blocks"] == sum(page["block_count"] for page in document["pages"])
    assert all("raw_text" in block for page in document["pages"] for block in page["blocks"])
    assert all(page["page_number"] > 0 for page in document["pages"])
    extracted_text = "".join(block["raw_text"] for page in document["pages"] for block in page["blocks"])
    assert any("\u0600" <= char <= "\u06ff" for char in extracted_text)
