# SortedPC: Local-First File Assistant

SortedPC is a modular Python application for local file organization, semantic search, and query answering using Retrieval-Augmented Generation (RAG) and Local Language Models (LLMs). The system is designed for privacy, offline operation, and extensibility. Below is a technical overview of the project, detailing each file and its core functions/methods.

---

## 📁 Project Structure & File Functions

```
sortedpc/
│
├── main.py
│   - `main()`: CLI entry point; orchestrates core workflows.
│
├── config/
│   ├── folders.json
│       - Defines file categories and folder mappings.
│   └── settings.yaml
│       - Stores global paths, model configurations, and operational rules.
│
├── core/
│   ├── extractor.py
│       - `extract_text(file_path)`: Extracts text from PDF, DOCX, TXT files.
│       - `get_file_type(file_path)`: Determines file type for extraction.
│   ├── embedder.py
│       - `embed_text(text)`: Converts text to vector embeddings for semantic search.
│       - `load_embedding_model(config)`: Loads embedding model as per settings.
│   ├── retriever.py
│       - `search(query, top_k)`: Performs FAISS-based vector search.
│       - `load_index(index_path)`: Loads FAISS index from disk.
│   ├── file_ops.py
│       - `move_file(src, dest)`: Moves files between folders.
│       - `validate_file(file_path)`: Checks file integrity and type.
│   ├── logger.py
│       - `log_sorting_action(action_data)`: Logs sorting/classification steps.
│       - `log_error(error_data)`: Logs errors during processing.
│   ├── feedback.py
│       - `record_feedback(feedback_data)`: Stores user feedback on sorting/classification.
│       - `get_feedback_history()`: Retrieves feedback logs.
│   └── pipeline_utils.py
│       - `run_sorting_pipeline(file_path)`: Orchestrates extraction, classification, moving, and logging.
│       - `run_indexing_pipeline()`: Indexes organized files for semantic search.
│
├── kb_builder.py
│   - `build_faiss_index()`: Builds FAISS knowledge base from organized files.
│   - `update_metadata()`: Updates docs_metadata.json with file summaries.
│
├── file_watcher.py
│   - `watch_raw_files()`: Monitors raw_files directory for new files.
│   - `trigger_sorting(file_path)`: Initiates sorting pipeline on new files.
│
├── sorter_pipeline.py
│   - `sort_file(file_path)`: End-to-end pipeline: extract → classify (LLM) → move → log.
│   - `classify_file(text)`: Uses LLM to determine file category.
│
├── query_engine.py
│   - `answer_query(query)`: Answers user queries using RAG over local files.
│   - `retrieve_relevant_docs(query)`: Retrieves documents relevant to the query.
│
├── llm_interface.py
│   - `prompt_llm(prompt)`: Sends prompt to local LLM and returns response.
│   - `load_llm_model(model_path)`: Loads local LLM for inference.
│
├── index/
│   ├── faiss_index.bin
│       - FAISS vector store for semantic search.
│   └── docs_metadata.json
│       - Maps vectors to files and stores file summaries.
│
├── feedback/
│   ├── sorting_feedback.jsonl
│       - Logs of sorting/classification actions.
│   └── corrections/
│       - Stores user corrections for retraining.
│
├── data/
│   ├── raw_files/
│       - Incoming unsorted files.
│   └── organized/
│       - Sorted files by category.
│
└── models/
    └── local_llm/
        - Local LLM binaries (GGUF/Ollama) for offline inference.
```

---

## 🧩 Module Details

- **main.py**: CLI launcher; calls core pipeline functions.
- **config/**: Contains folder category definitions and global settings.
- **core/**: Implements extraction, embedding, retrieval, file operations, logging, feedback, and pipeline orchestration.
- **kb_builder.py**: Builds and updates FAISS index and metadata for semantic search.
- **file_watcher.py**: Watches for new files and triggers sorting pipeline.
- **sorter_pipeline.py**: Runs extraction, classification (LLM), moving, and logging for each file.
- **query_engine.py**: Handles semantic queries using RAG and local vector search.
- **llm_interface.py**: Manages local LLM loading and prompt/response handling.
- **index/**: Stores FAISS index and document metadata.
- **feedback/**: Logs sorting actions and user corrections.
- **data/**: Stores raw and organized files.
- **models/**: Contains local LLM binaries for offline inference.

---

## 🚀 Features

- **Automated File Sorting**: Extracts content, classifies using LLM, and organizes files.
- **Semantic Search & Querying**: Natural language queries over local documents using FAISS and RAG.
- **Feedback Logging**: Logs every sorting/classification for review and correction.
- **Modular & Extensible**: Decoupled logic; supports CLI, service, or frontend integration.
- **Local-First & Private**: No cloud APIs; optimized for offline, private use.

---