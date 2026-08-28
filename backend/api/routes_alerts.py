from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.models import Alert, IOC


router = APIRouter(
    prefix="/api/alerts",
    tags=["Alerts"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class AlertCreate(BaseModel):
    alert_id: str
    detected_at: datetime
    source_ip: str
    asset_name: str | None = None
    anomaly_score: float | None = None
    anomaly_model: str | None = None
    ioc_matched: bool = False
    ioc_type: str | None = None
    shared_by: str | None = None
    llm_explanation: str | None = None
    risk_level: str
    recommended_action: str
    status: str = "PENDING_CONFIRMATION"


@router.get("/")
def get_alerts(db: Session = Depends(get_db)):

    alerts = db.query(Alert).all()

    return [
        {
            "alert_id": alert.alert_id,
            "detected_at": alert.detected_at,
            "source": {
                "ip": alert.source_ip,
                "asset_name": alert.asset_name
            },
            "anomaly": {
                "score": alert.anomaly_score,
                "model": alert.anomaly_model
            },
            "ioc_match": {
                "matched": alert.ioc_matched,
                "type": alert.ioc_type,
                "shared_by": alert.shared_by
            },
            "llm_explanation": alert.llm_explanation,
            "risk_level": alert.risk_level,
            "recommended_action": alert.recommended_action,
            "status": alert.status
        }
        for alert in alerts
    ]


@router.post("/")
def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db)
):

    # Check whether the source IP exists in the IOC database
    matched_ioc = (
        db.query(IOC)
        .filter(IOC.value == alert_data.source_ip)
        .first()
    )

    # Default values
    ioc_matched = False
    ioc_type = None
    shared_by = None

    # If IOC is found, automatically populate IOC information
    if matched_ioc:
        ioc_matched = True
        ioc_type = matched_ioc.type
        shared_by = matched_ioc.shared_by_org_hash

    alert = Alert(
        alert_id=alert_data.alert_id,
        detected_at=alert_data.detected_at,
        source_ip=alert_data.source_ip,
        asset_name=alert_data.asset_name,
        anomaly_score=alert_data.anomaly_score,
        anomaly_model=alert_data.anomaly_model,
        ioc_matched=ioc_matched,
        ioc_type=ioc_type,
        shared_by=shared_by,
        llm_explanation=alert_data.llm_explanation,
        risk_level=alert_data.risk_level,
        recommended_action=alert_data.recommended_action,
        status=alert_data.status
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return {
        "message": "Alert created successfully",
        "alert_id": alert.alert_id,
        "ioc_matched": ioc_matched,
        "ioc_type": ioc_type,
        "shared_by": shared_by
    }