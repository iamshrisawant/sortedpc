import os

# CRITICAL: Disable SSL Verify to bypass proxy/corporate blocking issues
os.environ['HF_HUB_DISABLE_SSL_VERIFY'] = '1'

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(BASE_DIR, "inbox")
DEST_DIR = os.path.join(BASE_DIR, "sorted")
INDEX_PATH = os.path.join(BASE_DIR, "file_index.pkl")

# Ensure directories exist
os.makedirs(SOURCE_DIR, exist_ok=True)
os.makedirs(DEST_DIR, exist_ok=True)

# Models
BI_ENCODER_MODEL = 'all-MiniLM-L6-v2'

# Feature Settings
MIN_FILES_FOR_STATS = 3
SUPPORTED_EXTENSIONS = {'.txt', '.pdf', '.docx'}

# Rank-Weighted k-NN Parameters
K_NEIGHBORS = 5
DEPTH_WEIGHT = 0.08  # Balanced specificity (validated for fair evaluation)
