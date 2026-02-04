SCAM_WORDS = [
    "blocked","verify","urgent","click","otp",
    "refund","winner","lottery","suspend","account",
    "upi","pay","transfer"
]

def is_scam(message):
    msg = message.lower()
    for word in SCAM_WORDS:
        if word in msg:
            return True
    return False

def get_suspicious_words(message):
    found = []
    for w in SCAM_WORDS:
        if w in message.lower():
            found.append(w)
    return found
