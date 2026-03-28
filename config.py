import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
DB_DIR = PROJECT_ROOT / "db"
VECTORSTORE_DIR = PROJECT_ROOT / "vectorstore"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)
VECTORSTORE_DIR.mkdir(exist_ok=True)

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# FAISS Configuration
VECTOR_STORE_PATH = VECTORSTORE_DIR / "faiss_index"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Database Configuration
DB_PATH = DB_DIR / "lab_assistant.db"

# PDF Processing
MAX_PDF_SIZE = 50 * 1024 * 1024  # 50 MB
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# spaCy model
SPACY_MODEL = "en_core_web_sm"
