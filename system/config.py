import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
load_dotenv("code/elastic-start-local/.env")

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Set LLM configuration
LLM_MODEL = "gemini/gemini-2.5-flash-preview-05-20"
LLM_TEMPERATURE = 0.2

# Set vector database configuration
VECTOR_DB_HOST = "http://localhost:9200"
VECTOR_DB_INDEX = "document_vectors"

# Set directories
PROMPTS_DIR = "./system/prompts"
OUTPUT_DIR = "./system/output"
DATA_DIR = "./system/data"

os.makedirs(PROMPTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set minutes
BASELINE_MINUTE_IDS = [
    "h-tk-20182019-35-8-n1",
    "h-tk-20182019-64-32",
    "h-tk-20012002-4369-4373",
    "h-tk-20072008-2932-2933",
    "h-tk-20022003-3055-3080",
]