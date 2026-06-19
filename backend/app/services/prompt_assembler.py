import os
from typing import List, Dict, Any
from app.services.system_prompt import get_system_prompt
from app.services.language_router import detect_language_details
from app.services.prompts import LANGUAGE_INSTRUCTIONS

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")

class PromptAssembler:
    def assemble_prompt(
        self,
        query: str,
        memory_context: Dict[str, Any],
        source_chunks: List[Any] = None,
        source_mode: bool = False
    ) -> str:
        """
        Build a unified, memory-aware prompt for the LLM.
        """
        system_base = get_system_prompt()
        
        # Determine Mode Prompt
        mode = memory_context.get("current_mode", "explain")
        mode_prompt = ""
        if mode == "quiz":
            prompt_file = os.path.join(PROMPTS_DIR, "quiz_prompt.txt")
        else:
            prompt_file = os.path.join(PROMPTS_DIR, "explain_prompt.txt")
            
        if os.path.exists(prompt_file):
            with open(prompt_file, "r", encoding="utf-8") as f:
                mode_prompt = f"\n### MODE INSTRUCTIONS\n{f.read().strip()}\n"
        
        # Determine Language Rules
        language_mode, is_explicit = detect_language_details(query)
        if language_mode == "hinglish":
            actual_lang = "hinglish_explicit" if is_explicit else "hinglish"
        else:
            actual_lang = language_mode
        lang_rule = LANGUAGE_INSTRUCTIONS.get(actual_lang, LANGUAGE_INSTRUCTIONS["hinglish"])
        lang_block = f"\n### LANGUAGE RULES\n{lang_rule}\n"
        
        # Memory Section
        user_prefs = memory_context["user_preferences"]
        memory_block = f"""
### MEMORY CONTEXT
- Recent Conversation:
{memory_context['session_summary']}
- User Preferences:
  * Preferred Language: {user_prefs['preferred_language']}
  * Class Level: {user_prefs['preferred_class_level']}
  * Recurring Topics: {", ".join(user_prefs['recurring_topics'])}
  * Past Corrections: {", ".join(user_prefs['correction_history'])}
- Assistant State: {memory_context['assistant_state']}
- Current Mode: {memory_context['current_mode']}
"""

        # Source Section
        source_block = ""
        if source_mode and source_chunks:
            context_text = "\n\n".join([f"Source: {c.source_title}\nText: {c.text}" for c in source_chunks])
            source_block = f"""
### SOURCE MATERIAL (STRICT GROUNDING ON)
{context_text}
"""

        # Final Assembly
        final_prompt = f"""{system_base}
{mode_prompt}
{lang_block}
{memory_block}

{source_block}

### STUDENT COMMAND
Language Mode Requested: {memory_context['current_language_mode']}
Language Mode Explicitly Specified: {is_explicit}
Student Question: {query}

Response:"""

        return final_prompt

prompt_assembler = PromptAssembler()
