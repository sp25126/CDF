# Phase 1 Backend Testing Guide

This guide provides terminal-first tests for the CDF classroom assistant Phase 1 core using cURL.

## Quick Start

### 1. Start the backend server

```bash
cd backend
pip install -r requirements.txt
python -m app.main
# or: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will run on `http://localhost:8000`

---

## Health Check

Verify the backend is running:

```bash
curl -s http://localhost:8000/health | python -m json.tool
```

**Expected output:**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

---

## Test 1: Explain Mode (Default Hinglish)

Request a simple explanation:

```bash
curl -s -X POST http://localhost:8000/api/command/text \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo_session_1",
    "text": "Explain photosynthesis for class 6"
  }' | python -m json.tool
```

**Expected output:**
- `mode`: "explain"
- `language_mode`: "hinglish"
- `answer_text`: Contains explanation
- `confidence`: 0.85 (high confidence)
- `requires_clarification`: false
- `avatar_state`: "speaking"
- `next_actions`: Non-empty list

---

## Test 2: Quiz Mode

Request a quiz:

```bash
curl -s -X POST http://localhost:8000/api/command/text \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo_session_1",
    "text": "Quiz me on fractions"
  }' | python -m json.tool
```

**Expected output:**
- `mode`: "quiz"
- `quiz.total_questions`: 1 or more
- `quiz.questions[0].question`: Question text
- `quiz.questions[0].options`: Array of 3+ options
- `quiz.questions[0].correct_index`: 0-2 (or more)
- `quiz.questions[0].explanation`: Explanation text
- `answer_text`: Quiz intro message

---

## Test 3: English Language Request

Request explanation explicitly in English:

```bash
curl -s -X POST http://localhost:8000/api/command/text \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo_session_1",
    "text": "Explain gravity in English"
  }' | python -m json.tool
```

**Expected output:**
- `language_mode`: "english"
- `answer_text`: Full English explanation
- `confidence`: 0.95 (highest - explicit request)

---

## Test 4: Hindi Language Request

Request explanation in Hindi:

```bash
curl -s -X POST http://localhost:8000/api/command/text \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo_session_1",
    "text": "Explain in Hindi what is evaporation"
  }' | python -m json.tool
```

**Expected output:**
- `language_mode`: "hindi"
- `answer_text`: Full Hindi explanation
- `confidence`: 0.95

---

## Test 5: Unclear Command (Clarification)

Send an unclear command:

```bash
curl -s -X POST http://localhost:8000/api/command/text \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo_session_1",
    "text": "xyz abc 123"
  }' | python -m json.tool
```

**Expected output:**
- `mode`: "unclear"
- `requires_clarification`: true
- `answer_text`: Clarification message
- `next_actions`: Suggestions like ["Explain Photosynthesis", "Quiz on Gravity"]

---

## Test 6: Stop Command

Send a stop/pause command:

```bash
curl -s -X POST http://localhost:8000/api/command/text \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo_session_1",
    "text": "Stop"
  }' | python -m json.tool
```

**Expected output:**
- `mode`: "stop"
- `answer_text`: Stop confirmation message
- `avatar_state`: "idle"

---

## Test 7: Followup Command

Request a repeat/followup:

```bash
curl -s -X POST http://localhost:8000/api/command/text \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo_session_1",
    "text": "Repeat that slowly"
  }' | python -m json.tool
```

**Expected output:**
- `mode`: "followup"
- `answer_text`: Repeat message
- `avatar_state`: "speaking"

---

## Test 8: Mode Hint Override

Force a specific mode with `mode_hint`:

```bash
curl -s -X POST http://localhost:8000/api/command/text \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo_session_1",
    "text": "fractions",
    "mode_hint": "quiz"
  }' | python -m json.tool
```

**Expected output:**
- `mode`: "quiz" (forced by mode_hint)
- `confidence`: 1.0 (manual hint = highest confidence)

---

## Validation Checklist

After running the tests, verify:

