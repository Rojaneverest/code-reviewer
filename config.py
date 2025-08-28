import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# PostgreSQL Database Configuration
# Uses local PostgreSQL database since runner runs locally
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "rules"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "root"),
    "host": os.getenv("DB_HOST", "localhost"),  # Local PostgreSQL database
    "port": os.getenv("DB_PORT", "5432")
}

# LLM Configuration - Supports both LM Studio (local dev) and Databricks (production)
LLM_CONFIG = {
    # Databricks configuration (for production/CI)
    "databricks": {
        "enabled": bool(os.getenv("DATABRICKS_TOKEN")),
        "token": os.getenv("DATABRICKS_TOKEN"),
        "base_url": os.getenv("DATABRICKS_BASE_URL", "https://dbc-3735add4-1cb6.cloud.databricks.com"),
        "endpoint": os.getenv("DATABRICKS_ENDPOINT", "/serving-endpoints/databricks-claude-sonnet-4/invocations"),
        "model_name": os.getenv("DATABRICKS_MODEL_NAME", "databricks-claude-sonnet-4"),
        "timeout": int(os.getenv("DATABRICKS_TIMEOUT", "60"))
    },
    # LM Studio configuration (for local development)
    "lm_studio": {
        "enabled": not bool(os.getenv("DATABRICKS_TOKEN")) or bool(os.getenv("ENABLE_LM_STUDIO_FALLBACK")),
        "api_base": os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"),
        "api_key": "not-needed",
        "timeout": int(os.getenv("LM_STUDIO_TIMEOUT", "60"))
    }
}

# Legacy LM Studio config for backward compatibility
LM_STUDIO_CONFIG = LLM_CONFIG["lm_studio"]
