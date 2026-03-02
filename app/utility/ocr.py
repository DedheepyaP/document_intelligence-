# from PIL import Image
# import pytesseract
# import pdfplumber
# from pdf2image import convert_from_path
# from typing import List
# from docx import Document
# import io

# def extract_text_from_image(file_path: str, filename: str) -> List[dict]:
#     # Image.open can open from a file path
#     image = Image.open(file_path)
#     text = pytesseract.image_to_string(image)

#     return [{
#         "text": text,
#         "metadata": {
#             "filename": filename,
#             "page": 1,
#             "source": "ocr"
#         }
#     }]


# def extract_text_from_pdf(file_path: str, filename: str):
#     extracted_docs = []

#     # pdfplumber can open from a file path
#     with pdfplumber.open(file_path) as pdf:
#         text_pages = [page.extract_text() for page in pdf.pages]

#     if any(text_pages):
#         for i, text in enumerate(text_pages):
#             if text and text.strip():
#                 extracted_docs.append({
#                     "text": text,
#                     "metadata": {
#                         "filename": filename,
#                         "page": i + 1,
#                         "source": "pdf"
#                     }
#                 })
#         return extracted_docs

#     # convert_from_path is more memory efficient than convert_from_bytes for large files
#     # It communicates with poppler via subprocess and doesn't load the whole PDF into RAM
#     images = convert_from_path(file_path, dpi=300)

#     for i, image in enumerate(images):
#         text = pytesseract.image_to_string(image)
#         extracted_docs.append({
#             "text": text,
#             "metadata": {
#                 "filename": filename,
#                 "page": i + 1,
#                 "source": "ocr"
#             }
#         })

#     return extracted_docs

# def extract_text_from_docx(file_path: str, filename: str) -> List[dict]:
#     doc = Document(file_path)
#     extracted_docs = []
    
#     content = []
#     for para in doc.paragraphs:
#         if para.text.strip():
#             content.append(para.text.strip())
            
#     full_text = "\n".join(content)

#     extracted_docs.append({
#         "text": full_text,
#         "metadata": {
#             "filename": filename,
#             "source": "docx"
#         }
#     })

#     return extracted_docs
