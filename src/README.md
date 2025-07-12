
```
src
├─ core
│  ├─ data
│  │  ├─ .env
│  │  ├─ index.faiss
│  │  ├─ meta.json
│  │  └─ state.json
│  ├─ file_watcher.py
│  ├─ kb_builder.py
│  ├─ kb_state.py
│  ├─ llm_interface.py
│  ├─ logs
│  │  ├─ moves.log
│  │  └─ watcher.log
│  ├─ models
│  │  ├─ distilgpt2
│  │  │  ├─ config.json
│  │  │  ├─ generation_config.json
│  │  │  ├─ merges.txt
│  │  │  ├─ model.safetensors
│  │  │  ├─ special_tokens_map.json
│  │  │  ├─ tokenizer.json
│  │  │  ├─ tokenizer_config.json
│  │  │  └─ vocab.json
│  │  ├─ mistral-7b-instruct-v0.1.Q4_K_M.gguf
│  │  ├─ phi-2-q4_k_m.gguf
│  │  └─ tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
│  ├─ query_engine.py
│  ├─ scheduler.py
│  ├─ sorter_pipeline.py
│  ├─ utils
│  │  ├─ chunker.py
│  │  ├─ config.py
│  │  ├─ embedder.py
│  │  ├─ extractor.py
│  │  ├─ file_ops.py
│  │  ├─ indexer.py
│  │  ├─ logger.py
│  │  ├─ path_utils.py
│  │  ├─ retriever.py
│  │  └─ __pycache__
│  │     ├─ chunker.cpython-313.pyc
│  │     ├─ config.cpython-313.pyc
│  │     ├─ embedder.cpython-313.pyc
│  │     ├─ extractor.cpython-313.pyc
│  │     ├─ file_ops.cpython-313.pyc
│  │     ├─ indexer.cpython-313.pyc
│  │     ├─ logger.cpython-313.pyc
│  │     ├─ path_utils.cpython-313.pyc
│  │     └─ retriever.cpython-313.pyc
│  └─ __pycache__
│     ├─ file_watcher.cpython-313.pyc
│     ├─ kb_builder.cpython-313.pyc
│     ├─ kb_state.cpython-313.pyc
│     ├─ llm_interface.cpython-313.pyc
│     ├─ query_engine.cpython-313.pyc
│     ├─ scheduler.cpython-313.pyc
│     └─ sorter_pipeline.cpython-313.pyc
├─ gui
│  ├─ components
│  │  ├─ AddPathRow.ui
│  │  ├─ AddPathRow_ui.py
│  │  ├─ ChatBubbleApp.ui
│  │  ├─ ChatBubbleApp_ui.py
│  │  ├─ ChatBubbleUser.ui
│  │  ├─ ChatBubbleUser_ui.py
│  │  ├─ FileCard.ui
│  │  ├─ FileCard_ui.py
│  │  ├─ LogRow.ui
│  │  ├─ LogRow_ui.py
│  │  ├─ PathRow.ui
│  │  └─ PathRow_ui.py
│  ├─ icons
│  ├─ scripts
│  │  ├─ config_window.py
│  │  ├─ log_window.py
│  │  ├─ main_window.py
│  │  ├─ themes.py
│  │  ├─ ui_configWindow.py
│  │  ├─ ui_logWindow.py
│  │  ├─ ui_mainWindow.py
│  │  ├─ utils.py
│  │  └─ __pycache__
│  │     ├─ config_window.cpython-313.pyc
│  │     ├─ log_window.cpython-313.pyc
│  │     ├─ main_window.cpython-313.pyc
│  │     ├─ themes.cpython-313.pyc
│  │     ├─ ui_configWindow.cpython-313.pyc
│  │     ├─ ui_logWindow.cpython-313.pyc
│  │     ├─ ui_mainWindow.cpython-313.pyc
│  │     └─ utils.cpython-313.pyc
│  ├─ stylesheets
│  │  ├─ base.qss
│  │  └─ themes
│  │     ├─ dark.qss
│  │     └─ light.qss
│  └─ windows
│     ├─ configWindow.ui
│     ├─ logWindow.ui
│     └─ mainWindow.ui
├─ logs
│  ├─ moves.log
│  └─ watcher.log
├─ main.py
├─ README.md
└─ test_llm_interface.py

```