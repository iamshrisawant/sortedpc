# setup_models.py

import os, shutil
from huggingface_hub import hf_hub_download

MODELS = {
    "mistral": ("TheBloke/Mistral-7B-Instruct-v0.1-GGUF", "mistral-7b-instruct-v0.1.Q4_K_M.gguf"),
    "tinyllama": ("TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF", "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"),
    "phi2": ("raghav0/phi-2-Q4_K_M-GGUF", "phi-2-q4_k_m.gguf")
}

target_dir = "src/core/models"
os.makedirs(target_dir, exist_ok=True)

for key, (repo, fname) in MODELS.items():
    print(f"📥 Downloading {key}...")
    path = hf_hub_download(repo_id=repo, filename=fname)
    dest = os.path.join(target_dir, fname)
    shutil.copy(path, dest)
    print(f"✅ {key} saved at {dest}")
