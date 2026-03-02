# from typing import List
# from docling.document_converter import DocumentConverter

# converter = DocumentConverter()

# def extract_with_docling(file_path: str, filename: str) -> List[dict]:
    
#     result = converter.convert(file_path)
#     text = result.document.export_to_markdown()
    
#     return [{
#         "text": text,
#         "metadata": {
#             "filename": filename,
#             "source": "docling"
#         }
#     }]
