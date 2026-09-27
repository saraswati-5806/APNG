# Place this inside backend/api/routes_llm.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from llm_engine.ollama_client import generate_guidance

router = APIRouter(prefix="/api/llm", tags=["LLM Security Engine"])

class LLMRequest(BaseModel):
    alert_context: str
    log_excerpt: str

@router.post("/analyze")
async def analyze_security_alert(payload: LLMRequest):
    """
    Calls Member 4's local Ollama client to generate AI threat analysis and remediation guidance.
    """
    try:
        guidance = generate_guidance(payload.alert_context, payload.log_excerpt)
        return {
            "status": "success",
            "ai_guidance": guidance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))