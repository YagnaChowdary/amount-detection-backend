# Amount Detection Service (Problem Statement 4)

This project implements **Problem Statement 4: AI-Powered Amount Detection in Medical Documents** from the provided assignment. It provides a simple backend that extracts monetary amounts from text (and optionally images via OCR) and classifies them by context (total, paid, due, discount, percent, unknown).

## Features
- Accepts **text** input (JSON) or **image** upload (multipart/form-data).
- Extracts numeric tokens and normalizes common OCR digit mistakes.
- Classifies amounts by nearby keywords (heuristic-based).
- Produces structured JSON with provenance fields and confidence score.

## Files
- `app.py` - Flask app exposing the API endpoints
- `extractor.py` - extraction and normalization logic
- `requirements.txt` - Python dependencies
- `sample_requests.sh` - example curl requests
- `README.md` - this file

## Quick Start (local)
1. Create virtualenv and install:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. Run the server:
```bash
python app.py
```
3. Health check:
```bash
curl http://localhost:5000/api/health
```

## Example - text input
```bash
curl -X POST http://localhost:5000/api/extract -H "Content-Type: application/json" -d '{"text":"Total: INR 1200 | Paid: 1000 | Due: 200 | Discount: 10%"}'
```

## Example - image input (optional OCR)
Requires `pytesseract` and `Pillow` to be installed and `tesseract` binary accessible.
```bash
curl -X POST -F "image=@/path/to/bill.jpg" http://localhost:5000/api/extract
```

## Notes & Guardrails
- This implementation uses regex and heuristics; it is not a replacement for production OCR+NLP pipelines.
- If OCR is needed, install `pytesseract` and the Tesseract engine separately.
- The service defaults to `INR` when currency is not detected, as per assignment domain.

## License
MIT
