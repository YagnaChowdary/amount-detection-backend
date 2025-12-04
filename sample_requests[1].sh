#!/bin/bash
# Text request
echo "Text input example:"
curl -s -X POST http://localhost:5000/api/extract -H "Content-Type: application/json" -d '{"text":"Total: INR 1200 | Paid: 1000 | Due: 200 | Discount: 10%"}' | jq

# Image request (requires server running and tesseract installed)
# curl -s -X POST -F "image=@/path/to/bill.jpg" http://localhost:5000/api/extract | jq
