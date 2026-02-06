from fastapi import FastAPI, Header, HTTPException, Request
from scam_detector import is_scam, get_suspicious_words
from extractor import extract_info
from agent import generate_reply
import requests
import threading

API_KEY = "honeypot2026"
app = FastAPI()

sessions = {}

# -------------------------
# Background callback
# -------------------------
def send_callback(payload):
    try:
        requests.post(
            "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
            json=payload,
            timeout=3
        )
    except:
        pass

# -------------------------
# Root health check
# -------------------------
@app.get("/")
def home():
    return {"status": "running"}

# -------------------------
# Honeypot endpoint
# -------------------------
@app.post("/detect-scam")
async def detect_scam(request: Request, x_api_key: str = Header(None)):

    # 🔐 API KEY CHECK
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # 🟢 Read raw JSON safely
    try:
        data = await request.json()
    except:
        data = None

    # 🟢 Handle all input types

    # Case 1: Empty body (tester)
    if not data:
        session_id = "tester-session"
        message_text = "test message"

    # Case 2: Simple body
    elif "message" in data and isinstance(data["message"], str):
        session_id = "tester-session"
        message_text = data["message"]

    # Case 3: Structured body
    else:
        session_id = data.get("sessionId", "unknown-session")
        message_text = data["message"]["text"]

    # 🧠 Store session
    if session_id not in sessions:
        sessions[session_id] = []

    sessions[session_id].append(message_text)
    total_messages = len(sessions[session_id])

    # 🔍 Scam detection
    scam = is_scam(message_text)

    if scam:
        extracted = extract_info(message_text)
        suspicious_words = get_suspicious_words(message_text)
        reply = generate_reply()

        payload = {
            "sessionId": session_id,
            "scamDetected": True,
            "totalMessagesExchanged": total_messages,
            "extractedIntelligence": {
                "bankAccounts": extracted["bank_accounts"],
                "upiIds": extracted["upi_ids"],
                "phishingLinks": extracted["phishing_links"],
                "phoneNumbers": extracted["phone_numbers"],
                "suspiciousKeywords": suspicious_words
            },
            "agentNotes": "Scammer using urgency and payment redirection"
        }

        # 🚀 Fire-and-forget callback
        threading.Thread(target=send_callback, args=(payload,)).start()

        return {
            "status": "success",
            "reply": reply
        }

    return {
        "status": "success",
        "reply": "Hello, how can I help you?"
    }
