import os
import pypdf
import docx

def extract_text(file_path):
    """
    Robustly extracts text from .txt, .pdf, and .docx files.
    Returns trimmed string. Returns None on ANY failure to protect system stability.
    """
    ext = os.path.splitext(file_path)[1].lower()
    text = None
    
    try:
        if ext == '.txt':
            # Try utf-8 first, then fallback to latin-1
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as f:
                    text = f.read()
        
        elif ext == '.pdf':
            with open(file_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                pages = []
                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        pages.append(content)
                text = "\n".join(pages)
            
        elif ext == '.docx':
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            
        else:
            return None # Unsupported extension

    except Exception as e:
        # Catch-all to prevent crashes
        print(f"[Warning] Failed to read {file_path}: {e}")
        return None

    if text and len(text.strip()) > 0:
        return text.strip()
    return None
