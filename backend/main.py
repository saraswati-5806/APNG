import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes_alerts import router as alerts_router
from api.routes_ioc import router as ioc_router
from api.routes_remediation import router as remediation_router
from api.routes_auth import router as auth_router
from api.routes_telemetry import router as telemetry_router
from api.routes_topology import router as topology_router

from db.database import engine, Base
from db import models


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="APNG - Autonomous Predictive Network Guardian",
    version="1.0.0",
    description="Backend orchestration engine for APNG"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(alerts_router)
app.include_router(ioc_router)
app.include_router(remediation_router)
app.include_router(auth_router)
app.include_router(telemetry_router)
app.include_router(topology_router)


@app.get("/")
def root():
    return {
        "message": "APNG Backend is running",
        "status": "success"
    }