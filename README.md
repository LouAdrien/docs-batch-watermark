# PDF Batch Watermark

Add a semi-transparent diagonal text watermark to every page of every PDF in a folder (including subfolders). Originals are left unchanged; output is written to a separate folder.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

1. Edit the config at the top of `watermark_folder.py`:
   - **SOURCE_FOLDER** – folder containing your PDFs
   - **OUTPUT_FOLDER** – where watermarked PDFs will be saved (same structure as source)
   - **WATERMARK_TEXT** – the text to stamp (e.g. `"CONFIDENTIEL"` or a full sentence)

2. Run:

```bash
python watermark_folder.py
```

Watermarked files appear in `OUTPUT_FOLDER` with the same relative paths as in the source.

## Requirements

- Python 3.8+
- pypdf
- reportlab

## License

Use as you like.
