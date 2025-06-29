from pathlib import Path
from typing import List, Tuple, Literal, Dict

from jinja2 import Template
from llama_cpp import Llama

MODEL_PATH = "models/llm.gguf"
MAX_TOKENS = 512
TEMPERATURE = 0.1

llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=4)

classification_template = Template("""
You are a smart document assistant.

Given the following document content:
---
{{ content }}
---

And the list of possible folders:
{{ folders }}

Classify the document into the most appropriate folder from the list.

Respond with the exact folder name only.
""".strip())

qa_template = Template("""
You are a helpful assistant answering a user query using provided documents.

Query:
{{ query }}

Documents:
{% for file, text in docs %}
File: {{ file }}
Content: {{ text[:1000] }}...
{% endfor %}

Answer the question using the above content. Keep it concise and relevant.
""".strip())

def run_llm(prompt: str) -> str:
    output = llm(
        prompt,
        max_tokens=MAX_TOKENS,
        stop=["</s>", "\n\n"],
        temperature=TEMPERATURE
    )
    result = output["choices"][0]["text"]
    return result.strip()

def classify_document(content: str, folder_labels: List[str], retrieved_docs: List[Tuple[str, str]]) -> Tuple[str, List[str]]:
    """
    Classify a document into one of the provided folder labels using LLM and context.
    """
    # You can optionally augment content using retrieved_docs if needed
    prompt = classification_template.render(
        content=content.strip()[:3000],
        folders=", ".join(folder_labels)
    )
    predicted_folder = run_llm(prompt)
    referenced_files = [path for path, _ in retrieved_docs]
    return predicted_folder, referenced_files

def answer_query(query: str, retrieved_docs: List[Tuple[str, str]]) -> Tuple[str, List[str]]:
    
    prompt = qa_template.render(
        query=query,
        docs=retrieved_docs
    )
    answer = run_llm(prompt)
    referenced_files = [path for path, _ in retrieved_docs]
    return answer, referenced_files

def answer_query_on_selected_files(query: str, file_texts: Dict[str, str]) -> Tuple[str, List[str]]:
    
    doc_list = list(file_texts.items())
    prompt = qa_template.render(query=query, docs=doc_list)
    answer = run_llm(prompt)
    return answer, list(file_texts.keys())