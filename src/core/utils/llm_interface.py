from typing import List, Tuple, Dict, Union
import os
import re
import google.generativeai as genai

# ────────────────────────────────────────────────────────────────────────────────
# Gemini Initialization
# ────────────────────────────────────────────────────────────────────────────────

GEMINI_MODEL_ID = "gemini-2.0-flash-001"
GEMINI_MAX_DOCS = 5  # Avoid token overload

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel(GEMINI_MODEL_ID)


# ────────────────────────────────────────────────────────────────────────────────
# Prompt Builders
# ────────────────────────────────────────────────────────────────────────────────

def render_qa_prompt(query: str, docs: List[Tuple[str, str]]) -> str:
    """
    Build prompt for RAG-style QA.
    Includes top N docs as context, capped by GEMINI_MAX_DOCS.
    """
    context_blocks = []
    for name, text in docs[:GEMINI_MAX_DOCS]:
        safe_text = sanitize(text[:2000])
        context_blocks.append(f"### Document: {name}\n{safe_text}")

    context = "\n\n".join(context_blocks)

    return f"""You are a helpful assistant. Use the following documents to answer the question.

Question:
{query}

Context:
{context}

Answer:"""


def render_classification_prompt(document_text: str, folder_labels: List[str]) -> str:
    safe_text = sanitize(document_text[:2000])
    label_list = ", ".join(folder_labels)

    return f"""You are a document assistant. Your job is to classify the document into the most suitable folder.

Document:
{safe_text}

Possible Folders:
{label_list}

Answer with the most appropriate folder name from above.
"""


# ────────────────────────────────────────────────────────────────────────────────
# LLM Interface Methods
# ────────────────────────────────────────────────────────────────────────────────

def answer_query(query: str, related_docs: List[Tuple[str, str]]) -> Tuple[str, List[str]]:
    prompt = render_qa_prompt(query, related_docs)
    try:
        response = gemini_model.generate_content(prompt)
        text = (response.text or "").strip()
        return (text if text else "No response generated."), [doc[0] for doc in related_docs]
    except Exception as e:
        return f"[LLM Error] {e}", []


def answer_query_on_selected_files(query: str, file_texts: Union[Dict[str, str], List[Dict[str, str]]]) -> Tuple[str, List[str]]:
    if isinstance(file_texts, dict):
        docs = list(file_texts.items())
    else:
        docs = [(d["name"], d["text"]) for d in file_texts if "name" in d and "text" in d]

    prompt = render_qa_prompt(query, docs)
    try:
        response = gemini_model.generate_content(prompt)
        text = (response.text or "").strip()
        return (text if text else "No response generated."), [doc[0] for doc in docs]
    except Exception as e:
        return f"[LLM Error] {e}", []


def classify_document(document_text: str, folder_labels: List[str], related_docs: List[Tuple[str, str]]) -> Tuple[str, List[str]]:
    prompt = render_classification_prompt(document_text, folder_labels)
    try:
        response = gemini_model.generate_content(prompt)
        output = (response.text or "").strip()

        # Try strict match
        for label in folder_labels:
            if label.lower() in output.lower():
                return label, [doc[0] for doc in related_docs]

    except Exception as e:
        return f"[LLM Error] {e}", []

    return "Unsorted", [doc[0] for doc in related_docs]


# ────────────────────────────────────────────────────────────────────────────────
# Helper
# ────────────────────────────────────────────────────────────────────────────────

def sanitize(text: str) -> str:
    """Cleans text for prompt input (avoid Gemini rejection or prompt injection)."""
    return re.sub(r"[^\x00-\x7F]+", " ", text).strip()
