from fastapi import APIRouter
from app.api.schemas import GlobalResponse

router = APIRouter()

@router.post("/{session_id}/clear", response_model=GlobalResponse)
async def clear_session(session_id: str):
    return {
        "status": "success",
        "data": {
            "session_id": session_id,
            "cleared": True
        }
    }

@router.get("/{session_id}/last", response_model=GlobalResponse)
async def get_last_interaction(session_id: str):
    return {
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
