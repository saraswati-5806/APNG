from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.auth import get_current_user
from db.database import SessionLocal
from db.models import Alert, RemediationAction, AuditLog, User


router = APIRouter(
    prefix="/api/remediate",
    tags=["Remediation"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RemediationCreate(BaseModel):
    alert_id: str
    action_type: str


class RemediationConfirm(BaseModel):
    confirmed_by: str


# -------------------------------------------------
# STEP 1: Create pending remediation
# -------------------------------------------------
@router.post("/")
def create_remediation(
    remediation: RemediationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = (
        db.query(Alert)
        .filter(Alert.alert_id == remediation.alert_id)
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    # Do not create a second pending action
    action = (
        db.query(RemediationAction)
        .filter(
            RemediationAction.alert_id == remediation.alert_id,
            RemediationAction.status == "PENDING_CONFIRMATION"
        )
        .first()
    )

    if action:
        return {
            "message": "Human confirmation required",
            "action_id": action.action_id,
            "alert_id": action.alert_id,
            "action_type": action.action_type,
            "requires_confirmation": True,
            "status": action.status,
            "dry_run": action.dry_run
        }

    action = RemediationAction(
        action_id=f"REM-{remediation.alert_id}",
        alert_id=remediation.alert_id,
        action_type=remediation.action_type,
        status="PENDING_CONFIRMATION",
        dry_run=True
    )

    db.add(action)

    try:
        db.commit()
        db.refresh(action)
    except Exception:
        db.rollback()
        raise

    return {
        "message": "Human confirmation required",
        "action_id": action.action_id,
        "alert_id": action.alert_id,
        "action_type": action.action_type,
        "requires_confirmation": True,
        "status": action.status,
        "dry_run": action.dry_run
    }


# -------------------------------------------------
# STEP 2: Human confirms existing action
# -------------------------------------------------
@router.post("/{action_id}/confirm")
def confirm_remediation(
    action_id: str,
    confirmation: RemediationConfirm,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    action = (
        db.query(RemediationAction)
        .filter(
            RemediationAction.action_id == action_id,
            RemediationAction.status == "PENDING_CONFIRMATION"
        )
        .first()
    )

    if not action:
        raise HTTPException(
            status_code=404,
            detail="Pending remediation action not found"
        )

    alert = (
        db.query(Alert)
        .filter(Alert.alert_id == action.alert_id)
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    # Human confirmation
    action.status = "CONFIRMED"
    action.confirmed_by = confirmation.confirmed_by
    action.confirmed_at = datetime.now(timezone.utc)

    # Mandatory demo safety rule
    action.dry_run = True

    # Update alert status
    alert.status = "REMEDIATION_CONFIRMED"

    # Audit entry
    audit = AuditLog(
        log_id=f"LOG-{action.action_id}",
        alert_id=alert.alert_id,
        action_id=action.action_id,
        event_type="REMEDIATION_CONFIRMED",
        performed_by=confirmation.confirmed_by,
        details=(
            f"Remediation action {action.action_type} "
            f"confirmed in dry-run mode"
        )
    )

    db.add(audit)

    try:
        db.commit()
        db.refresh(action)
        db.refresh(audit)
    except Exception:
        db.rollback()
        raise

    return {
        "message": "Remediation confirmed",
        "action_id": action.action_id,
        "alert_id": action.alert_id,
        "action_type": action.action_type,
        "status": action.status,
        "confirmed_by": action.confirmed_by,
        "dry_run": action.dry_run,
        "audit_log_id": audit.log_id
    }