"""
server.py — Optional FastAPI sidecar

Endpoints:
  GET  /health        → liveness probe for Railway / Render
  POST /lead          → manual lead ingestion (e.g. from n8n testing)
  GET  /leads         → returns in-memory lead log (dev only)

Run alongside the agent worker:
  uvicorn server:app --host 0.0.0.0 --port 8080
"""

import os
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

app = FastAPI(
    title="Forge Labs AI Voice Agent — API",
    description="Sidecar server for health checks and lead management",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory lead store (replace with a DB / n8n webhook in production)
_leads: list[dict] = []


# ── Models ───────────────────────────────────────────────────

class Lead(BaseModel):
    name: Optional[str] = None
    whatsapp: Optional[str] = None
    room: Optional[str] = None
    collected: bool = False


# ── Routes ───────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "forge-labs-voice-agent"}


@app.post("/lead", status_code=201)
async def receive_lead(lead: Lead):
    """Receive a lead from the agent or n8n and store it."""
    record = lead.dict()
    record["received_at"] = datetime.now(timezone.utc).isoformat()
    _leads.append(record)
    return {"message": "Lead received", "lead": record}


@app.get("/leads")
async def list_leads():
    """Return all captured leads (dev/debug only — secure this in prod)."""
    return {"total": len(_leads), "leads": _leads}
