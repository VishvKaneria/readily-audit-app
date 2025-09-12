# 📑 Readily Audit App

A simple web app that helps healthcare organizations demonstrate compliance during audits.

The app extracts **audit questions** from a PDF and matches them with **policies & procedures (P&P) documents**, showing whether requirements are met along with supporting evidence.

---

## 📄 Deliverables

Live Demo: https://readily-audit-app.vercel.app

---

## 🚀 Features
- Upload **Audit Questions PDF** (list of compliance criteria).
- Extracts and displays questions in a structured list.
- For each question, shows:
  - Requirement met (Yes/No)
  - Policy reference & page
  - Supporting evidence text

---

## ⚙️ How It Works

1. Upload an Audit Questions PDF.
3. Backend extracts and processes text.
4. Each question is matched against policies.
5. Results are displayed in a compliance table.

---

## 🛠️ Tech Stack

- **Frontend**: React (Deployed on Vercel)
- **Backend**: Python (FastAPI)
- **Libraries**: `pymupdf`, `fastapi`, `python-multipart`, `uvicorn`, `numpy`, `sentence-transformers`

---

## 📦 Setup

### Backend
```bash
cd app
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
