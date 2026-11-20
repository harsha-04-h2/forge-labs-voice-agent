# context.md — Harsha's Clone Voice AI Agent

## Project Overview
An AI voice agent that sounds exactly like Harsha and handles all inbound calls for Forge Labs AI.
Callers think they're talking to Harsha. The agent qualifies them, answers questions about Forge Labs,
collects their details, and signs off — all in Harsha's cloned voice.

---

## Stack
- **STT** — Deepgram (nova-3)
- **LLM** — Gemini 2.5 Flash (`gemini-2.5-flash`)
- **TTS** — ElevenLabs (Harsha's cloned voice)
- **Voice Activity Detection** — Silero VAD
- **Agent Framework** — LiveKit Agents (Python SDK)
- **Call Routing** — LiveKit Cloud + SIP Trunk (Twilio/Vonage)
- **Backend** — Python + FastAPI
- **Deployment** — Railway / Render

---

## What the Agent Does
1. Picks up inbound calls routed via SIP → LiveKit room
2. Greets the caller in Harsha's voice
3. Asks what brought them to Forge Labs
4. Answers questions about Forge Labs AI services
5. Collects caller's name + WhatsApp number
6. Signs off and ends the call cleanly
7. Webhook to n8n for lead capture → CRM

---

## Forge Labs AI — Context for the Agent
- AI systems engineering and automation agency based in Bangalore, India
- Builds: AI voice agents, n8n + LangGraph pipelines, agentic workflows, WhatsApp/CRM automation, AI marketing systems
- Founder: Harsha
- Target clients: Businesses that want real AI implementation

---

## Agent Persona
- Speaks as Harsha — confident, direct, founder-first
- No corporate filler ("Great question!", "Absolutely!")
- Short responses — phone call, not an email
- Never quotes pricing or timelines
- Never promises deliverables
- Collects name + WhatsApp before every sign-off

---

## What Done Looks Like
- Agent picks up real phone calls
- Caller cannot tell it's an AI
- Every lead's name + WhatsApp is captured
- Harsha gets notified and follows up manually

---

## Files
| File | Purpose |
|------|---------|
| `agent.py` | Main LiveKit agent worker — STT → LLM → TTS pipeline |
| `prompts.py` | System prompt + persona + greeting |
| `server.py` | FastAPI sidecar — health check + lead endpoint |
| `context.md` | This file — project reference |
| `.env.example` | Template for required API keys |
| `requirements.txt` | Python dependencies |
| `Procfile` | Railway / Render process definitions |
| `runtime.txt` | Python version pin |

---

## Keys Needed
| Variable | Purpose |
|----------|---------|
| `LIVEKIT_URL` | wss://your-project.livekit.cloud |
| `LIVEKIT_API_KEY` | LiveKit Cloud API key |
| `LIVEKIT_API_SECRET` | LiveKit Cloud API secret |
| `DEEPGRAM_API_KEY` | Deepgram STT |
| `ELEVENLABS_API_KEY` | ElevenLabs TTS |
| `ELEVENLABS_VOICE_ID` | Harsha's cloned voice ID |
| `GEMINI_API_KEY` | Google Gemini LLM |
| `LEAD_WEBHOOK_URL` | (Optional) n8n webhook URL for lead capture |

---

## Setup & Run

### 1. Clone voice on ElevenLabs
1. Go to ElevenLabs → Voice Lab → Add Voice → Instant Voice Clone
2. Upload 2–5 minutes of clean Harsha audio (no background noise)
3. Copy the Voice ID → paste into `.env` as `ELEVENLABS_VOICE_ID`

### 2. Install dependencies
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Configure environment
```bash
copy .env.example .env
# Edit .env with your actual API keys
```

### 4. Download VAD model
```bash
python -c "from livekit.plugins import silero; silero.VAD.load()"
```

### 5. Run locally (dev mode)
```bash
python agent.py dev
```

### 6. Set up SIP trunk (Twilio)
1. Buy a phone number on Twilio
2. In LiveKit Cloud → SIP → Create Inbound Trunk → paste Twilio credentials
3. In Twilio → Voice webhook → point to your LiveKit SIP termination URI
4. Any call to the number now routes into a LiveKit room → agent picks up

### 7. Deploy to Railway
1. Push repo to GitHub
2. New Railway project → Deploy from GitHub
3. Add all env vars in Railway dashboard
4. Railway auto-detects `Procfile` and starts both `web` and `worker` processes

---

## Architecture

```
Caller
  │
  ▼
Twilio (SIP Trunk)
  │
  ▼
LiveKit Cloud (SIP → Room)
  │
  ▼
agent.py (LiveKit Worker)
  ├─ Silero VAD  ← detects speech start/end
  ├─ Deepgram nova-3  ← speech → text
  ├─ Gemini 2.5 Flash  ← text → response
  └─ ElevenLabs (Harsha voice)  ← text → audio
  │
  ▼
Lead captured → Webhook → n8n → CRM / WhatsApp notification
```

---

## Latency Targets
| Stage | Target |
|-------|--------|
| VAD → STT | < 300ms |
| STT → LLM first token | < 400ms |
| LLM → TTS first audio | < 300ms |
| **Total TTFW** | **< 1 second** |

ElevenLabs `eleven_turbo_v2_5` + Deepgram nova-3 streaming + Gemini Flash streaming keeps latency under 1s in practice.

---

## Lead Capture Flow
1. During call: agent scans for name ("my name is…") and phone pattern
2. On call end: `send_lead_to_webhook()` fires a POST to `LEAD_WEBHOOK_URL`
3. n8n receives lead → saves to Notion/Airtable/Sheets → sends Harsha a WhatsApp alert
4. Harsha follows up manually

---

## Roadmap
- [ ] Structured lead extraction via LLM tool call (more reliable than regex)
- [ ] Outbound calling (Harsha dials leads proactively)
- [ ] Multi-language support (Hindi, Kannada)
- [ ] Call recording + summary email after each call
- [ ] Dashboard to view all captured leads
