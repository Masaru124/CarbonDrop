# EcoBasket — Receipt OCR & Carbon Footprint (Free stack)

Backend: FastAPI + pytesseract + RapidFuzz + SQLite
Frontend: Vite + React + Chart.js

## Backend
1) Create venv and install deps:
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r backend/requirements.txt
```
2) Install **Tesseract OCR** engine:
- macOS: `brew install tesseract`
- Ubuntu/Debian: `sudo apt update && sudo apt install -y tesseract-ocr libtesseract-dev`
- Windows: installer from https://github.com/tesseract-ocr/tesseract/releases

3) Run backend:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend
```bash
cd frontend
npm install
npm run dev -- --host
```

## Quick OCR test (no frontend)
```bash
curl -F "file=@backend/sample_receipts/basic-receipt.png" http://localhost:8000/upload_receipt
```
