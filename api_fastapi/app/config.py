import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://erpuser:erppass@localhost:5432/erpcenter")
API_JWT_SECRET = os.getenv("API_JWT_SECRET", "dev-secret")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60
