# Project Structure Overview

This project is a lightweight, modular, local-first file assistant application that monitors, sorts, and answers queries about files using RAG (Retrieval-Augmented Generation) and LLMs (Local Language Models). It is optimized for low resource usage, efficient file handling, and seamless GUI integration (though GUI logic is kept separate).

## 📁 Project Directory Structure

```
project_root/
│
├── main.py
│   - Optional entry point or CLI launcher.
│
├── config/
│   ├── folders.json            # List of folder categories for classification.
│   └── settings.yaml           # Paths, model configs, LLM options, indexing rules.
│
├── core/                       # ✅ Centralized logic for shared tasks
│   ├── extractor.py            # Extract text from PDFs, DOCX, and TXT files.
│   ├── embedder.py             # Embeds text using sentence-transformers.
│   ├── retriever.py            # Wraps FAISS search functionality.
│   ├── file_ops.py             # Handles file/folder moves, renames, validation.
│   ├── logger.py               # Logs classification steps and user feedback.
│   ├── feedback.py             # Feedback schema and manager for review/correction.
│   └── pipeline_utils.py       # Reusable orchestration logic for sorting and indexing.
│
├── kb_builder.py               # Index all files from organized folders to build FAISS KB.
├── file_watcher.py             # Monitors incoming raw files and triggers sorting.
├── sorter_pipeline.py          # Extract → Classify → Move → Log pipeline using LLM.
├── query_engine.py             # RAG-based question answering over local files.
├── llm_interface.py            # Sends prompts to and receives responses from local LLM.
│
├── index/
│   ├── faiss_index.bin         # FAISS vector store for embedded files.
│   └── docs_metadata.json      # Maps vector entries to file paths and summaries.
│
├── feedback/
│   ├── sorting_feedback.jsonl  # One-line-per-file classification logs.
│   └── corrections/            # User-corrected file entries (for future tuning).
│
├── data/
│   ├── raw_files/              # Folder watched for incoming unorganized files.
│   └── organized/              # Final destination folders for sorted content.
│
└── models/
    └── local_llm/              # Local LLM binaries (GGUF for llama.cpp or Ollama models).
```

## 🧠 Features
- **RAG-based File Sorting**: Classifies files into categories using extracted content + LLM.
- **Semantic Query Answering**: Lets users query local files using natural language.
- **Feedback Mechanism**: Every sorting decision is logged for user review/correction.
- **Modular Architecture**: Core logic is decoupled from GUI, allowing CLI, service, or frontend integration.
- **Local-first Execution**: No cloud API calls; everything is optimized for offline use.