from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .pipeline import extract_document, write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract PDF text and write a quality report.")
    parser.add_argument("input_pdf", type=Path, help="Path to the source PDF")
    parser.add_argument("--output-dir", type=Path, default=Path("output"), help="Directory for JSON outputs (default: ./output)")
    parser.add_argument("--overwrite", action="store_true", help="Replace output files if they already exist")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_doc = args.output_dir / f"{args.input_pdf.stem}.extracted.json"
    output_report = args.output_dir / f"{args.input_pdf.stem}.quality.json"
    try:
        document, report = extract_document(args.input_pdf)
        # Check both destinations before writing either one.
        if not args.overwrite:
            existing = [str(path) for path in (output_doc, output_report) if path.exists()]
            if existing:
                raise FileExistsError("Output already exists: " + ", ".join(existing) + " (pass --overwrite to replace)")
        write_json(output_doc, document, overwrite=args.overwrite)
        write_json(output_report, report, overwrite=args.overwrite)
    except (FileNotFoundError, FileExistsError, ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(f"Processed {document['total_pages']} pages and {document['total_blocks']} text blocks.")
    print(f"Pages without extractable text: {report['pages_without_extractable_text']}")
    print(f"Document: {output_doc.resolve()}")
    print(f"Quality report: {output_report.resolve()}")
    return 0
