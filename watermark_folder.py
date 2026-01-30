#!/usr/bin/env python3
"""
Add a semi-transparent text watermark to every page of every PDF
in the source folder and its subfolders. Non-PDF files (e.g. JPG, PNG)
are copied to the output folder unchanged.
Output is written to the configured output folder (originals unchanged).
"""

import shutil
import tempfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# --- Config ---
SOURCE_FOLDER = Path(__file__).resolve().parent / "docs"
OUTPUT_FOLDER = Path(__file__).resolve().parent / "docs - watermarked"
WATERMARK_TEXT = "Uniquement projet immo T1 2026"  # change if you prefer e.g. "COPY" or "DRAFT"


def create_watermark_pdf(output_path: Path) -> None:
    """Create a one-page PDF with diagonal semi-transparent watermark text."""
    w, h = A4
    c = canvas.Canvas(str(output_path), pagesize=A4)
    c.setFillAlpha(0.25)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.setFont("Helvetica-Bold", 32)
    c.saveState()
    c.translate(w / 2, h / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, WATERMARK_TEXT)
    c.restoreState()
    c.save()


def scale_stamp_to_page(stamp_page, content_page):
    """Return a Transformation that scales the stamp to fit the content page."""
    sw = float(stamp_page.mediabox.width)
    sh = float(stamp_page.mediabox.height)
    cw = float(content_page.mediabox.width)
    ch = float(content_page.mediabox.height)
    if sw <= 0 or sh <= 0:
        return Transformation()
    sx, sy = cw / sw, ch / sh
    return Transformation().scale(sx, sy)


def watermark_pdf(input_path: Path, output_path: Path, stamp_page) -> None:
    """Overlay the stamp on every page of the PDF and write to output_path."""
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        page.merge_transformed_page(
            stamp_page,
            scale_stamp_to_page(stamp_page, page),
            over=True,
        )
        writer.add_page(page)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)


def main() -> None:
    if not SOURCE_FOLDER.is_dir():
        raise SystemExit(f"Source folder not found: {SOURCE_FOLDER}")

    all_files = [p for p in SOURCE_FOLDER.rglob("*") if p.is_file()]
    pdf_files = [p for p in all_files if p.suffix.lower() == ".pdf"]
    other_files = [p for p in all_files if p not in pdf_files]

    if not all_files:
        print("No files found in", SOURCE_FOLDER)
        return

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        create_watermark_pdf(tmp_path)
        stamp_page = PdfReader(tmp_path).pages[0]

        for pdf_path in pdf_files:
            rel = pdf_path.relative_to(SOURCE_FOLDER)
            out_path = OUTPUT_FOLDER / rel
            print("Watermarking:", rel)
            watermark_pdf(pdf_path, out_path, stamp_page)

        for other_path in other_files:
            rel = other_path.relative_to(SOURCE_FOLDER)
            out_path = OUTPUT_FOLDER / rel
            out_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(other_path, out_path)
            print("Copied:", rel)

        print(f"\nDone. {len(pdf_files)} PDF(s) watermarked, {len(other_files)} file(s) copied to:\n  {OUTPUT_FOLDER}")
    finally:
        tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
