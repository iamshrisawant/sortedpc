# Sorted: Mirroring Human Logic via Local-First Semantic Organization

![Pipeline Diagram](assets/pipeline.png)

## Abstract
**Sorted** is a research project designed to mirror human file organization logic using a **local-first, semantic approach**. Unlike traditional automation tools that rely on rigid regex or keyword matching, Sorted uses a **Bi-Encoder Neural Network (all-MiniLM-L6-v2)** to understand the *context* and *meaning* of your files.

It observes how you organize your files and learns to replicate that logic automatically. It features **Rank-Weighted k-NN classification**, **Depth Bias**, and a **Confidence Threshold** system to ensure high-precision sorting while leaving uncertain files for human review (Open-Set Recognition).

## Key Features

*   **🔒 Local-First & Privacy-Focused**: All processing happens on your device. No data is sent to the cloud.
*   **🧠 Semantic Understanding**: Understands file content (not just filenames) using state-of-the-art sentence transformers.
*   **🔁 Online Learning**: Instantly learns from new examples. When a file is sorted (automatically or manually moved and scanned), the system updates its vector index immediately.
*   **🛡️ Open-Set Recognition**: Files with low confidence scores are explicitly **rejected** and left in the Inbox, preventing misclassification.
*   **📂 Hierarchical Awareness**: Implements a "Depth Bias" to prefer specific sub-folders over generic root folders when semantic similarity is close.
*   **⚡ Debounced Watching**: Monitors your `inbox` folder in real-time, waiting for file writes to complete before processing.

## Architecture Pipeline

1.  **Inbox Monitoring**: The `Watcher` script monitors the target directory.
2.  **Extraction**: Text is extracted from the document (Header + Footer chunks for efficiency).
3.  **Encoding**: The `SemantiSorter` encodes the document context into a high-dimensional vector.
4.  **Retrieval**: The system queries the "Vector Cloud" (existing sorted files) for the nearest neighbors.
5.  **Classification**: 
    *   **Rank-Weighted k-NN**: Neighbors are weighted by their rank (closer neighbors vote more).
    *   **Depth Bias**: Deeper folder paths get a slight score boost to encourage specific sorting.
6.  **Decision**:
    *   If `Score > Confidence Threshold`: **Move** to target folder.
    *   If `Score < Confidence Threshold`: **Reject** (leave in Inbox).

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/sorted.git
    cd sorted
    ```

2.  **Install Dependencies**:
    Recommendation: Use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
    *Dependencies include: `torch`, `sentence-transformers`, `watchdog`, `numpy`, `scikit-learn`.*

3.  **Directory Setup**:
    Ensure your directory structure matches `config.py` (or modify `config.py`):
    *   `inbox/`: Where new files arrive.
    *   `sorted/`: Your organized file structure (Ground Truth).

## Usage

### 1. Initialize the Knowledge Base (Vector Cloud)
Before the system can sort anything, it needs to "learn" your existing organization structure.

```bash
python scanner.py
```
*   This scans the `sorted/` directory.
*   Encodes all valid files (`.txt`, `.pdf`, `.docx`).
*   Builds and saves the `file_index.pkl`.

### 2. Start the Watcher
Run the watcher to monitor your inbox.

```bash
python watcher.py
```
*   The system now watches `inbox/`.
*   Drop a file into `inbox/`.
*   Check the console for live sorting logs (Latency, Method, Confidence Score).

### 3. Benchmarking (For Researchers)
To evaluate the system's performance against a standard dataset (e.g., 20 Newsgroups):

```bash
python benchmark.py
```
*   Runs a simulation of the sorting process.
*   Calculates Accuracy, F1-Score, and Unknown Detection Rates.
*   Generates performance plots (`fig4_accuracy_analysis.png`, `fig5_efficiency.png`).

## Configuration (`config.py`)

*   **`BI_ENCODER_MODEL`**: Default `'all-MiniLM-L6-v2'`. Light and fast.
*   **`CONFIDENCE_THRESHOLD`**: Default `0.5`. Adjust this to tune the aggressive/conservative nature of the sorter.
*   **`K_NEIGHBORS`**: Number of neighbors to consider (Default `5`).
*   **`DEPTH_WEIGHT`**: Bias toward deeper directory structures (Default `0.08`).
*   **`OFFLINE_MODE`**: Set to `True` for air-gapped environments (requires pre-downloaded models).

## Project Structure

```
Sorted/
├── assets/             # Project visual assets
├── inbox/              # Watch folder
├── sorted/             # Destination/Training folder
├── sorter.py           # Core Ranking & Sorting Engine
├── watcher.py          # Real-time File System Monitor
├── scanner.py          # Index Builder (Offline Learning)
├── benchmark.py        # Academic Benchmarking Suite
├── calibration.py      # Threshold Calibration Tool
└── config.py           # Global Configuration
```

## License
MIT License
