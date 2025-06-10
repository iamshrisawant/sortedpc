# 📂 Project Structure: Human-Like File Organizer

This system mimics human-style file organization using metadata, folder context, content classification, and learning-based refinement. It is modular, efficient, and built for local use.

---

## 🧱 Layered Architecture Overview

Each layer contains pipelines, which are composed of independent modules. Arrows (→) show data flow and integration.

ROOT/
├── core/
│   ├── file_io.py             # Scans files, extracts base metadata
│   ├── db.py                  # SQLite database operations
│   └── config.py              # Config loader with feature toggles
│
├── preprocess/
│   ├── folder_parser.py       # Tokenizes folder names, infers categories
│   └── path_classifier.py     # Path+filename based classification heuristics
│
├── classify/
│   ├── pattern_matcher.py     # Regex & keyword classification
│   ├── content_analyzer.py    # (Optional) NLP classifier using file content
│   └── decision_engine.py     # Combines evidence to finalize classification
│
├── organize/
│   ├── folder_templates.py    # Generates human-style folder paths
│   └── organizer.py           # Suggests or moves files to destinations
│
├── learn/
│   ├── feedback_collector.py  # Records user feedback on misclassifications
│   ├── relearn.py             # Trains rules/ML from feedback logs
│   └── confidence_monitor.py  # Detects low-confidence rules
│
├── ui/
│   ├── menu.py                # CLI menu system for interacting with the user
│   └── report.py              # Shows summaries, stats, unresolved cases
│
├── main.py                    # Entry point: initializes, loads config, launches menu
├── config.json                # Settings: toggles for processing depth, content analysis, etc.
└── README.md                  # This file


---

## 🔁 Functional Layer Stack (Data Flow Overview)


          ┌────────────────────────────────────┐
          │        LAYER 1: CORE INFRA         │
          │ ────────────────────────────────── │
          │ file_io.py → db.py ←→ config.py    │
          └────────────┬───────────────────────┘
                       ↓
          ┌────────────────────────────────────┐
          │   LAYER 2: CONTEXT ENRICHMENT      │
          │ ────────────────────────────────── │
          │ folder_parser.py + path_classifier │
          └────────────┬───────────────────────┘
                       ↓
          ┌────────────────────────────────────┐
          │    LAYER 3: CLASSIFICATION         │
          │ ────────────────────────────────── │
          │ pattern_matcher.py                 │
          │ content_analyzer.py (if enabled)   │
          │ decision_engine.py (final labels)  │
          └────────────┬───────────────────────┘
                       ↓
          ┌────────────────────────────────────┐
          │     LAYER 4: ORGANIZATION          │
          │ ────────────────────────────────── │
          │ folder_templates.py → organizer.py │
          └────────────┬───────────────────────┘
                       ↓
          ┌────────────────────────────────────┐
          │    LAYER 5: LEARNING LOOP          │
          │ ────────────────────────────────── │
          │ feedback_collector.py              │
          │ relearn.py ←→ confidence_monitor   │
          └────────────┬───────────────────────┘
                       ↓
          ┌────────────────────────────────────┐
          │        LAYER 6: USER INTERFACE     │
          │ ────────────────────────────────── │
          │ menu.py ←→ report.py               │
          └────────────────────────────────────┘
`

---

## 🚀 Development & Execution Flow


Step 1: Startup
  → main.py initializes config and DB
  → Launches menu system

Step 2: Path Added
  → file_io.py scans path
  → Metadata saved via db.py

Step 3: Preprocessing
  → folder_parser.py analyzes parent folders
  → path_classifier.py classifies from path + filename

Step 4: Classification
  → pattern_matcher.py runs heuristic classification
  → (Optional) content_analyzer.py loads small text files
  → decision_engine.py finalizes category, subject, etc.

Step 5: Organization
  → folder_templates.py proposes structured path
  → organizer.py moves files (or suggests)

Step 6: Feedback & Learning
  → feedback_collector.py logs user fixes
  → relearn.py updates classifiers/rules
  → confidence_monitor.py disables weak rules

Step 7: Repeat
  → New files are processed continuously or manu