# from pathlib import Path
# from typing import List


# from app.utility import ocr

# SUPPORTED_IMAGE_TYPES = {".png", ".jpg", ".jpeg"}
# SUPPORTED_DOC_TYPES = {".docx"}

# def extract_text(file_path: str, filename: str) -> List[dict]:
#     ext = Path(filename).suffix.lower()

#     if ext == ".pdf":
#         return ocr.extract_text_from_pdf(file_path, filename)

#     elif ext in SUPPORTED_IMAGE_TYPES:
#         return ocr.extract_text_from_image(file_path, filename)

#     elif ext in SUPPORTED_DOC_TYPES:
#         return ocr.extract_text_from_docx(file_path, filename) 

#     else:
#         raise ValueError(f"Unsupported file type: {ext}")
