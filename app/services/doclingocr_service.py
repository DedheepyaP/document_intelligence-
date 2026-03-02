from pathlib import Path
from typing import List
from docling.document_converter import DocumentConverter

SUPPORTED_TYPES = {".pdf", ".png", ".jpg", ".jpeg", ".docx"}
converter = DocumentConverter()

def extract_text(file_path: str, filename: str) -> List[dict]:
    ext = Path(filename).suffix.lower()

    if ext not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported file type for Docling OCR: {ext}")

    result = converter.convert(file_path)
    text = result.document.export_to_markdown()

    return [{
        "text": text,
        "docling_ast": result.document.export_to_dict(),
        "metadata": {
            "filename": filename,
            "source": "docling"
        }
    }]
