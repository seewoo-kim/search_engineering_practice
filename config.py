import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # App Settings
    API_KEY = os.getenv("APP_API_KEY", None)
    
    # Database Settings
    DB_URL = os.getenv("DB_URL")
    
    # OpenSearch Settings
    OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST")
    OPENSEARCH_ID = os.getenv("OPENSEARCH_ID")
    OPENSEARCH_PW = os.getenv("OPENSEARCH_PW")
    OPENSEARCH_INDEX = "press-list-alias"

settings = Settings()
