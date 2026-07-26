# import os
# import PyPDF2
# from docx import Document

# def extract_text_from_file(file_path: str) -> str:
#     """Extracts raw text from a PDF or TXT file."""
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"File not found: {file_path}")
        
#     ext = os.path.splitext(file_path)[1].lower()
    
#     if ext == '.txt':
#         with open(file_path, 'r', encoding='utf-8') as f:
#             return f.read()
            
#     elif ext == '.pdf':
#         text = ""
#         with open(file_path, 'rb') as f:
#             reader = PyPDF2.PdfReader(f)
#             for page in reader.pages:
#                 page_text = page.extract_text()
#                 if page_text:
#                     text += page_text + "\n"
#         return text
#     else:
#         raise ValueError(f"Unsupported file format: {ext}")
import os
import PyPDF2
from docx import Document


def extract_text_from_file(file_path: str) -> str:
    """Extracts raw text from a PDF, DOCX or TXT file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    elif ext == '.pdf':
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    elif ext == '.docx':
        doc = Document(file_path)
        text = ""

        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text + "\n"

        return text

    else:
        raise ValueError(f"Unsupported file format: {ext}")
    
