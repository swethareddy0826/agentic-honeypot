from fastapi import FastAPI, Header, HTTPException
from scam_detector import is_scam, get_suspicious_words
from extractor import extract_info
from agent import generate_reply
import requests

API_KEY = "honeypot2026"
app = FastAPI()

# store session memory
sessions = {}

@app.post("/detect-scam")
def detect_scam(data: dict, x_api_key: str = Header(None)):

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    session_id = data.get("sessionId")
    message_text = data["message"]["text"]

    history = data.get("conversationHistory", [])

    # store session messages
    if session_id not in sessions:
        sessions[session_id] = []

    sessions[session_id].append(message_text)
    total_messages = len(sessions[session_id])

    scam = is_scam(message_text)

    if scam:
        extracted = extract_info(message_text)
        suspicious_words = get_suspicious_words(message_text)
        reply = generate_reply()

        # Send mandatory callback
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
