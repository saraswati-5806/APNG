from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.models import Alert, RemediationAction, AuditLog


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
    confirmed_by: str | None = None


@router.post("/")
def create_remediation(
    remediation: RemediationCreate,
    db: Session = Depends(get_db)
):

    # Check whether the alert exists
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

    # -------------------------------------------------
    # STEP 1: No human confirmation yet
    # -------------------------------------------------
    if not remediation.confirmed_by:

        action = (
            db.query(RemediationAction)
            .filter(
                RemediationAction.alert_id == remediation.alert_id,
                RemediationAction.status == "PENDING_CONFIRMATION"
            )
            .first()
        )

        # If pending action already exists, return it
        if action:
            return {
                "message": "Human confirmation required",
                "action_id": action.action_id,
                "alert_id": action.alert_id,
                "action_type": action.action_type,
                "status": action.status,
                "dry_run": action.dry_run
            }

        # Create new pending action
        action = RemediationAction(
            action_id=f"REM-{remediation.alert_id}",
            alert_id=remediation.alert_id,
            action_type=remediation.action_type,
            status="PENDING_CONFIRMATION",
            dry_run=True
        )

        db.add(action)
        db.commit()
        db.refresh(action)

        return {
            "message": "Human confirmation required",
            "action_id": action.action_id,
            "alert_id": action.alert_id,
            "action_type": action.action_type,
            "status": action.status,
            "dry_run": action.dry_run
        }

    # -------------------------------------------------
    # STEP 2: Human confirmation received
    # -------------------------------------------------

    action = (
        db.query(RemediationAction)
        .filter(
            RemediationAction.alert_id == remediation.alert_id,
            RemediationAction.status == "PENDING_CONFIRMATION"
        )
        .first()
    )

    if not action:
        raise HTTPException(
            status_code=404,
            detail="Pending remediation action not found"
        )

    # Update existing action instead of creating duplicate
    action.status = "CONFIRMED"
    action.confirmed_by = remediation.confirmed_by
    action.confirmed_at = datetime.utcnow()
    action.dry_run = True

    # Update related alert
    alert.status = "REMEDIATION_CONFIRMED"

    # -------------------------------------------------
    # STEP 3: Create audit log
    # -------------------------------------------------

    audit = AuditLog(
        log_id=f"LOG-{action.action_id}",
        alert_id=alert.alert_id,
        action_id=action.action_id,
        event_type="REMEDIATION_CONFIRMED",
        performed_by=remediation.confirmed_by,
        details=(
            f"Remediation action {action.action_type} "
            f"confirmed in dry-run mode"
        )
    )

    db.add(audit)

    db.commit()
    db.refresh(action)
    db.refresh(audit)

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