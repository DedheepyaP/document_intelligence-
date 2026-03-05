DocuChat — Document Intelligence System

Setup

1. Clone
git clone https://github.com/<your-username>/document-system.git
cd document-system

2. Copy and fill in environment variables
cp .env.example .env

3. Install backend dependencies
poetry install

4. Run database migrations
poetry run alembic upgrade head

Running

**Terminal 1 — Backend**

>> poetry run uvicorn main:app --reload


**Terminal 2 — Celery worker** (background file processing)

>> poetry run celery -A app.core.celery_app worker --loglevel=info


**Terminal 3 — Frontend**
bash
>> cd frontend
>> npm install
>> npm run dev


Open **http://localhost:5173**