### Response Schema ✓
- [ ] `session_id` matches request
- [ ] `mode` is one of: explain, quiz, followup, stop, unclear
- [ ] `language_mode` is one of: hinglish, english, hindi
- [ ] `confidence` is between 0.0 and 1.0
- [ ] `avatar_state` is one of: idle, speaking, listening, thinking
- [ ] `answer_text` is present (non-null)
- [ ] `next_actions` is an array (never null)
- [ ] `source_refs`, `visuals`, `videos` are arrays (never null)

### Intent Detection ✓
- [ ] "explain" keyword → mode: "explain"
- [ ] "quiz" keyword → mode: "quiz"
- [ ] "repeat", "again" → mode: "followup"
- [ ] "stop", "pause" → mode: "stop"
- [ ] Random text → mode: "unclear" with requires_clarification: true

### Language Detection ✓
- [ ] Default (no language request) → language_mode: "hinglish"
- [ ] "in English" / "English mein" → language_mode: "english"
- [ ] "in Hindi" / "Hindi mein" → language_mode: "hindi"
- [ ] Explicit request → confidence: 0.95
- [ ] Default → confidence: 0.8

### Mode Routing ✓
- [ ] Explain mode → answer_text has explanation
- [ ] Quiz mode → quiz payload with questions array
- [ ] Unclear mode → requires_clarification: true
- [ ] Stop mode → avatar_state: "idle"

### Clarification Fallback ✓
- [ ] Unclear command → answer_text in detected language
- [ ] next_actions → relevant suggestions
- [ ] No crashes on edge cases

### Quiz Payload Shape ✓
- [ ] quiz.title: string
- [ ] quiz.topic: string
- [ ] quiz.questions: array of QuizQuestion
- [ ] quiz.current_index: 0
- [ ] quiz.total_questions: > 0
- [ ] Each question has: question, options[], correct_index, explanation

---

## Common Issues

### Port Already in Use
```bash
# Kill the process on port 8000
lsof -i :8000
kill -9 <PID>
```

### Python Dependency Issues
```bash
# Reinstall requirements
pip install --force-reinstall -r requirements.txt
```

### JSON Parse Error
```bash
# Ensure you have Python installed for json.tool
python --version
```

### CORS Errors (Frontend)
Backend CORS is pre-configured. If issues persist:
```python
# Check app/core/config.py CORS_ORIGINS setting
```

---

## Quick Test Loop (Bash Script)

Create `test_backend.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"
SESSION_ID="test_$(date +%s)"

echo "🧪 Testing CDF Backend Phase 1"
echo "Session: $SESSION_ID"
echo ""

echo "1️⃣  Health Check..."
curl -s $BASE_URL/health | python -m json.tool | head -5
echo ""

echo "2️⃣  Explain Mode..."
curl -s -X POST $BASE_URL/api/command/text \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"text\":\"Explain photosynthesis\"}" \
  | python -m json.tool | grep -E '"mode"|"language_mode"|"confidence"'
echo ""

echo "3️⃣  Quiz Mode..."
curl -s -X POST $BASE_URL/api/command/text \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"text\":\"Quiz me on fractions\"}" \
  | python -m json.tool | grep -E '"mode"|"total_questions"'
echo ""

echo "4️⃣  English Language..."
curl -s -X POST $BASE_URL/api/command/text \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"text\":\"Explain in English\"}" \
  | python -m json.tool | grep '"language_mode"'
echo ""

echo "5️⃣  Clarification..."
curl -s -X POST $BASE_URL/api/command/text \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"text\":\"xyz abc 123\"}" \
  | python -m json.tool | grep '"requires_clarification"'
echo ""

echo "✅ Test complete!"
```

Run it:
```bash
chmod +x test_backend.sh
./test_backend.sh
```

---

## Notes

- All responses are JSON objects (never null arrays, use `[]` instead)
- Confidence scores reflect certainty (manual hint = 1.0, default = 0.8-0.9)
- The `transcript_text` field repeats the input for audit/debug purposes
- Future fields (`source_refs`, `visuals`, `videos`) are empty arrays for Phase 1
- `avatar_state` manages the visual indicator in the frontend
- All text is rendered as-is from the backend (no frontend rewriting)
