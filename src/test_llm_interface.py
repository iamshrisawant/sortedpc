import os
import sys
import time
import statistics
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from core.llm_interface import load_model_runner

# Define test scenarios
TEST_QUERY = "What is the capital of France?"
TEST_DOC_CONTENT = "This is an electricity bill for the month of June 2023 from Adani Electricity Mumbai."
TEST_FOLDER_LABELS = ["Bills", "Travel", "Personal", "Banking", "Receipts"]
TEST_QA_DOCS = [
    ("credit_card_statement.pdf", "This file contains details about your recent credit card transaction with HDFC Bank for ₹5000 on Flipkart.")
]
TEST_QA_QUERY = "What kind of document is this?"

MODELS = {
    "tinyllama": "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
    "phi2": "models/phi-2-q4_k_m.gguf",
    "mistral": "models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
    "distilgpt2": "distilgpt2"
}

# To store overall scores and timings
model_scores = {}
model_times = {}


def score_generation(output):
    return 1 if "paris" in output.lower() else 0

def score_classification(output):
    return 1 if "bills" in output.lower() else 0

def score_qa(output):
    return 1 if "credit card" in output.lower() else 0


def run_tests(model_name, model_path):
    print(f"\n====================\n🔍 Testing {model_name.upper()}\n====================")
    llm = load_model_runner(model_path)

    scores = []
    times = []

    # --- Test 1: Basic Generation ---
    print("\n1️⃣ Basic generation test")
    print("Prompt:", TEST_QUERY)
    start = time.time()
    output = llm.run(TEST_QUERY)
    duration = round(time.time() - start, 2)
    score = score_generation(output)
    print("⏱️ Execution time:", duration, "s")
    print("🧠 Output:", output)
    print("🧪 Score:", score)
    scores.append(score)
    times.append(duration)

    # --- Test 2: Classification ---
    print("\n2️⃣ Classification test")
    prompt = llm.render_classification_prompt(TEST_DOC_CONTENT, TEST_FOLDER_LABELS)
    start = time.time()
    output = llm.run(prompt)
    duration = round(time.time() - start, 2)
    score = score_classification(output)
    print("⏱️ Execution time:", duration, "s")
    print("🧠 Output:", output)
    print("🧪 Score:", score)
    scores.append(score)
    times.append(duration)

    # --- Test 3: QA ---
    print("\n3️⃣ QA test")
    prompt = llm.render_qa_prompt(TEST_QA_QUERY, TEST_QA_DOCS)
    start = time.time()
    output = llm.run(prompt)
    duration = round(time.time() - start, 2)
    score = score_qa(output)
    print("⏱️ Execution time:", duration, "s")
    print("🧠 Output:", output)
    print("🧪 Score:", score)
    scores.append(score)
    times.append(duration)

    model_scores[model_name] = scores
    model_times[model_name] = times


if __name__ == "__main__":
    for name, path in MODELS.items():
        full_path = os.path.join("src/core", path) if not name.startswith("distilgpt2") else path
        run_tests(name, full_path)

    print("\n====================\n📊 SUMMARY\n====================")
    print("Model      | Score (out of 3) | Avg Time (s)")
    print("-----------|------------------|--------------")
    for model in MODELS:
        score = sum(model_scores[model])
        avg_time = round(statistics.mean(model_times[model]), 2)
        print(f"{model:<10} | {score:^16} | {avg_time:^12}")
