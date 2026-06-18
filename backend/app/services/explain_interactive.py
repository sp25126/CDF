import logging
from typing import Tuple, List
from app.services.explain_service import generate_explanation

logger = logging.getLogger(__name__)

def get_interactive_followup(language_mode: str) -> Tuple[str, List[str]]:
    """
    Returns an interactive follow-up prompt and voice commands based on language.
    """
    if language_mode == "english":
        return "Should I give an example, ask one question, or move on?", ["example", "ask one question", "move on", "repeat", "simpler"]
    elif language_mode == "hindi":
        return "क्या मैं एक उदाहरण दूँ, एक सवाल पूछूँ, या आगे बढूँ?", ["उदाहरण दें", "सवाल पूछें", "आगे बढ़ें", "दोहराएं", "आसान करें"]
    else:  # hinglish
        return "Kya main ek example doon, ek question poochun, ya aage badhu?", ["example", "ask one question", "move on", "repeat", "simpler"]

async def generate_interactive_explanation(session_id: str, text: str, language_mode: str = "hinglish", source_mode: bool = False) -> dict:
    """
    Generates an explanation and appends interactive follow-up logic for hands-free mode.
    """
    logger.info(f"Generating interactive explanation for session {session_id}")
    
    # Re-use the existing core explanation generator
    result = await generate_explanation(session_id, text, language_mode, source_mode)
    
    # Overwrite the standard follow-up with the interactive one
    q_text, commands = get_interactive_followup(language_mode)
    
    ans_text = result.get("answer_text", "")
    # Remove the standard prompt if it was already appended by explain_service
    # It might have appended "Should I explain it more simply?" etc.
    # A cleaner way would be to refactor explain_service, but we can just replace known strings.
    standard_prompts = [
        "Should I explain it more simply?", 
        "क्या मैं इसे और सरल तरीके से समझाऊं?", 
        "Kya main isko aur simply samjhaoon?"
    ]
    for sp in standard_prompts:
        ans_text = ans_text.replace(f" {sp}", "")
        ans_text = ans_text.replace(sp, "")
        
    if "cannot find the answer" not in ans_text.lower():
        result["answer_text"] = f"{ans_text.strip()} {q_text}"
        result["follow_up_prompt"] = q_text
        result["next_voice_commands"] = commands
        # Override suggestions
        result["next_actions"] = commands
        
    return result
