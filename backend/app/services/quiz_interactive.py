import logging
from typing import Tuple, List, Optional
from app.services.quiz_service import generate_quiz
from app.services.hands_free_state import state_manager

logger = logging.getLogger(__name__)

async def generate_interactive_quiz(session_id: str, text: str, language_mode: str = "hinglish", source_mode: bool = False) -> dict:
    """
    Generates a quiz and prepares it for interactive one-question-at-a-time voice mode.
    """
    logger.info(f"Generating interactive quiz for session {session_id}")
    
    # Generate the full quiz
    res = await generate_quiz(session_id, text, language_mode, source_mode)
    questions = res.get("questions", [])
    
    if not questions:
        return res # Fallback if error

    # Save the full quiz state (we could store this in hands_free_state or a separate quiz_state cache)
    state = state_manager.get_state(session_id)
    state["quiz_data"] = res
    state_manager.reset_quiz_index(session_id)
    
    return get_current_quiz_question(session_id, language_mode)

def get_current_quiz_question(session_id: str, language_mode: str) -> dict:
    """
    Retrieves the current question from the active interactive quiz.
    """
    state = state_manager.get_state(session_id)
    quiz_data = state.get("quiz_data")
    idx = state_manager.get_quiz_index(session_id)
    
    if not quiz_data or "questions" not in quiz_data:
        return {"answer_text": "Quiz not found."}
        
    questions = quiz_data["questions"]
    if idx >= len(questions):
        state_manager.set_state(session_id, "idle")
        if language_mode == "english":
            msg = "You have finished the quiz!"
        elif language_mode == "hindi":
            msg = "आपने क्विज़ पूरा कर लिया है!"
        else:
            msg = "Aapne quiz poora kar liya hai!"
        return {
            "title": "Quiz Finished",
            "answer_text": msg,
            "next_voice_commands": ["explain something else"],
            "follow_up_prompt": None,
            "questions": questions # send all back for display
        }
        
    current_q = questions[idx]
    
    # Format the prompt
    options_text = " ".join([f"Option {chr(65+i)}: {opt}." for i, opt in enumerate(current_q["options"])])
    if language_mode == "english":
        prompt = f"Question {idx+1}. {current_q['question']} {options_text} What is your answer?"
    elif language_mode == "hindi":
        prompt = f"प्रश्न {idx+1}. {current_q['question']} {options_text} आपका जवाब क्या है?"
    else:
        prompt = f"Question {idx+1}. {current_q['question']} {options_text} Aapka jawab kya hai?"
        
    return {
        "title": f"Quiz: Question {idx+1}",
        "answer_text": prompt,
        "follow_up_prompt": prompt,
        "next_voice_commands": ["repeat", "show answer", "next question", "end quiz"],
        "questions": [current_q] # Just the current one for now
    }

def process_quiz_answer(session_id: str, text: str, language_mode: str) -> dict:
    """
    Processes a voice answer for the interactive quiz.
    Returns feedback and either stays on question or moves on.
    """
    state = state_manager.get_state(session_id)
    quiz_data = state.get("quiz_data")
    idx = state_manager.get_quiz_index(session_id)
    
    if not quiz_data or idx >= len(quiz_data.get("questions", [])):
        return {"answer_text": "Quiz is not active."}
        
    current_q = quiz_data["questions"][idx]
    correct_idx = current_q["correct_index"]
    correct_option_text = current_q["options"][correct_idx].lower()
    
    # Very basic answer checking (A, B, C, D or exact text match)
    text_lower = text.lower()
    
    is_correct = False
    is_answered = False
    
    letters = ["a", "b", "c", "d"]
    if idx < len(letters):
        correct_letter = letters[correct_idx]
        if correct_letter in text_lower.split() or "option " + correct_letter in text_lower:
            is_correct = True
            is_answered = True
            
    if not is_answered:
        if correct_option_text in text_lower:
            is_correct = True
            is_answered = True
            
    # For now, just show answer if they speak
    if language_mode == "english":
        feedback = "Correct! " if is_correct else "Not quite! "
        feedback += current_q["explanation"] + " Ready for the next question?"
        followup = "Ready for the next question?"
    elif language_mode == "hindi":
        feedback = "सही जवाब! " if is_correct else "थोड़ा गलत हो गया! "
        feedback += current_q["explanation"] + " अगले प्रश्न के लिए तैयार हैं?"
        followup = "अगले प्रश्न के लिए तैयार हैं?"
    else:
        feedback = "Sahi jawab! " if is_correct else "Thoda galat ho gaya! "
        feedback += current_q["explanation"] + " Agle question ke liye ready hain?"
        followup = "Agle question ke liye ready hain?"
        
    # We move them past the question but pause for confirmation before going to next
    state_manager.increment_quiz_index(session_id)
    
    return {
        "title": "Feedback",
        "answer_text": feedback,
        "follow_up_prompt": followup,
        "next_voice_commands": ["next question", "end quiz"],
        "questions": [current_q]
    }
