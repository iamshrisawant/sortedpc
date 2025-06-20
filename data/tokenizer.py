from PyPDF2 import PdfReader
from docx import Document
from pptx import Presentation

def extract_text(file_path):
    ext = file_path.lower().split('.')[-1]
    try:
        if ext == "txt":
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        elif ext == "pdf":
            reader = PdfReader(file_path)
            return "\n".join([page.extract_text() or "" for page in reader.pages])
        elif ext == "docx":
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        elif ext == "pptx":
            prs = Presentation(file_path)
            texts = []
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        texts.append(shape.text)
            return "\n".join(texts)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return ""

def tokenize(text):
    return text.lower().split()
