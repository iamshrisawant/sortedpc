import os
import shutil
import time
import random
import string
import numpy as np
import warnings

# CRITICAL: Force Offline Mode before importing transformers to prevent network errors
os.environ['HF_HUB_DISABLE_SSL_VERIFY'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

from sklearn.datasets import fetch_20newsgroups, load_files, get_data_home
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sentence_transformers import util
from scanner import DynamicScanner
from sorter import SemantiSorter
import config

# Suppress technical warnings
warnings.filterwarnings("ignore")

BENCHMARK_ENV = "benchmark_env"
TEST_INBOX = "test_inbox"

def normalize(path):
    if not path: return "None"
    return os.path.normpath(path).replace('\\', '/')

def generate_noise(text):
    prefix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    date = "2024-10-27"
    boilerplate = "CONFIDENTIAL. This document is intended for the recipient only. Page 1 of 5."
    
    noisy_text = text if text else ""
    chars = list(noisy_text)
    for i in range(len(chars)):
        if random.random() < 0.05: 
            if random.random() < 0.5:
                if i < len(chars) - 1:
                    chars[i], chars[i+1] = chars[i+1], chars[i]
            else:
                chars[i] = random.choice(string.ascii_lowercase)
    noisy_text = "".join(chars)

    formats = [
        f"{prefix}_{date} - {noisy_text}\n\n{boilerplate}",
        f"Subject: {noisy_text}\nDate: {date}\nRef: {prefix}\n\n{boilerplate}",
        f"{noisy_text} (ID: {prefix})",
        f"[SCANNED_DOC] {noisy_text} ... {boilerplate}"
    ]
    return random.choice(formats)

def setup_env():
    if os.path.exists(BENCHMARK_ENV): shutil.rmtree(BENCHMARK_ENV)
    os.makedirs(BENCHMARK_ENV)
    
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

class LexicalSearchBaseline:
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
    def __init__(self, docs, labels):
        self.v = TfidfVectorizer()
        X = self.v.fit_transform(docs)
        self.clf = MultinomialNB()
        self.clf.fit(X, labels)
        
    def predict(self, txt):
        vec = self.v.transform([txt])
        probs = self.clf.predict_proba(vec)[0]
        if max(probs) < 0.2: return "None"
        return self.clf.predict(vec)[0]

class SbertCentroidBaseline:
    def __init__(self, vectors, labels, model):
        self.model = model
        self.centroids = {}
        counts = {}
        for vec, label in zip(vectors, labels):
            if label not in self.centroids:
                self.centroids[label] = np.zeros_like(vec)
                counts[label] = 0
            self.centroids[label] += vec
            counts[label] += 1
        
        self.keys = list(self.centroids.keys())
        self.matrix = np.array([self.centroids[k]/counts[k] for k in self.keys])

    def predict(self, txt):
        vec = self.model.encode(txt)
        scores = util.cos_sim(vec, self.matrix)[0]
        return self.keys[np.argmax(scores)]

def evaluate_phase(phase_name, train_docs, train_labels, test_data):
    print(f"\n>>> Running {phase_name} <<<")
    print(f"Training Size: {len(train_docs)} docs")
    print(f"Test Size: {len(test_data)} docs")
    
    phase_env = f"env_{phase_name.replace(' ', '_')}"
    if os.path.exists(phase_env): shutil.rmtree(phase_env)
    os.makedirs(phase_env)
    
    for i, (doc, label) in enumerate(zip(train_docs, train_labels)):
        path = label.replace('.', '/')
        dpath = os.path.join(phase_env, path)
        os.makedirs(dpath, exist_ok=True)
        with open(os.path.join(dpath, f"{i}.txt"), "w", encoding='latin-1', errors='ignore') as f:
            f.write(doc)
            
    DynamicScanner().scan_directory(phase_env)
    semanti_sorter = SemantiSorter()
    
    lexical = LexicalSearchBaseline(train_docs, train_labels)
    bayes = NaiveBayesBaseline(train_docs, train_labels)
    
    if semanti_sorter.vectors is not None:
        centroid_model = SbertCentroidBaseline(semanti_sorter.vectors, [i['path'] for i in semanti_sorter.instances], semanti_sorter.bi_encoder)
    else:
        print("Error: No vectors")
        return

    models = {"Lexical": lexical, "Bayes": bayes, "Centroid": centroid_model, "SemantiSort": semanti_sorter}
    results = {name: {"y_true": [], "y_pred": [], "latencies": []} for name in models}
    
    test_inbox = f"test_inbox_{phase_name.replace(' ', '_')}"
    if os.path.exists(test_inbox): shutil.rmtree(test_inbox)
    os.makedirs(test_inbox)
    
    paths = []
    print("Writing verification files to disk...")
    for i, item in enumerate(test_data):
        fpath = os.path.join(test_inbox, item['name'])
        with open(fpath, "w", encoding='latin-1', errors='ignore') as f: f.write(item['content'])
        paths.append(fpath)
    
    print("Starting Inference Loop...")
    ss_correct, ss_total = 0, 0
    
    for i, item in enumerate(test_data):
        text, truth, fpath = item['content'], normalize(item['label']), paths[i]
        ss_total += 1

        if i > 0 and i % 50 == 0:
            acc = ss_correct / (ss_total-1) * 100
            print(f"  [Batch {i}] SemantiSort Accuracy: {acc:.1f}%")

        for name, model in models.items():
            t0 = time.time()
            if name == "SemantiSort":
                res, _, _ = model.predict_folder(fpath)
                pred = res if res else "None"
            else:
                pred = model.predict(text)
                
            # UNIVERSAL FIX: Convert folder paths (sci/med) back to dot-labels (sci.med) for Phase B
            if phase_name == "Phase B (Academic)" and pred != "None":
                pred = pred.replace('/', '.')
                
            lat = (time.time() - t0) * 1000
            p_norm = normalize(pred)
            
            results[name]["y_true"].append(truth)
            results[name]["y_pred"].append(p_norm)
            results[name]["latencies"].append(lat)
            
            if name == "SemantiSort" and p_norm == truth:
                ss_correct += 1
                    
    print(f"\n--- Results: {phase_name} ---")
    print(f"{'ALGORITHM':<20} | {'ACCURACY':<10} | {'LATENCY':<15} | {'F1-SCORE':<20}")
    print("-" * 80)
    
    for name, data in results.items():
        acc = accuracy_score(data["y_true"], data["y_pred"])
        lat = np.mean(data["latencies"])
        _, _, f1, _ = precision_recall_fscore_support(data["y_true"], data["y_pred"], average='weighted', zero_division=0)
        print(f"{name:<20} | {acc*100:<9.1f}% | {lat:<9.2f} ms    | {f1:.3f}")
    
    for p in [phase_env, test_inbox]:
        if os.path.exists(p): shutil.rmtree(p)

def run():
    print("===============================================================")
    print("   MULTI-DATASET BENCHMARK: Synthethic vs Academic")
    print("===============================================================")
    
    old_dest = config.DEST_DIR
    tr_docs, tr_labels = setup_env()
    
    base_cases = [
        ("inv_1.txt", "Invoice for July Services", "Work/Finance"),
        ("err_1.txt", "Python StackTrace Error", "Work/Engineering"),
        ("fiscal.txt", "Fiscal Year End Summary", "Work/Finance"), 
        ("meds.txt", "Patient Clinical Report", "Personal/Medical"), 
        ("aws.txt", "AWS Cloud Server Monthly Cost", "Work/Finance"),
        ("python_fin.txt", "Python Script for calculating Taxes", "Work/Engineering"),
        ("hiring.txt", "New Developer Onboarding Checklist", "Work/HR"),
        ("random.txt", "Recipe for Chocolate Cake", "None") 
    ]
    
    test_set_A = []
    for _ in range(40): 
        for fname, content, exp in base_cases:
            test_set_A.append({"name": f"{random.randint(10000,99999)}_{fname}", "content": generate_noise(content), "label": normalize(exp)})
            
    evaluate_phase("Phase A (Synthetic)", tr_docs, tr_labels, test_set_A)
    
    print("\n[Setup] Fetching 20 Newsgroups Dataset...")
    cats = ['sci.med', 'rec.autos', 'comp.graphics', 'misc.forsale']
    
    try:
        newsgroups_train = fetch_20newsgroups(subset='train', categories=cats, remove=('headers', 'footers', 'quotes'), download_if_missing=False)
        newsgroups_test = fetch_20newsgroups(subset='test', categories=cats, remove=('headers', 'footers', 'quotes'), download_if_missing=False)
    except Exception:
        base_dir = os.path.join(get_data_home(), "20news_home")
        train_dir, test_dir = os.path.join(base_dir, "20news-bydate-train"), os.path.join(base_dir, "20news-bydate-test")
        if os.path.exists(train_dir):
            newsgroups_train = load_files(train_dir, categories=cats, encoding='latin-1')
            newsgroups_test = load_files(test_dir, categories=cats, encoding='latin-1')
        else:
            print("Critical: Dataset not found.")
            return

    test_set_B = [{"name": f"news_{i}.txt", "content": txt, "label": normalize(newsgroups_test.target_names[idx])} 
                  for i, (txt, idx) in enumerate(zip(newsgroups_test.data, newsgroups_test.target)) if txt.strip()]
    
    evaluate_phase("Phase B (Academic)", newsgroups_train.data, [newsgroups_train.target_names[i] for i in newsgroups_train.target], test_set_B)
    config.DEST_DIR = old_dest

if __name__ == "__main__":
    run()