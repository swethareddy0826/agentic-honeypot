from fastapi import FastAPI, Header, HTTPException, Request
from scam_detector import is_scam, get_suspicious_words
from extractor import extract_info
from agent import generate_reply
import requests

API_KEY = "honeypot2026"
app = FastAPI()

sessions = {}

@app.post("/detect-scam")
async def detect_scam(request: Request, x_api_key: str = Header(None)):

    # 🔐 API KEY CHECK
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # 🟢 READ RAW JSON SAFELY
    try:
        data = await request.json()
    except:
        data = None

    # 🟢 HANDLE ALL POSSIBLE INPUT TYPES

    # 1) Empty body (tester)
    if not data:
        session_id = "tester-session"
        message_text = "test message"

    # 2) Simple body { "message": "text" }
    elif "message" in data and isinstance(data["message"], str):
        session_id = "tester-session"
        message_text = data["message"]

    # 3) Hackathon structured body
    else:
        session_id = data.get("sessionId", "unknown-session")
        message_text = data["message"]["text"]

    # 🧠 STORE SESSION MEMORY
    if session_id not in sessions:
        sessions[session_id] = []

    sessions[session_id].append(message_text)
    total_messages = len(sessions[session_id])

    # 🔍 SCAM CHECK
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

        try:
            requests.post(
                "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
                json=payload,
                timeout=5
            )
        except:
            pass

        return {
            "status": "success",
            "reply": reply
        }

    return {
        "status": "success",
        "reply": "Hello, how can I help you?"
    }
