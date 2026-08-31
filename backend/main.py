from fastapi import FastAPI

from api.routes_alerts import router as alerts_router
from api.routes_ioc import router as ioc_router
from api.routes_remediation import router as remediation_router
from api.routes_auth import router as auth_router

from db.database import engine, Base
from db import models


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="APNG - Autonomous Predictive Network Guardian",
    version="1.0.0",
    description="Backend orchestration engine for APNG"
)


# Register API routers
app.include_router(alerts_router)
app.include_router(ioc_router)
app.include_router(remediation_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {
        "message": "APNG Backend is running",
        "status": "success"
    }