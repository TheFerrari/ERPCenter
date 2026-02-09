import os

DATABASE_URL = os.getenv("DATABASE_URL")
POSTGRES_DB = os.getenv("POSTGRES_DB", "erpcenter")
POSTGRES_USER = os.getenv("POSTGRES_USER", "erpuser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "erppass")
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")

if not DATABASE_URL:
    DATABASE_URL = (
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{DATABASE_HOST}:5432/{POSTGRES_DB}"
    )

JWT_SECRET = os.getenv("API_JWT_SECRET", "dev-secret")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
