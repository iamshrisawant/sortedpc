import os
import shutil
import time
import random
import string
import numpy as np
import warnings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from sentence_transformers import util, SentenceTransformer
from scanner import DynamicScanner
from sorter import SemantiSorter
import config

# Suppress technical warnings for cleaner output
warnings.filterwarnings("ignore")

BENCHMARK_ENV = "benchmark_env"
TEST_INBOX = "test_inbox"

def normalize(path):
    if not path: return "None"
    return os.path.normpath(path).replace('\\', '/')

def generate_noise(text):
    """
    Simulates real-world 'dirty' data.
    Adds random prefixes (dates, ids) and noise (boilerplate).
    """
    prefix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    date = "2024-10-27"
    boilerplate = "CONFIDENTIAL. This document is intended for the recipient only. Page 1 of 5."
    
    # Randomly structure the file content
    formats = [
        f"{prefix}_{date} - {text}\n\n{boilerplate}",
        f"Subject: {text}\nDate: {date}\nRef: {prefix}\n\n{boilerplate}",
        f"{text} (ID: {prefix})",
        f"[SCANNED_DOC] {text} ... {boilerplate}"
    ]
    return random.choice(formats)

def setup_env():
    """Generates the Knowledge Base (Seeds) - The 'Training Set'"""
    if os.path.exists(BENCHMARK_ENV): shutil.rmtree(BENCHMARK_ENV)
    os.makedirs(BENCHMARK_ENV)
    
    # Expanded Seed Set
    seeds = {
        "Work/Finance": [
            "Invoice for Consultant Services - $500", 
            "Tax Deduction Form 1040", 
            "IRS Quarterly Statement Q3",
            "Bank Transfer Confirmation Details"
        ],
        "Work/Engineering": [
            "Python StackTrace Error Log", 
            "C++ Compiler Optimization Logs - gcc", 
            "Java Virtual Machine Config Heap Size",
            "API Endpoint Documentation JSON Schema"
        ],
        "Personal/Medical": [
            "Prescription 500mg Amoxicillin", 
            "Pharmacy Receipt CVS", 
            "Daily Dosage Instructions",
            "Doctor Appointment Reminder - Dr. Smith"
        ],
        "Work/HR": [
            "General Staff Memo - Holiday Policy", 
            "Employee Handbook 2024", 
            "Sexual Harassment Training Certificate"
        ]
    }
    
    docs, labels = [], []
    for f, txts in seeds.items():
        p = os.path.join(BENCHMARK_ENV, f)
        os.makedirs(p, exist_ok=True)
        for i, t in enumerate(txts):
            with open(os.path.join(p, f"{i}.txt"), "w") as file: file.write(t)
            docs.append(t)
            labels.append(normalize(f))
    return docs, labels

# --- Competitors ---

class LexicalSearchBaseline:
    """
    Represents the 'Old School' Search approach.
    Uses TF-IDF vectors + Cosine Similarity.
    Fast, but dumb (doesn't understand synonyms).
    """
    def __init__(self, docs, labels):
        self.v = TfidfVectorizer()
        self.X = self.v.fit_transform(docs)
        self.L = labels
        
    def predict(self, txt):
        vec = self.v.transform([txt])
        if vec.nnz == 0: return "None"
        sims = cosine_similarity(vec, self.X).flatten()
        return self.L[np.argmax(sims)]

class NaiveBayesBaseline:
    """
    Represents the 'Standard ML' approach.
    Uses Multinomial Naive Bayes on TF-IDF features.
    Probabilistic and robust, but relies heavily on keyword overlap.
    """
    def __init__(self, docs, labels):
        self.v = TfidfVectorizer()
        X = self.v.fit_transform(docs)
        self.clf = MultinomialNB()
        self.clf.fit(X, labels)
        
    def predict(self, txt):
        vec = self.v.transform([txt])
        # Get probability to potentially reject low-confidence
        probs = self.clf.predict_proba(vec)[0]
        if max(probs) < 0.2: return "None"
        return self.clf.predict(vec)[0]

class SbertCentroidBaseline:
    """
    Represents the 'Lightweight AI' approach.
    Computes the AVERAGE vector for each folder.
    Fast, but ignores nuances (e.g. outlier files in a folder).
    """
    def __init__(self, vectors, labels, model):
        self.model = model
        self.centroids = {}
        counts = {}
        # Compute mean vector per folder
        for vec, label in zip(vectors, labels):
            if label not in self.centroids:
                self.centroids[label] = np.zeros_like(vec)
                counts[label] = 0
            self.centroids[label] += vec
            counts[label] += 1
        
        self.keys = list(self.centroids.keys())
        # Average them
        self.matrix = np.array([self.centroids[k]/counts[k] for k in self.keys])

    def predict(self, txt):
        vec = self.model.encode(txt)
        scores = util.cos_sim(vec, self.matrix)[0]
        return self.keys[np.argmax(scores)]

