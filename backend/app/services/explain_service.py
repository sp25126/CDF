import re
import logging
from typing import Dict, Any
from app.services.llm_service import llm_service
from app.services.source_service import source_service
from app.services.lesson_service import _get_mock_explanation
from app.services.prompts import (
    SYSTEM_PROMPT, EXPLAIN_PROMPT_TEMPLATE, LANGUAGE_INSTRUCTIONS,
    SOURCE_SYSTEM_PROMPT, SOURCE_EXPLAIN_PROMPT_TEMPLATE
)

logger = logging.getLogger(__name__)

def build_explain_prompt(topic: str, language_mode: str, class_level: str | None = None) -> str:
    """
    Constructs the prompt for explain mode.
    """
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language_mode, LANGUAGE_INSTRUCTIONS["default"])
    return EXPLAIN_PROMPT_TEMPLATE.format(
        topic=topic,
        grade=class_level or "6",
        language_instruction=lang_instruction
    )

async def generate_explanation(session_id: str, text: str, language_mode: str = "hinglish", source_mode: bool = False) -> dict:
    """
    Generate explanation using the LLM, with fallback to local mock database.
    Returns a dict that conforms to explain output.
    """
    # Clean up search topic
    clean_text = text.lower()
    for char in [".", ",", "?", "!", "\"", "'"]:
        clean_text = clean_text.replace(char, " ")
        
    stop_words = [
        "explain", "samjhao", "batao", "kya hai", "meaning", "how", "why", "about",
        "for class 6", "for class 7", "for class 8", "for class 5", "in hinglish", 
        "haryana", "a", "an", "the", "make", "in english", "english mein", "english me",
        "in hindi", "hindi mein", "hindi me", "pure hindi"
    ]
    for word in stop_words:
        clean_text = re.sub(rf'\b{re.escape(word)}\b', ' ', clean_text)
        
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    topic = clean_text.title() or "Photosynthesis"
    topic_lower = topic.lower()

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language_mode, LANGUAGE_INSTRUCTIONS["default"])

    if source_mode:
        all_sources = source_service.list_sources()
        if not all_sources:
            return {
                "title": "No Source Uploaded",
                "grade_level": 6,
                "bullets": ["Please upload classroom materials first in the sources panel."],
                "example": "No active files found.",
                "recap": "Upload files, text, or links to query documents.",
                "answer_text": "Please upload some classroom materials first in the sources panel.",
                "citations": []
            }

        chunks = source_service.retrieve_chunks(text, limit=3)
        if not chunks:
            return {
                "title": "Not Found",
                "grade_level": 6,
                "bullets": [],
                "example": "",
                "recap": "",
                "answer_text": "I cannot find the answer to this question in the provided source material.",
                "citations": []
            }

        snippets_str = "\n---\n".join([f"Source: {c['source_title']} (Page {c['page_number']}):\n{c['text']}" for c in chunks])
        sys_prompt = SOURCE_SYSTEM_PROMPT.format(LANGUAGE_MODE=lang_instruction)
        user_prompt = SOURCE_EXPLAIN_PROMPT_TEMPLATE.format(
            topic=topic,
            grade=6,
            language_instruction=lang_instruction,
            snippets=snippets_str
        )

        citations = [
            {
                "source_title": c["source_title"],
                "snippet": c["text"][:150] + "...",
                "page_number": c["page_number"],
                "section_label": c["section_label"]
            }
            for c in chunks
        ]

        try:
            response_json = await llm_service.get_chat_completion([
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ], response_format={"type": "json_object"})
            
            ans_text = response_json.get("response_text") or response_json.get("answer_text")
            if "provided source material" in str(ans_text).lower() or response_json.get("title") == "Not Found":
                cits = []
            else:
                cits = citations
                
            return {
                "title": response_json.get("title", f"Explain {topic}"),
                "grade_level": response_json.get("grade_level", 6),
                "bullets": response_json.get("bullets", []),
                "example": response_json.get("example", ""),
                "recap": response_json.get("recap", ""),
                "answer_text": ans_text,
                "citations": cits
            }
        except Exception as e:
            logger.error(f"Source explain generation failed: {e}")
            top_chunk = chunks[0]
            bullets = [top_chunk["text"][:120] + "..."]
            if len(top_chunk["text"]) > 120:
                bullets.append(top_chunk["text"][120:240] + "...")
            return {
                "title": f"From: {top_chunk['source_title']}",
                "grade_level": 6,
                "bullets": bullets,
                "example": f"Verified from page {top_chunk['page_number']}.",
                "recap": "Grounded direct source chunk fallback.",
                "answer_text": top_chunk["text"][:300] + "...",
                "citations": [citations[0]]
            }

    # Standard Explain Mode
    sys_prompt = SYSTEM_PROMPT.format(LANGUAGE_MODE=lang_instruction)
    user_prompt = build_explain_prompt(topic, language_mode)

    try:
        response_json = await llm_service.get_chat_completion([
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ], response_format={"type": "json_object"})
        
        return {
            "title": response_json.get("title", f"Simplifying {topic}"),
            "grade_level": response_json.get("grade_level", 6),
            "bullets": response_json.get("bullets", []),
            "example": response_json.get("example", ""),
            "recap": response_json.get("recap", ""),
            "answer_text": response_json.get("response_text") or response_json.get("answer_text")
        }
    except Exception as e:
        logger.error(f"LLM explanation generation failed: {e}")
        # Fallback to mock explanation database
        mock_lang = "english" if language_mode == "english" else ("hindi" if language_mode == "hindi" else "hinglish")
        
        # Merge English written content with Hinglish spoken if default (which maps to hinglish/default here)
        if language_mode == "default" or language_mode == "hinglish":
            eng = _get_mock_explanation(topic_lower, "english", topic)
            hing = _get_mock_explanation(topic_lower, "hinglish", topic)
            return {
                "title": eng["title"],
                "grade_level": eng["grade_level"],
                "bullets": eng["bullets"],
                "example": eng["example"],
                "recap": eng["recap"],
                "answer_text": hing["response_text"]
            }
        else:
            mock_data = _get_mock_explanation(topic_lower, mock_lang, topic)
            return {
                "title": mock_data["title"],
                "grade_level": mock_data["grade_level"],
                "bullets": mock_data["bullets"],
                "example": mock_data["example"],
                "recap": mock_data["recap"],
                "answer_text": mock_data["response_text"]
            }
