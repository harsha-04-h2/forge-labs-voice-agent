"""
agent.py — Forge Labs AI Voice Agent (Harsha's Clone)
Built for livekit-agents 1.8+

Stack:
  STT  → Deepgram nova-3
  LLM  → Groq (openai/gpt-oss-120b) via LiveKit OpenAI plugin (ultra-low latency)
  TTS  → ElevenLabs (Harsha's cloned voice)
  VAD  → Silero
  Framework → LiveKit Agents Python SDK 1.8+

Run locally:
  python agent.py dev

Deploy:
  python agent.py start
"""

import asyncio
import os
import re
from typing import Optional

import httpx
from dotenv import load_dotenv
from loguru import logger

from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
    voice,
)
from livekit.plugins import deepgram, elevenlabs, openai, silero

from prompts import GREETING, SYSTEM_PROMPT

# ── Environment ──────────────────────────────────────────────────────────────
load_dotenv()

LIVEKIT_URL         = os.environ["LIVEKIT_URL"]
LIVEKIT_API_KEY     = os.environ["LIVEKIT_API_KEY"]
LIVEKIT_API_SECRET  = os.environ["LIVEKIT_API_SECRET"]
DEEPGRAM_API_KEY    = os.environ["DEEPGRAM_API_KEY"]
ELEVENLABS_API_KEY  = os.environ["ELEVENLABS_API_KEY"]
ELEVENLABS_VOICE_ID = os.environ["ELEVENLABS_VOICE_ID"]
GROQ_API_KEY        = os.environ.get("GROQ_API_KEY", "")
LEAD_WEBHOOK_URL    = os.getenv("LEAD_WEBHOOK_URL")  # optional


# ── Lead webhook ─────────────────────────────────────────────────────────────
async def send_lead_to_webhook(lead: dict) -> None:
    if not LEAD_WEBHOOK_URL:
        logger.info(f"[LEAD] Captured: {lead}")
        return
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(LEAD_WEBHOOK_URL, json=lead)
            resp.raise_for_status()
            logger.info(f"[LEAD] Webhook OK {resp.status_code}")
    except Exception as exc:
        logger.error(f"[LEAD] Webhook failed: {exc}")


# ── Lead tracker ─────────────────────────────────────────────────────────────
class LeadTracker:
    def __init__(self):
        self.name: Optional[str] = None
        self.whatsapp: Optional[str] = None

    def scan(self, text: str) -> None:
        if not self.whatsapp:
            phone = re.search(
                r"\b(?:\+91[\s\-]?)?[6-9]\d{9}\b|\+\d{1,3}[\s\-]?\d{6,14}",
                text,
            )
            if phone:
                self.whatsapp = phone.group().strip()
                logger.info(f"[LEAD] WhatsApp: {self.whatsapp}")

        if not self.name:
            name = re.search(
                r"(?:my name is|i'm|i am|this is)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)",
                text,
                re.IGNORECASE,
            )
            if name:
                self.name = name.group(1).strip()
                logger.info(f"[LEAD] Name: {self.name}")


# ── Agent definition ──────────────────────────────────────────────────────────
class HarshaAgent(voice.Agent):
    """Forge Labs inbound voice agent — speaks as Harsha's AI clone."""

    def __init__(self):
        super().__init__(instructions=SYSTEM_PROMPT)
        self._lead = LeadTracker()

    async def on_enter(self) -> None:
        """Called when the agent enters the session — greet the caller."""
        await self.session.say(GREETING)

    async def on_user_turn_completed(
        self,
        turn_ctx: llm.ChatContext,
        new_message: llm.ChatMessage,
    ) -> None:
        """Scan every user utterance for lead data."""
        text = new_message.text_content or ""
        if text:
            self._lead.scan(text)

    async def on_exit(self) -> None:
        """Fire webhook when the call ends."""
        lead = {
            "name": self._lead.name,
            "whatsapp": self._lead.whatsapp,
        }
        if self._lead.name or self._lead.whatsapp:
            await send_lead_to_webhook(lead)
        else:
            logger.warning("[LEAD] Call ended — no lead captured.")


# ── Entrypoint ────────────────────────────────────────────────────────────────
async def entrypoint(ctx: JobContext) -> None:
    logger.info(f"[AGENT] Job started — room: {ctx.room.name}")

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    session = voice.AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(
            model="nova-3",
            language="en-IN",
            api_key=DEEPGRAM_API_KEY,
        ),
        llm=openai.LLM(
            model="openai/gpt-oss-120b",
            base_url="https://api.groq.com/openai/v1",
            api_key=GROQ_API_KEY,
            temperature=0.7,
        ),
        tts=elevenlabs.TTS(
            voice_id=ELEVENLABS_VOICE_ID,
            api_key=ELEVENLABS_API_KEY,
            model="eleven_turbo_v2_5",
            voice_settings=elevenlabs.VoiceSettings(
                stability=0.45,
                similarity_boost=0.85,
                style=0.0,
                use_speaker_boost=True,
            ),
        ),
    )

    await session.start(
        agent=HarshaAgent(),
        room=ctx.room,
    )

    logger.info("[AGENT] Session started — waiting for caller.")


# ── Worker ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