def run():
    print("===============================================================")
    print("   HONEST BENCHMARK: SemantiSort vs Traditional Methods")
    print("===============================================================")
    print("Scenario: Sorting a LARGE BACKLOG of noisy files (Personal System Simulation).")
    
    # 1. Setup Environment
    tr_docs, tr_labels = setup_env()
    print(f"[Setup] Created Knowledge Base with {len(tr_docs)} seed files across {len(set(tr_labels))} categories.")
    
    # 2. Initialize Models
    print("\n[Init] Training Competitors...")
    old_dest = config.DEST_DIR
    config.DEST_DIR = BENCHMARK_ENV
    
    # A. SemantiSort (Our System)
    # We must scan first to build the 'Vector Cloud'
    DynamicScanner().scan_directory(BENCHMARK_ENV)
    semanti_sorter = SemantiSorter()
    
    # B. Lexical Search (Classic)
    lexical = LexicalSearchBaseline(tr_docs, tr_labels)
    
    # C. Naive Bayes (Standard ML)
    bayes = NaiveBayesBaseline(tr_docs, tr_labels)
    
    # D. SBERT Centroid (Alternative AI)
    # Reuse the bi-encoder to be fair (same compute power/model size)
    if semanti_sorter.vectors is not None:
        vectors = semanti_sorter.vectors
        labels = [i['path'] for i in semanti_sorter.instances]
        centroid_model = SbertCentroidBaseline(vectors, labels, semanti_sorter.bi_encoder)
    else:
        print("Critical Error: SemantiSort failed to index.")
        return

    # 3. Generate Evaluation Data (Unseen by training)
    # We mix Easy (Lexical) and Hard (Semantic) cases
    base_cases = [
        # --- Easy (Keyword Matches) ---
        ("inv_1.txt", "Invoice for July Services", "Work/Finance"),
        ("err_1.txt", "Python StackTrace Error", "Work/Engineering"),
        
        # --- Medium (Synonyms) ---
        ("fiscal.txt", "Fiscal Year End Summary", "Work/Finance"), # 'Fiscal' ~= 'Tax/Invoice'
        ("meds.txt", "Patient Clinical Report", "Personal/Medical"), # 'Clinical' ~= 'Medical'
        
        # --- Hard (Ambiguous / Contextual) ---
        ("aws.txt", "AWS Cloud Server Monthly Cost", "Work/Finance"), # 'AWS' usually Eng, but 'Cost' -> Finance
        ("python_fin.txt", "Python Script for calculating Taxes", "Work/Engineering"), # 'Taxes' usually Fin, but 'Script' -> Eng
        ("hiring.txt", "New Developer Onboarding Checklist", "Work/HR"), # Semantically distinct from other Eng docs
        
        # --- Out/None (Should be rejected or misclassified if brittle) ---
        ("random.txt", "Recipe for Chocolate Cake", "None") # Should ideally be None or low score
    ]
    
    test_set = []
    # Generate 40 variations of each base case (Total ~320 files)
    # This simulates a "Backlog" or "Pile" found on a neglected personal system
    files_per_case = 40
    print(f"[Data] Generative Parameters: {files_per_case} variations per case x {len(base_cases)} cases.")
    
    for _ in range(files_per_case): 
        for fname, content, exp in base_cases:
            noisy_content = generate_noise(content)
            unique_name = f"{random.randint(10000,99999)}_{fname}"
            test_set.append({
                "name": unique_name,
                "content": noisy_content,
                "label": normalize(exp)
            })

    print(f"[Data] Created a stress-test pile of {len(test_set)} files.")
    
    if os.path.exists(TEST_INBOX): shutil.rmtree(TEST_INBOX)
    os.makedirs(TEST_INBOX)

    # 4. The Race
    models = {
        "Lexical (TF-IDF)": lexical,
        "Naive Bayes": bayes,
        "Centroid (AI)": centroid_model,
        "SemantiSort (AI)": semanti_sorter # Fits different interface
    }
    
    # Storage for results
    results = {name: {"y_true": [], "y_pred": [], "latencies": []} for name in models}
    
    print("\n[Run] Processing Pile...")
    
    # Write files to disk once to simulate real folder conditions
    paths = []
    for item in test_set:
        fpath = os.path.join(TEST_INBOX, item['name'])
        with open(fpath, "w") as f: f.write(item['content'])
        paths.append(fpath)
        
    start_global = time.time()
    
    for i, item in enumerate(test_set):
        text = item['content']
        truth = item['label']
        fpath = paths[i]
        
        if i % 50 == 0:
            print(f"  Processed {i}/{len(test_set)} files...")

        # We run each model on the file
        for name, model in models.items():
            t0 = time.time()
            
            # SemantiSort allows 'None' if confidence is low or folders don't match
            # But here we force a prediction or capture 'None'
            
            if name == "SemantiSort (AI)":
                # SemantiSort requires file path to respect I/O overhead
                pred, _, _ = model.predict_folder(fpath)
                if not pred: pred = "None"
            else:
                pred = model.predict(text)
                
            lat = (time.time() - t0) * 1000
            
            results[name]["y_true"].append(truth if truth != "None" else "None") # Normalize truth
            results[name]["y_pred"].append(normalize(pred))
            results[name]["latencies"].append(lat)

    print(f"[Done] Benchmarking complete in {time.time() - start_global:.2f}s.")
    config.DEST_DIR = old_dest # Restore

    # 5. Final Report
    print("\n" + "="*110)
    print(f"{'ALGORITHM':<20} | {'ACCURACY':<10} | {'AVG LATENCY':<15} | {'THROUGHPUT':<15} | {'F1-SCORE':<20}")
    print("-" * 110)
    
    best_acc = 0
    winner = ""
    
    for name, data in results.items():
        y_true = data["y_true"]
        y_pred = data["y_pred"]
        lat = np.mean(data["latencies"])
        
        acc = accuracy_score(y_true, y_pred)
        p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
        
        # Throughput: Files per Minute
        throughput = (60 * 1000) / lat if lat > 0 else 0
        
        print(f"{name:<20} | {acc*100:<9.1f}% | {lat:<9.2f} ms    | {throughput:<6.0f} files/min | {f1:.3f}")
        
        if acc > best_acc:
            best_acc = acc
            winner = name

    print("-" * 110)
    print(f"🏆 WINNER: {winner}")
    print("\nDetailed breakdown for SemantiSort:")
    print(classification_report(results["SemantiSort (AI)"]["y_true"], results["SemantiSort (AI)"]["y_pred"], zero_division=0))

if __name__ == "__main__":
    run()