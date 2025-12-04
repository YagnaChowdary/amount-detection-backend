import re
from typing import List, Dict, Any

# Optional OCR dependencies are imported only when needed to avoid hard failures
def _safe_import_pytesseract_pil():
    try:
        from PIL import Image
        import pytesseract
        return Image, pytesseract
    except Exception as e:
        return None, None

# Normalize common OCR digit errors (e.g., 'l' -> '1', 'O' -> '0', 'S'->'5')
_DIGIT_REPLACEMENTS = {
    'l': '1', 'I': '1', 'O': '0', 'o': '0', 'S': '5', 's': '5', 'B': '8', 'Z': '2', ',': '', '₹':'', 'Rs':'', 'Rs.':'', 'INR':''
}

CURRENCY_SYMBOLS = ['₹', 'Rs', 'INR', 'Rs.', 'USD', '$', '€', 'EUR']

_amount_regex = re.compile(r'(?:(?:₹|Rs(?:\.)?|INR|\$|USD|€|EUR)\s*)?[\d\.,]{1,15}(?:\s*%?)', flags=re.IGNORECASE)

def _clean_token(tok: str) -> str:
    # replace common OCR mistakes
    cleaned = tok
    for k, v in _DIGIT_REPLACEMENTS.items():
        cleaned = cleaned.replace(k, v)
    cleaned = cleaned.strip()
    # remove stray non-digit except dot and percent
    cleaned = re.sub(r"[^0-9\.\%]", "", cleaned)
    return cleaned

def extract_amounts_from_text(text: str) -> Dict[str, Any]:
    """
    Extract numeric tokens and classify them by surrounding keywords.
    Returns JSON structure matching the assignment spec.
    """
    if not text or not text.strip():
        return {"status":"no_amounts_found","reason":"empty_text"}
    raw_tokens = []
    for m in _amount_regex.finditer(text):
        token = m.group(0).strip()
        raw_tokens.append(token)
    currency_hint = None
    # infer currency
    for sym in CURRENCY_SYMBOLS:
        if sym in text:
            currency_hint = sym
            break
    if currency_hint is None:
        # default to INR as per problem domain
        currency_hint = "INR"
    # normalize tokens to numbers
    normalized = []
    for tok in raw_tokens:
        cleaned = _clean_token(tok)
        if cleaned.endswith('%'):
            # percentages are preserved separately
            normalized.append({"raw":tok, "normalized": cleaned, "is_percent": True})
        elif cleaned == "":
            continue
        else:
            # attempt to parse as int or float, handle commas
            try:
                if '.' in cleaned:
                    val = float(cleaned)
                else:
                    val = int(cleaned)
                normalized.append({"raw":tok, "normalized": val, "is_percent": False})
            except Exception:
                # try removing dots and parse
                digits = re.sub(r"\.", "", cleaned)
                try:
                    val = int(digits)
                    normalized.append({"raw":tok, "normalized": val, "is_percent": False})
                except Exception:
                    # skip unparsable token
                    continue
    if not normalized:
        return {"status":"no_amounts_found","reason":"document too noisy", "confidence": 0.0}
    # Classification heuristics by searching nearby words in original text
    amounts_out = []
    lowered = text.lower()
    for item in normalized:
        raw = item["raw"]
        val = item["normalized"]
        is_percent = item["is_percent"]
        src = f"text: '{raw}'"
        typ = "unknown"
        # find context window
        idx = lowered.find(raw.lower())
        window = lowered[max(0, idx-40): idx+len(raw)+40] if idx!=-1 else lowered
        if "total" in window or "bill" in window or "amount" in window or "net" in window:
            typ = "total_bill"
        elif "paid" in window or "received" in window or "paid:" in window:
            typ = "paid"
        elif "due" in window or "balance" in window or "outstanding" in window:
            typ = "due"
        elif is_percent or "%" in raw:
            typ = "percent"
        elif "discount" in window or "disc" in window:
            typ = "discount"
        else:
            # fallback using position: if first numeric near 'total' etc
            typ = "unknown"
        amounts_out.append({"type": typ, "value": val, "source": src})
    # compute a simple confidence
    confidence = 0.75 if normalized else 0.0
    return {"raw_tokens": [t for t in raw_tokens], "currency_hint": currency_hint, "normalized_amounts": [i["normalized"] for i in normalized if not i["is_percent"]], "amounts": amounts_out, "confidence": round(confidence,2), "status":"ok"}

def extract_amounts_from_image(file_storage) -> Dict[str, Any]:
    Image, pytesseract = _safe_import_pytesseract_pil()
    if Image is None or pytesseract is None:
        raise RuntimeError("pytesseract or PIL not available")
    # read image from file_storage (Flask FileStorage)
    img = Image.open(file_storage.stream)
    text = pytesseract.image_to_string(img)
    return extract_amounts_from_text(text)
