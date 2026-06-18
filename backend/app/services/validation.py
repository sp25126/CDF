import logging

logger = logging.getLogger(__name__)

def validate_response(res: dict, task_type: str) -> bool:
    """
    Validate that the dict returned from LLM service contains all required
    fields and correct types for the requested task type.
    """
    if not isinstance(res, dict):
        logger.warning(f"[Validation] Response is not a dict: {type(res)}")
        return False

    if task_type == "explain":
        # Check required fields for explain response
        required_keys = ["title", "answer_text"]
        for key in required_keys:
            if key not in res:
                logger.warning(f"[Validation] Missing key '{key}' in explain response")
                return False
            if not isinstance(res[key], str) or not res[key].strip():
                logger.warning(f"[Validation] Key '{key}' in explain response is not a non-empty string")
                return False
        return True

    elif task_type == "quiz":
        # Check required fields for quiz response
        if "questions" not in res:
            logger.warning("[Validation] Missing 'questions' key in quiz response")
            return False
        questions = res["questions"]
        if not isinstance(questions, list) or len(questions) == 0:
            logger.warning("[Validation] 'questions' is not a non-empty list in quiz response")
            return False
            
        for idx, q in enumerate(questions):
            if not isinstance(q, dict):
                logger.warning(f"[Validation] Question at index {idx} is not a dict")
                return False
            # We accept either "question" (new code) or "text" (some prompts use text)
            q_text_key = "question" if "question" in q else "text"
            if q_text_key not in q or not isinstance(q[q_text_key], str) or not q[q_text_key].strip():
                logger.warning(f"[Validation] Question at index {idx} lacks a non-empty question text")
                return False
            if "options" not in q or not isinstance(q["options"], list) or len(q["options"]) < 2:
                logger.warning(f"[Validation] Question at index {idx} lacks valid options")
                return False
            # Check correct_index
            if "correct_index" not in q and "answer" not in q:
                logger.warning(f"[Validation] Question at index {idx} lacks correct answer key")
                return False
        return True

    elif task_type == "classify":
        # visual classifiers / video classifier
        # We want to make sure it's a dictionary with at least some content.
        return True

    # Default / intent / clarify
    return True
