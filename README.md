

**Amount Detection Service — AI-based Medical Document Parser**

This project implements an **AI-powered Amount Detection Backend** that extracts **billing amounts, totals, dues, percentages, discounts, and monetary values** from **text or medical bill images**.
It fulfills **Problem Statement 4: Amount Extraction in Medical Documents**.

The backend is built using **Python + Flask**, supports both **raw text** and **OCR-based image extraction**, and returns **structured JSON**.

---

# 🚀 Features

* Extracts amounts such as:

  * Total Bill
  * Paid Amount
  * Due / Pending Amount
  * Discounts
  * Percentages
* OCR support for image inputs (Tesseract inside Docker)
* Cleans OCR mistakes:

  * `O → 0`, `l → 1`, `S → 5`, etc.
* Currency inference (₹, INR, USD, etc.)
* JSON output with:

  * Raw tokens
  * Normalized values
  * Classified types
  * Confidence score
  * Source provenance
* REST API with `/api/extract` and `/api/health`

---

# 📂 Project Structure

```
amount_detection_service/
│── app.py
│── extractor.py
│── requirements.txt
│── Dockerfile
│── docker-compose.yml
│── sample_requests.sh
│── README.md
```

---

# 🛠️ Installation (Local)

## 1️⃣ Create Virtual Environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/Mac:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

> OCR is optional — if you want image extraction, install Tesseract:

* Ubuntu: `sudo apt install tesseract-ocr`
* Mac: `brew install tesseract`
* Windows: install from: [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

---

## 3️⃣ Start the Server

```bash
python app.py
```

Server runs on:

```
http://localhost:5000
```

---

# 🌐 API Endpoints

## ✔️ **Health Check**

```
GET /api/health
```

Response:

```json
{
  "status": "ok",
  "service": "amount-detection",
  "tz": "Asia/Kolkata"
}
```

---

## ✔️ **Extract Amounts (Text Input)**

### Request:

```
POST /api/extract
Content-Type: application/json
```

Body:

```json
{
  "text": "Total INR 1200 Paid 1000 Due 200 Discount 10%"
}
```

### Response:

```json
{
  "status": "ok",
  "currency_hint": "INR",
  "raw_tokens": ["INR 1200", "1000", "200", "10%"],
  "normalized_amounts": [1200, 1000, 200],
  "amounts": [
    {"type":"total_bill","value":1200,"source":"text: 'INR 1200'"},
    {"type":"paid","value":1000,"source":"text: '1000'"},
    {"type":"due","value":200,"source":"text: '200'"},
    {"type":"percent","value":"10%","source":"text: '10%'"}
  ],
  "confidence": 0.75
}
```

---

## ✔️ **Extract Amounts (Image OCR)**

Requires Tesseract installed OR use Docker image.

```
POST /api/extract
Form-Data:
  image: <file>
```

```bash
curl -X POST -F "image=@bill.jpg" http://localhost:5000/api/extract
```

---

# 🐳 Docker Guide (Recommended)

Docker image includes Tesseract OCR, so **image extraction works automatically**.

## 1️⃣ Build Docker Image

```bash
docker build -t amount-service .
```

## 2️⃣ Run Container

```bash
docker run -p 5000:5000 amount-service
```

Now API runs at:

```
http://localhost:5000
```

---

# 🐳 Docker Compose (Alternative)

```bash
docker-compose up --build
```

---

# 🧪 Sample cURL Requests

### Text:

```bash
curl -X POST http://localhost:5000/api/extract \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Total INR 1500 Paid 500 Due 1000 Discount 5%\"}"
```

### Image:

```bash
curl -X POST -F "image=@/path/to/bill.jpg" http://localhost:5000/api/extract
```

---

# 🧠 How Amount Classification Works

The system detects numbers using regex + OCR cleanup.
Then finds context using nearby words:

| Keyword               | Type         |
| --------------------- | ------------ |
| total, amount, net    | `total_bill` |
| paid, received        | `paid`       |
| due, balance, pending | `due`        |
| discount, disc        | `discount`   |
| % or percent          | `percent`    |

If no match → `unknown`.

---

# 📌 Notes

* Default currency is **INR** (can be changed in code).
* Designed for **medical bills, invoices, prescriptions**.
* Not a replacement for production OCR/NLP models.
* Works fully without OCR when using pure text input.

---

# 📜 License

MIT License — free for commercial use, modification, and distribution.

---
