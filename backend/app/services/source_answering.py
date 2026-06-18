import json
from typing import Dict, Any, List
from app.services.llm_service import llm_service
from app.services.retrieval import retrieve_relevant_chunks
from app.schemas.chunk import Chunk

REFUSAL_MESSAGES = {
    "english": "I'm sorry, I couldn't find the answer to that in the uploaded source material.",
    "hindi": "माफ़ करें, मुझे अपलोड की गई सामग्री में इसका उत्तर नहीं मिला।",
    "hinglish": "Maaf karein, mujhe upload kiye gaye material mein iska answer nahi mila."
}

async def generate_source_grounded_answer(session_id: str, text: str, language_mode: str) -> Dict[str, Any]:
    """
    Generate an answer strictly based on retrieved source chunks.
    """
    chunks: List[Chunk] = retrieve_relevant_chunks(text, limit=3)
    
    if not chunks:
        refusal = REFUSAL_MESSAGES.get(language_mode, REFUSAL_MESSAGES["hinglish"])
        return {
            "answer_text": refusal,
            "citations": [],
            "title": "Not Found",
            "next_actions": ["Ask something else", "Explain a new topic"]
        }
        
    # Build prompt
    context_text = "\n\n".join([f"Source: {c.source_title}\nText: {c.text}" for c in chunks])
    
    prompt = f"""You are a helpful classroom assistant.
You must answer the student's question ONLY using the provided source material below.
Do NOT use your generic knowledge. If the answer is not in the material, say "NOT_FOUND".

Language constraint: 
- Answer in {language_mode.upper()} language.

Source Material:
{context_text}

Student Question: {text}

Output JSON format strictly:
{{
    "title": "Topic title",
    "answer_text": "Your detailed explanation here",
    "next_actions": ["Action 1", "Action 2"]
}}
"""
    
    try:
        response_text = await llm_service.generate_response(prompt)
        if "NOT_FOUND" in response_text or not response_text.strip():
            refusal = REFUSAL_MESSAGES.get(language_mode, REFUSAL_MESSAGES["hinglish"])
            return {
                "answer_text": refusal,
                "citations": [],
                "title": "Not Found",
                "next_actions": ["Ask something else", "Explain a new topic"]
            }
            
        result = json.loads(response_text)
        
        # Add citations from retrieved chunks
        citations = []
        for c in chunks:
            citations.append({
                "source_title": c.source_title,
                "snippet": c.text[:100] + "...",
                "page_number": c.page_number,
                "section_label": c.section_label
            })
            
        result["citations"] = citations
        return result
        
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error in source_answering: {e}")
        refusal = REFUSAL_MESSAGES.get(language_mode, REFUSAL_MESSAGES["hinglish"])
        return {
            "answer_text": refusal,
            "citations": [],
            "title": "Error Processing",
            "next_actions": ["Try again"]
        }
