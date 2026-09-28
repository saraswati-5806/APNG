from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.auth import get_current_user
from db.database import SessionLocal
from db.models import Alert, IOC, User
from ml_engine.scorer import predict


router = APIRouter(
    prefix="/api/telemetry",
    tags=["Telemetry"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TelemetryIn(BaseModel):
    sensor: str
    source_ip: str
    asset_name: str | None = None
    status: str = "normal"
    details: str | None = None

    flow_duration: float
    total_fwd_packets: float
    total_backward_packets: float
    total_length_fwd_packets: float
    total_length_bwd_packets: float
    flow_bytes_per_sec: float
    flow_packets_per_sec: float
    packet_length_mean: float
    packet_length_std: float
    syn_flag_count: float
    ack_flag_count: float


@router.post("/ingest")
def ingest_telemetry(
    data: TelemetryIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ml_features = {
        "Flow Duration": data.flow_duration,
        "Total Fwd Packets": data.total_fwd_packets,
        "Total Backward Packets": data.total_backward_packets,
        "Total Length of Fwd Packets": data.total_length_fwd_packets,
        "Total Length of Bwd Packets": data.total_length_bwd_packets,
        "Flow Bytes/s": data.flow_bytes_per_sec,
        "Flow Packets/s": data.flow_packets_per_sec,
        "Packet Length Mean": data.packet_length_mean,
        "Packet Length Std": data.packet_length_std,
        "SYN Flag Count": data.syn_flag_count,
        "ACK Flag Count": data.ack_flag_count,
    }

    ml_result = predict(ml_features)

    matched_ioc = (
        db.query(IOC)
        .filter(IOC.value == data.source_ip)
        .first()
    )

    ioc_matched = matched_ioc is not None
    ioc_type = matched_ioc.type if matched_ioc else None
    shared_by = (
        matched_ioc.shared_by_org_hash
        if matched_ioc
        else None
    )

    if ml_result["prediction"] == "ANOMALY":
        risk_level = "HIGH"
        recommended_action = "BLOCK_IP"
    else:
        risk_level = "LOW"
        recommended_action = "MONITOR"

    alert_id = (
        f"APNG-{datetime.now(timezone.utc):%Y%m%d%H%M%S}-"
        f"{uuid4().hex[:6]}"
    )

    alert = Alert(
        alert_id=alert_id,
        detected_at=datetime.now(timezone.utc),
        source_ip=data.source_ip,
        asset_name=data.asset_name or data.sensor,
        anomaly_score=ml_result["anomaly_score"],
        anomaly_model="isolation_forest_v1",
        ioc_matched=ioc_matched,
        ioc_type=ioc_type,
        shared_by=shared_by,
        llm_explanation=data.details,
        risk_level=risk_level,
        recommended_action=recommended_action,
        status="PENDING_CONFIRMATION",
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return {
        "alert_id": alert.alert_id,
        "detected_at": alert.detected_at,
        "source": {
            "ip": alert.source_ip,
            "asset_name": alert.asset_name,
        },
        "anomaly": {
            "score": alert.anomaly_score,
            "model": alert.anomaly_model,
        },
        "ioc_match": {
            "matched": alert.ioc_matched,
            "type": alert.ioc_type,
            "shared_by": alert.shared_by,
        },
        "llm_explanation": alert.llm_explanation,
        "risk_level": alert.risk_level,
        "recommended_action": alert.recommended_action,
        "status": alert.status,
    }