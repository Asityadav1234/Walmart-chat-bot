import os
from dotenv import load_dotenv
load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_MODEL = "mistral-small"  # or "mistral-medium" if needed
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
