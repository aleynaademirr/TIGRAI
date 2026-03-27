import os
from typing import List
from dotenv import load_dotenv
load_dotenv()
class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./recommendation_system.db"
    )
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "true").lower() == "true"
    CORS_ORIGINS: List[str] = [
        origin.strip() 
        for origin in os.getenv(
            "CORS_ORIGINS", 
            "http://localhost:3000,http://localhost:8000"
        ).split(",")
        if origin.strip()
    ]
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "supersecretkey"
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    ML_MODEL_MAX_FEATURES: int = int(
        os.getenv("ML_MODEL_MAX_FEATURES", "5000")
    )
    ML_MODEL_TOP_N_RECOMMENDATIONS: int = int(
        os.getenv("ML_MODEL_TOP_N_RECOMMENDATIONS", "5")
    )
    RATE_LIMIT_PER_MINUTE: int = int(
        os.getenv("RATE_LIMIT_PER_MINUTE", "60")
    )
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
settings = Settings()