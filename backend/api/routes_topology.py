from fastapi import APIRouter, Depends

from core.auth import get_current_user
from db.models import User


router = APIRouter(
    prefix="/api/topology",
    tags=["Topology"],
)


@router.get("/")
def get_topology(current_user: User = Depends(get_current_user)):
    return {
        "nodes": [
            {
                "id": "APNG",
                "label": "APNG",
                "type": "ORCHESTRATOR",
                "status": "healthy",
            },
            {
                "id": "EDGE-04",
                "label": "EDGE-04",
                "type": "NETWORK NODE",
                "status": "healthy",
            },
            {
                "id": "APP-03",
                "label": "APP-03",
                "type": "APPLICATION",
                "status": "healthy",
            },
            {
                "id": "DB-01",
                "label": "DB-01",
                "type": "DATABASE",
                "status": "healthy",
            },
            {
                "id": "WORKSTATION",
                "label": "WORKSTATION",
                "type": "ENDPOINT",
                "status": "healthy",
            },
        ],
        "edges": [
            {"source": "APNG", "target": "EDGE-04"},
            {"source": "APNG", "target": "APP-03"},
            {"source": "APNG", "target": "DB-01"},
            {"source": "APNG", "target": "WORKSTATION"},
        ],
    }