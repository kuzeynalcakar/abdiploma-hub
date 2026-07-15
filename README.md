# ABDiploma Hub

**Free Alberta Diploma Exam Preparation**

A free practice platform for Alberta high school students. Students register,
pick a course (Mathematics 30-1 ships with curriculum-aligned questions),
take 10-question quizzes with properly rendered math (KaTeX), get instant
feedback with worked explanations and common mistakes, and track their
accuracy by topic.

## Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite (file `backend/albertaprep.db`)
- **Frontend:** React (Vite) + Tailwind CSS + KaTeX
- **Auth:** Session tokens (PBKDF2 password hashing, revocable bearer tokens)

## Requirements

- Python 3.12+
- Node.js 20+

## 1. Backend setup

```bash
cd backend
pip install -r requirements.txt

# Create the database tables (also applies additive migrations)
python -m app.database.init_db

# Seed Alberta courses and curriculum topics (idempotent)
python -m app.database.curriculum_seed

# Import the Math 30-1 question bank
python -m app.database.question_import ../questions.json/math30-1_questions_cleaned.json

# Start the API on http://127.0.0.1:8000
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Interactive API docs are served at `http://127.0.0.1:8000/docs`.

## 2. Frontend setup

```bash
cd frontend
npm install

# Start the dev server on http://localhost:5173
npm run dev
```

The Vite dev server proxies `/api` requests to the backend at
`http://127.0.0.1:8000`, so no CORS configuration is needed in development.

## 3. Use the platform

Open `http://localhost:5173`, create an account, and start practicing.

## Importing more questions

Question banks are JSON lists validated on import. See
`backend/app/database/import_questions.json.example` for the expected format.
All three Alberta formats are accepted (`multiple_choice`,
`numerical_response`, `written_response`); quizzes currently serve multiple
choice.

```bash
cd backend
python -m app.database.question_import path/to/questions.json
```

## Production build

```bash
cd frontend
npm run build   # outputs static files to frontend/dist
```

Serve `frontend/dist` from any static host and run the FastAPI app behind a
reverse proxy that forwards `/api` to it. Set `DATABASE_URL` in
`backend/.env` to point at a production database if you outgrow SQLite.
