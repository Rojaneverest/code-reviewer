import os

# PostgreSQL Database Configuration
# Uses environment variables with fallbacks for local development
DB_CONFIG = {
    "dbname": os.getenv("dbname", "rules"),
    "user": os.getenv("user", "postgres"),
    "password": os.getenv("password", "root"),
    "host": os.getenv("host", "localhost"),  # Will be 'postgres' in GitLab CI
    "port": os.getenv("port", "5432")
}

# LM Studio API Configuration
LM_STUDIO_CONFIG = {
    "api_base": "http://localhost:1234/v1",
    "api_key": "not-needed"
}
