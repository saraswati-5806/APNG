import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:12345@localhost:5432/apng_db"
)

APP_NAME = "APNG - Autonomous Predictive Network Guardian"