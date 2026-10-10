
import os

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is missing. Set it in your environment."
    )

APP_NAME = "APNG - Autonomous Predictive Network Guardian"
