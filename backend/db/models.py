from sqlalchemy import Column, String, Float, Boolean, DateTime
from sqlalchemy.sql import func

from db.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(String, primary_key=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())

    source_ip = Column(String, nullable=False)
    asset_name = Column(String, nullable=True)

    anomaly_score = Column(Float, nullable=True)
    anomaly_model = Column(String, nullable=True)

    ioc_matched = Column(Boolean, default=False)
    ioc_type = Column(String, nullable=True)
    shared_by = Column(String, nullable=True)

    llm_explanation = Column(String, nullable=True)

    risk_level = Column(String, nullable=False)
    recommended_action = Column(String, nullable=False)
    status = Column(String, nullable=False, default="PENDING_CONFIRMATION")


class IOC(Base):
    __tablename__ = "iocs"

    ioc_id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    confidence = Column(String, nullable=False)
    first_seen = Column(DateTime(timezone=True), nullable=False)
    shared_by_org_hash = Column(String, nullable=False)
    tlp = Column(String, nullable=False)

class RemediationAction(Base):
    __tablename__ = "remediation_actions"

    action_id = Column(String, primary_key=True)

    alert_id = Column(String, nullable=False)

    action_type = Column(String, nullable=False)

    status = Column(
        String,
        nullable=False,
        default="PENDING_CONFIRMATION"
    )

    confirmed_by = Column(String, nullable=True)

    confirmed_at = Column(DateTime(timezone=True), nullable=True)

    dry_run = Column(Boolean, nullable=False, default=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(String, primary_key=True)

    alert_id = Column(String, nullable=True)

    action_id = Column(String, nullable=True)

    event_type = Column(String, nullable=False)

    performed_by = Column(String, nullable=True)

    details = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )        
class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="admin")    