from pydantic import BaseModel

class IoCSchema(BaseModel):
    ioc_id: str
    type: str  # ip | file_hash | url
    value: str
    confidence: str  # HIGH | MEDIUM | LOW
    first_seen: str
    shared_by_org_hash: str
    tlp: str  # RED | AMBER | GREEN | CLEAR