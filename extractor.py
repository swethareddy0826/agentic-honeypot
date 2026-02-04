import re

def extract_info(text):
    bank = re.findall(r"\b\d{9,18}\b", text)
    upi = re.findall(r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}", text)
    links = re.findall(r"https?://\S+", text)
    phones = re.findall(r"\+91\d{10}", text)

    return {
        "bank_accounts": bank,
        "upi_ids": upi,
        "phishing_links": links,
        "phone_numbers": phones
    }
