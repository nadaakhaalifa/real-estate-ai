# 🏢 Real Estate Data Engine
### Schema-Agnostic Excel Ingestion & Analysis Platform

---

## 🚀 Overview

This project is a production-style system designed to ingest, clean, and analyze inconsistent real estate Excel files from multiple developers.

Instead of relying on fixed schemas, the system uses:

- Dynamic column detection
- Pattern-based value extraction
- Heuristic-driven classification

to transform messy Excel data into structured, reliable insights.

---

## 🎯 Problem

Real estate Excel sheets are:

- Inconsistent across developers
- Poorly structured
- Filled with mixed formats like:
  - 3B, 2 BR, Typical-3B
  - Family Home with Penthouse
- Not machine-friendly

---

## ✅ Solution

This system:

- Automatically detects column meanings
- Extracts structured data (price, area, bedrooms, unit type)
- Handles messy real-world formats
- Produces clean summaries and reports

---

## 🧠 Core Features

### 🔍 Dynamic Column Detection
- No fixed schema required
- Detects columns using header names and sample values

### 🧩 Smart Value Extraction
Handles patterns like:
- Typical-3B → 3 Bedrooms
- Garden 2B → 2 Bedrooms
- 3 BR → 3 Bedrooms

### 🏷️ Intelligent Unit Classification
Correctly identifies:

- Bedrooms (1, 2, 3, etc.)
- Unit types:
  - Villa
  - Penthouse
  - Chalet
  - Studio
  - Duplex
  - Town House

Even when the "Unit Type" column is incorrect.

### 🛡️ Data Cleaning
Prevents errors like:

- Prices being parsed as bedrooms
- "Apartment" overriding actual types (e.g., Penthouse)
- Missing values breaking grouping

---

## 🌐 Live Platform

👉 https://real-estate-frontend-production-5ff2.up.railway.app/

---

## 🏗️ Architecture

```
Excel Upload
   ↓
Header Detection
   ↓
Column Detection
   ↓
Value Parsing (price / bedrooms / area)
   ↓
Unit Classification
   ↓
Database Storage
   ↓
Summary Builder
   ↓
Export (Excel / PDF)
```

---

## 🛠️ Tech Stack

**Backend**
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pandas
- OpenPyXL
- ReportLab

**Frontend**
- React
- Vite
- Tailwind CSS

---

## 📂 Project Structure

```
backend/
├── routes/
│   ├── upload.py
│   ├── summary.py
│   └── search.py
├── services/
│   ├── column_detector.py
│   ├── value_parser.py
│   ├── summary_builder.py
│   ├── excel_generator.py
│   └── pdf_generator.py
├── models.py
├── schemas.py
├── database.py
└── main.py

frontend/
├── src/
├── components/
└── pages/

sample_data/
```

---

## ⚙️ Setup & Run Locally

### 1. Clone Repository

```bash
git clone git clone https://github.com/nadaakhaalifa/real-estate-ai.git
cd real-estate-ai
```

---

### 2. Backend Setup

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

---

### 3. Database Setup

Create `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/real_estate
```

Run migrations:

```bash
alembic upgrade head
```

---

### 4. Run Backend

```bash
uvicorn backend.main:app --reload --port 8000
```

Backend runs at:
http://127.0.0.1:8000

---

### 5. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:
http://localhost:5173

---

## 🧪 Test Data

Sample Excel files are included in:

```
sample_data/
```

---

## ▶️ How to Test

1. Run backend  
2. Run frontend  
3. Upload files from `sample_data/`  
4. Generate summary  

---

## 📤 Expected Behavior

The system will:

- Detect columns automatically
- Extract bedrooms from text
- Infer unit types (Villa, Penthouse, etc.)
- Normalize inconsistent data
- Generate a clean summary

---

## 💡 Design Principles

- No hardcoded mappings
- Works across multiple Excel formats
- Handles real-world messy data
- Focus on correctness and robustness

---

## 🚀 Future Improvements

- Machine learning-based classification
- NLP for better text understanding
- Real-time dashboard
- Data validation layer

---

## 📌 Summary

This project demonstrates:

- Real-world data engineering
- Backend system architecture
- Handling unstructured business data
- Building scalable parsing pipelines