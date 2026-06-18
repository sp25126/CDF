# Shiksha Sahayak (AI Teaching Assistant)

MVP for Haryana Government Schools.

## Setup
- **Backend:** `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`
- **Frontend:** `cd frontend && npm install && npm run dev`

## Features
1. Live Concept Simplification
2. Voice-Triggered Quizzing

## Memory System Testing

The memory system tracks session state and learns long-term user preferences to improve context-aware responses. To verify the memory logic and prompt assembly, run the following test scripts from the backend directory:

```bash
cd backend
.\venv\Scripts\python.exe tests\test_memory.py
.\venv\Scripts\python.exe tests\test_prompt_assembly.py
```

