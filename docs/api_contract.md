# API Contract: Shiksha Sahayak (AI Teaching Assistant)

**Version:** 0.1.0-MVP  
**Base URL:** `http://localhost:8000/api/v1`

---

## Global Response Wrapper
All responses follow this standard structure:
```json
{
  "status": "success | error",
  "data": {},
  "error": {
    "code": "string",
    "message": "string"
  }
}
```

---

## 1. Health Check
Checks API and core service availability.

- **Path:** `/health`
- **Method:** `GET`
- **Response Example:**
```json
{
  "status": "success",
  "data": {
    "api": "healthy",
    "version": "0.1.0"
  }
}
```

---

## 2. Process Text Command
Primary endpoint for text-simulated voice inputs.

- **Path:** `/command/text`
- **Method:** `POST`
- **Request Schema:**
```json
{
  "text": "string",
  "session_id": "string",
  "context": {
    "grade_level": 7,
    "subject": "Science"
  }
}
```
- **Response Example (Intent: explain):**
```json
{
  "status": "success",
  "data": {
    "intent": "explain",
    "display": {
      "title": "Simplifying Photosynthesis",
      "primary_text": "Pedhon ki rasoi (Plants' kitchen).",
      "analogy": "Jaise ghar mein rasoi mein khana banta hai, waise hi patton mein dhoop aur pani se ped apna khana banate hain.",
      "local_context": "Haryana Rural - Kitchen/Chulha analogy"
    },
    "metadata": {
      "processing_time_ms": 1200
    }
  }
}
```

---

## 3. Process Audio Command (Stub)
Reserved for Phase 1 audio implementation. Currently returns a structured error or placeholder.

- **Path:** `/command/audio`
- **Method:** `POST`
- **Request Content-Type:** `multipart/form-data`
- **Request Schema:**
  - `audio_file`: Binary
  - `session_id`: String
- **Response Example:**
```json
{
  "status": "error",
  "error": {
    "code": "NOT_IMPLEMENTED",
    "message": "Audio processing is not available in Phase 0. Use /command/text."
  }
}
```

---

## 4. Clear Session
Wipes the transient memory for a specific classroom session.

- **Path:** `/session/{session_id}/clear`
- **Method:** `POST`
- **Response Example:**
```json
{
  "status": "success",
  "data": {
    "session_id": "classroom_7a",
    "cleared": true
  }
}
```

---

## 5. Get Last Interaction
Retrieves the most recent AI response for the UI state recovery.

- **Path:** `/session/{session_id}/last`
- **Method:** `GET`
- **Response Example (Intent: quiz):**
```json
{
  "status": "success",
  "data": {
    "intent": "quiz",
    "display": {
      "title": "Quick Check: Gravity",
      "questions": [
        {
          "id": 1,
          "question": "Agar aap upar ball fenkenge toh kya hoga?",
          "options": ["Upar hi rahegi", "Niche giregi", "Gayab ho jayegi"],
          "answer": "Niche giregi"
        }
      ]
    }
  }
}
```

---

## Intent Types & Fallbacks

| Intent | Description | Fallback Behavior |
| :--- | :--- | :--- |
| `explain` | Simplifies a concept using local analogies. | Asks: "Kaunsa topic samjhau? (Which topic should I explain?)" |
| `quiz` | Generates 3-5 relevant MCQs based on last topic. | Asks: "Kis cheez ka test lena hai? (What should I quiz on?)" |
| `clarify` | Returned when intent is ambiguous. | Returns suggested buttons: ["Explain a topic", "Start a quiz"] |

---

## Error Codes
- `INVALID_SESSION`: session_id missing or invalid.
- `LLM_TIMEOUT`: AI provider took too long to respond.
- `AMBIGUOUS_INTENT`: Could not determine if teacher wanted an explanation or a quiz.
- `RATE_LIMIT`: Too many requests in a short period.
