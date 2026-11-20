# Forge Labs AI — Voice Agent (Clone Voice)

An ultra-low-latency inbound AI voice agent built for **Forge Labs AI**, powered by LiveKit Agents, Deepgram nova-3, Groq (Llama 3.3 / GPT-OSS), and ElevenLabs voice cloning.

---

## ⚡ Architecture & Stack

- **STT (Speech-to-Text):** [Deepgram](https://deepgram.com/) (`nova-3`, Indian English tuned)
- **LLM (Intelligence):** [Groq](https://groq.com/) (`openai/gpt-oss-120b`, <200ms TTFT)
- **TTS (Voice Synthesis):** [ElevenLabs](https://elevenlabs.io/) (`eleven_turbo_v2_5`, Instant Voice Clone)
- **VAD (Voice Activity Detection):** Silero VAD
- **Agent Framework:** [LiveKit Agents Python SDK](https://docs.livekit.io/agents/) (v1.8+)
- **Telephony & Transport:** LiveKit Cloud + SIP Trunking (Twilio/Vonage)
- **Backend API Sidecar:** FastAPI + Uvicorn

---

## 📁 Project Structure

```
├── agent.py            # Main LiveKit voice agent worker & event loop
├── prompts.py          # System prompt, Harsha persona & knowledgebase injection
├── knowledgebase.md    # Forge Labs business context, FAQs & call handling rules
├── server.py           # Optional FastAPI sidecar (healthcheck & lead endpoint)
├── requirements.txt    # Python dependencies
├── Procfile            # Deployment spec for Railway / Render
├── runtime.txt         # Python runtime version
├── .env.example        # Environment variable template
└── .gitignore          # Git exclusion rules
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd "ai voice agent with my voice clone"
```

### 2. Create virtual environment & install dependencies
```bash
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
```

### 3. Configure environment variables
Copy `.env.example` to `.env` and fill in your API keys:
```bash
copy .env.example .env      # Windows
# cp .env.example .env      # macOS / Linux
```

Required keys:
- `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`
- `DEEPGRAM_API_KEY`
- `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`
- `GROQ_API_KEY`

### 4. Run the Agent locally (Dev Mode)
```bash
python agent.py dev
```

### 5. Test the Agent
- Connect using the [LiveKit Agents Playground](https://agents-playground.livekit.io/) or the [LiveKit Cloud Console](https://cloud.livekit.io/).
- Or dial into your LiveKit SIP inbound phone number directly.

---

## 📄 License
MIT
