
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.models import IOC, User
from core.auth import get_current_user


router = APIRouter(
    prefix="/api/ioc",
    tags=["IOC"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class IOCCreate(BaseModel):
    ioc_id: str
    type: str
    value: str
    confidence: str
    first_seen: datetime
    shared_by_org_hash: str
    tlp: str


class IOCSyncRequest(BaseModel):
    source: str
    iocs: list[IOCCreate]


@router.get("/")
def get_iocs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    iocs = db.query(IOC).all()

    return [
        {
            "ioc_id": ioc.ioc_id,
            "type": ioc.type,
            "value": ioc.value,
            "confidence": ioc.confidence,
            "first_seen": ioc.first_seen,
            "shared_by_org_hash": ioc.shared_by_org_hash,
            "tlp": ioc.tlp
        }
        for ioc in iocs
    ]


@router.post("/")
def create_ioc(
    ioc_data: IOCCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    existing_ioc = (
        db.query(IOC)
        .filter(IOC.ioc_id == ioc_data.ioc_id)
        .first()
    )

    if existing_ioc:
        return {
            "message": "IOC already exists",
            "ioc_id": existing_ioc.ioc_id
        }

    ioc = IOC(
        ioc_id=ioc_data.ioc_id,
        type=ioc_data.type,
        value=ioc_data.value,
        confidence=ioc_data.confidence,
        first_seen=ioc_data.first_seen,
        shared_by_org_hash=ioc_data.shared_by_org_hash,
        tlp=ioc_data.tlp
    )

    db.add(ioc)
    db.commit()
    db.refresh(ioc)

    return {
        "message": "IOC created successfully",
        "ioc_id": ioc.ioc_id
    }


@router.post("/sync")
def sync_iocs(
    sync_data: IOCSyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    added = 0
    skipped = 0

    for ioc_data in sync_data.iocs:

        existing_ioc = (
            db.query(IOC)
            .filter(IOC.ioc_id == ioc_data.ioc_id)
            .first()
        )

        if existing_ioc:
            skipped += 1
            continue

        ioc = IOC(
            ioc_id=ioc_data.ioc_id,
            type=ioc_data.type,
            value=ioc_data.value,
            confidence=ioc_data.confidence,
            first_seen=ioc_data.first_seen,
            shared_by_org_hash=ioc_data.shared_by_org_hash,
            tlp=ioc_data.tlp
        )

        db.add(ioc)
        added += 1

    db.commit()

    return {
        "message": "IOC synchronization completed",
        "status": "success",
        "source": sync_data.source,
        "added": added,
        "skipped": skipped,
        "total_received": len(sync_data.iocs)
    }

