from flask import Flask, request, jsonify
from extractor import extract_amounts_from_text, extract_amounts_from_image
import werkzeug

app = Flask(__name__)

@app.route("/api/extract", methods=["POST"])
def extract():
    """
    Accepts either JSON with {"text": "..."} or multipart/form-data with file field "image".
    Returns structured JSON with currency hint, amounts, provenance, and status.
    """
    # Prefer text in JSON body
    if request.is_json:
        data = request.get_json()
        text = data.get("text")
        if not text:
            return jsonify({"error":"JSON must include 'text' field"}), 400
        result = extract_amounts_from_text(text)
        return jsonify(result)
    # Otherwise check for uploaded image
    if 'image' in request.files:
        image = request.files['image']
        try:
            result = extract_amounts_from_image(image)
            return jsonify(result)
        except RuntimeError as e:
            return jsonify({"error": str(e), "hint": "Install pytesseract and Pillow to enable image OCR."}), 500
    return jsonify({"error":"Send JSON with 'text' or upload an 'image' file."}), 400

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status":"ok","service":"amount-detection","tz":"Asia/Kolkata"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
