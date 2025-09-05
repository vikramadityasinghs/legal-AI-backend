import os
from typing import Optional

class Settings:
    # API Configuration
    API_TITLE = "AI Legal Document Analysis API"
    API_VERSION = "1.0.0"
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT: str = os.getenv(
        "AZURE_OPENAI_ENDPOINT", 
        "https://rrtopenaiwrapperprodazure.optum.com/"
    )
    AZURE_OPENAI_API_KEY: str = os.getenv(
        "AZURE_OPENAI_API_KEY", 
        "kjagudhjagjsbdjkabjsdad"
    )
    AZURE_OPENAI_API_VERSION: str = os.getenv(
        "AZURE_OPENAI_API_VERSION", 
        "2023-05-15"
    )
    AZURE_OPENAI_DEPLOYMENT: str = os.getenv(
        "AZURE_OPENAI_DEPLOYMENT", 
        "RRT-OPENAI-GPT40-GS"
    )
    
    # File Processing Configuration
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    EXTRACTED_TEXTS_DIR: str = os.getenv("EXTRACTED_TEXTS_DIR", "./extracted_texts")
    EXPORT_DIR: str = os.getenv("EXPORT_DIR", "./exports")
    
    # File size limits (in bytes)
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB
    MAX_FILES_PER_JOB: int = int(os.getenv("MAX_FILES_PER_JOB", 50))
    
    # Supported file types
    SUPPORTED_FILE_TYPES = [".pdf", ".jpg", ".jpeg", ".png"]
    
    # OCR Configuration
    TESSERACT_CONFIG = "--oem 3 --psm 6"
    
    # Job Configuration
    JOB_TIMEOUT_MINUTES: int = int(os.getenv("JOB_TIMEOUT_MINUTES", 30))
    CLEANUP_COMPLETED_JOBS_HOURS: int = int(os.getenv("CLEANUP_COMPLETED_JOBS_HOURS", 24))
    
    # Redis Configuration (for production job queue)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # CORS Configuration
    ALLOWED_ORIGINS = [
        "http://localhost:3000",  # React dev server
        "http://localhost:3001",  # Alternative React port
    ]
    
    def __init__(self):
        # Create required directories
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.EXTRACTED_TEXTS_DIR, exist_ok=True)
        os.makedirs(self.EXPORT_DIR, exist_ok=True)

# Global settings instance
settings = Settings()
