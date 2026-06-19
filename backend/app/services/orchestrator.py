import uuid
import base64
import logging
import json
from typing import Optional

from app.schemas.response import AssistantResponse, QuizPayload, QuizQuestion, SourceRef
from app.services.language_router import detect_language
from app.services.intent_router import detect_intent, normalize_text
from app.services.llm_service import llm_service
from app.services.response_builder import build_final_response

from app.services.retrieval import retrieve_relevant_chunks
from app.services.visual_classifier import detect_visual_need
from app.services.image_retrieval import retrieve_visuals
from app.services.video_search import search_videos

from app.services.memory_retriever import memory_retriever
from app.services.memory_writer import memory_writer
from app.services.session_memory import session_memory_service
from app.services.prompt_assembler import prompt_assembler

from app.services.topic_splitter import split_into_topics

logger = logging.getLogger(__name__)

from app.services.explain_interactive import generate_interactive_explanation
from app.services.quiz_interactive import generate_interactive_quiz, process_quiz_answer
from app.services.voice_command_router import voice_command_router
from app.services.hands_free_state import state_manager

# Basic fallbacks for unclear commands
UNCLEAR_RESPONSES = {
    "english": {
        "message": "I did not understand that. Please repeat in simpler words or ask to explain a topic.",
        "suggestions": ["Explain Photosynthesis", "Quiz on Gravity"],
        "response_text": "I'm sorry, I did not understand that. Please repeat in simpler words."
    },
    "hindi": {
        "message": "मुझे समझ नहीं आया। कृपया आसान शब्दों में दोहराएं या समझाने के लिए कहें।",
        "suggestions": ["Explain Photosynthesis", "Quiz on Gravity"],
        "response_text": "माफ़ कीजिये, मुझे समझ नहीं आया। कृपया आसान शब्दों में फिर से समझाएं।"
    },
    "hinglish": {
        "message": "Mafi chahta hu, samajh nahi aaya. Kripya thode aasan shabdon mein bataiye.",
        "suggestions": ["Explain Photosynthesis", "Quiz on Gravity"],
        "response_text": "Mafi chahta hu, samajh nahi aaya. Kripya thode aasan shabdon mein bataiye."
    }
}

async def build_assistant_response(
    session_id: str,
    text: str,
    mode_hint: Optional[str] = None,
    source_mode: bool = False,
    user_id: str = "default_teacher"
) -> AssistantResponse:
    """
    Main orchestrator service that coordinates intent, language, memory,
    and returns a unified AssistantResponse schema.
    """
    normalized = normalize_text(text)
    language_mode = detect_language(text)
    
    # 1. Retrieve Memory Context
    memory_context = memory_retriever.retrieve_memory_context(session_id, user_id, normalized)
    
    # Update session state with current inputs for later assembly
    session = session_memory_service.get_session(session_id)
    session.language_mode = language_mode
    session_memory_service.update_session(session)

    # Manage Hands Free Mode toggle
    if mode_hint == "hands_free_start" or text.lower().strip() == "hands_free_start":
        state_manager.enable_hands_free(session_id)
    elif mode_hint == "hands_free_stop" or text.lower().strip() in ["hands_free_stop", "stop hands free", "stop hands-free"]:
        state_manager.disable_hands_free(session_id)
        
    is_hf = state_manager.is_hands_free(session_id)
    current_hf_state = state_manager.get_state(session_id).get("assistant_state", "idle")
    
    # Defaults
    requires_clarification = False
    answer_text = None
    quiz_payload = None
    next_actions = []
    avatar_state = "idle"
    source_refs = []
    visuals = []
    videos = []
    visual_reason = None
    video_reason = None
    follow_up_prompt = None
    next_voice_commands = []
    voice_command_mode = False
    
    title = None
    grade_level = None
    bullets = []
    example = None
    recap = None
    questions_compat = []
    
    # Fast-path: Check Voice Command Router if in Hands Free
    voice_cmd = voice_command_router.route_command(normalized, is_hands_free=is_hf)
    
    if current_hf_state == "quizzing" and not voice_cmd:
        intent = "quiz_answer"
        confidence = 1.0
        res = process_quiz_answer(session_id, normalized, language_mode)
        title = res.get("title")
        answer_text = res.get("answer_text")
        follow_up_prompt = res.get("follow_up_prompt")
        next_voice_commands = res.get("next_voice_commands", [])
        next_actions = next_voice_commands
        avatar_state = "speaking"
        voice_command_mode = True
        questions_compat = res.get("questions", [])
        if title == "Quiz Finished":
            state_manager.set_state(session_id, "idle", follow_up_prompt, next_voice_commands)
        else:
            state_manager.set_state(session_id, "quizzing", follow_up_prompt, next_voice_commands)

    else:
        # Determine intent
        if voice_cmd:
            intent = voice_cmd
            confidence = 1.0
        elif mode_hint and mode_hint not in ["hands_free_start", "hands_free_stop"]:
            intent = mode_hint
            confidence = 1.0
        else:
            intent = detect_intent(normalized)
            confidence = 0.85 if intent != "unclear" else 0.3
                
        logger.info(f"Orchestrator: intent='{intent}', lang='{language_mode}'")
        
        if intent in ["explain", "example", "simpler", "quiz", "ask_question"]:
            avatar_state = "speaking"
            
            # Decompose the query into sub-questions
            sub_queries = split_into_topics(normalized)
            logger.info(f"TopicSplitter split query '{normalized}' into: {sub_queries}")
            
            sub_results = []
            
            for sub_q in sub_queries:
                # 2. Retrieve Source Chunks if needed
                chunks = []
                if source_mode:
                    chunks = retrieve_relevant_chunks(sub_q, limit=3)
                
                # 3. Assemble Memory-Aware Prompt
                final_prompt = prompt_assembler.assemble_prompt(
                    query=sub_q,
                    memory_context=memory_context,
                    source_chunks=chunks,
                    source_mode=source_mode
                )
                
                # 4. Call LLM
                try:
                    task_type = "quiz" if intent in ["quiz", "ask_question"] else "explain"
                    raw_response = await llm_service.generate_response(
                        final_prompt, 
                        task_type=task_type,
                        response_format={"type": "json_object"}
                    )
                    
                    import re
                    json_match = re.search(r'\{.*\}|\[.*\]', raw_response, re.DOTALL)
                    if json_match:
                        sub_res = json.loads(json_match.group(0))
                    else:
                        sub_res = {
                            "title": sub_q.title(),
                            "answer_text": raw_response.strip(),
                            "next_actions": ["Explain more", "Give an example"]
                        }
                except Exception as e:
                    logger.error(f"LLM failure in orchestrator for sub-query '{sub_q}': {e}")
                    sub_res = {"title": "Error", "answer_text": "I'm having trouble thinking right now.", "next_actions": ["Try again"]}
                
                # Visuals/Videos for this sub-question
                sub_visuals = []
                sub_visual_reason = None
                visual_info = await detect_visual_need(sub_q, sub_res.get("answer_text", ""))
                if visual_info.get("needs_visual"):
                    candidates = await retrieve_visuals(sub_q)
                    from app.services.image_selector import select_best_image
                    best_img = select_best_image(candidates)
                    if best_img:
                        sub_visuals = [best_img]
                    sub_visual_reason = visual_info.get("visual_reason")

                sub_videos = {"best_video": None, "candidate_videos": []}
                sub_video_reason = None
                video_info = await search_videos(sub_q, sub_res.get("answer_text", ""), language_mode)
                if video_info:
                    # Include primary video first, then alternatives
                    sub_videos["best_video"] = video_info["primary"]["video"]
                    sub_video_reason = video_info["primary"]["reason"]
                    for alt in video_info.get("alternatives", []):
                        sub_videos["candidate_videos"].append(alt["video"])
                    
                # Quiz questions compatibility
                sub_questions = []
                if intent in ["quiz", "ask_question"] and "questions" in sub_res:
                    sub_questions = sub_res["questions"]

                sub_results.append({
                    "res": sub_res,
                    "chunks": chunks,
                    "visuals": sub_visuals,
                    "visual_reason": sub_visual_reason,
                    "videos": sub_videos,
                    "video_reason": sub_video_reason,
                    "questions": sub_questions
                })

            # Merge the sub-results
            if len(sub_results) == 1:
                # Simple single query case
                single = sub_results[0]
                res = single["res"]
                chunks = single["chunks"]
                visuals = single["visuals"]
                visual_reason = single["visual_reason"]
                videos = single["videos"]
                video_reason = single["video_reason"]
                questions_compat = single["questions"]
            else:
                # Merge multiple sub-queries
                titles = [sr["res"].get("title") for sr in sub_results if sr["res"].get("title")]
                title = " & ".join(titles) if titles else "Compound Answer"
                
                # Merge answer texts with clean transitional flow
                answers = [sr["res"].get("answer_text") for sr in sub_results if sr["res"].get("answer_text")]
                if language_mode == "hindi":
                    transition = "\n\nइसके अलावा, आइए दूसरे भाग को देखें:\n\n"
                elif language_mode == "hinglish":
                    transition = "\n\nAlso, let's look at the second part:\n\n"
                else:
                    transition = "\n\nAlso, let's examine the second part:\n\n"
                answer_text = transition.join(answers) if answers else "Unable to combine answers."
                
                # Merge bullets, examples, and recaps
                bullets = []
                examples = []
                recaps = []
                for sr in sub_results:
                    bullets.extend(sr["res"].get("bullets", []))
                    if sr["res"].get("example"):
                        examples.append(sr["res"].get("example"))
                    if sr["res"].get("recap"):
                        recaps.append(sr["res"].get("recap"))
                        
                example = "\n\n".join(examples) if examples else None
                recap = " / ".join(recaps) if recaps else None
                
                # Merge visuals & videos (prevent duplicates)
                visuals = []
                visual_reasons = []
                for sr in sub_results:
                    for v in sr["visuals"]:
                        if v.url not in [vis.url for vis in visuals]:
                            visuals.append(v)
                    if sr["visual_reason"]:
                        visual_reasons.append(sr["visual_reason"])
                visual_reason = "; ".join(visual_reasons) if visual_reasons else None
                
                videos = {"best_video": None, "candidate_videos": []}
                video_reasons = []
                seen_video_ids = set()
                
                for sr in sub_results:
                    sub_vid = sr["videos"]
                    if sub_vid.get("best_video"):
                        vid = sub_vid["best_video"]
                        if not videos["best_video"]:
                            videos["best_video"] = vid
                            seen_video_ids.add(vid.youtube_id)
                        elif vid.youtube_id not in seen_video_ids:
                            videos["candidate_videos"].append(vid)
                            seen_video_ids.add(vid.youtube_id)
                            
                    for alt in sub_vid.get("candidate_videos", []):
                        if alt.youtube_id not in seen_video_ids:
                            videos["candidate_videos"].append(alt)
                            seen_video_ids.add(alt.youtube_id)
                            
                    if sr["video_reason"]:
                        video_reasons.append(sr["video_reason"])
                        
                video_reason = "; ".join(video_reasons) if video_reasons else None
                
                # Merge quiz questions
                questions_compat = []
                for sr in sub_results:
                    questions_compat.extend(sr["questions"])
                    
                # Merge chunks
                chunks = []
                for sr in sub_results:
                    chunks.extend(sr["chunks"])
                
                # Create merged dict
                res = {
                    "title": title,
                    "answer_text": answer_text,
                    "bullets": bullets,
                    "example": example,
                    "recap": recap,
                    "next_actions": ["Explain more", "Start a quiz"]
                }

            # Finalize fields
            title = res.get("title")
            answer_text = res.get("answer_text")
            next_actions = res.get("next_actions", ["Explain more", "Start a quiz"])
            
            # Citations for source mode
            if source_mode and chunks:
                source_refs = [SourceRef(title=c.source_title, snippet=c.text[:100], page_number=c.page_number) for c in chunks]
            
            # Quiz specific payload extraction
            if intent in ["quiz", "ask_question"] and questions_compat:
                quiz_payload = QuizPayload(title=title, topic=normalized, questions=questions_compat, total_questions=len(questions_compat))
            
            state_manager.set_state(session_id, "idle")

        elif intent == "stop":
            avatar_state = "idle"
            state_manager.set_state(session_id, "idle")
            answer_text = "Stopping. Let me know when you're ready."
            next_actions = ["Resume"]
            
        else:
            intent = "unclear"
            requires_clarification = True
            lang_key = language_mode if language_mode in UNCLEAR_RESPONSES else "hinglish"
            conf = UNCLEAR_RESPONSES[lang_key]
            answer_text = conf["response_text"]
            next_actions = conf["suggestions"]

    # 5. Update Memory (Write-back)
    session_memory_service.add_turn(session_id, "user", text)
    if answer_text:
        session_memory_service.add_turn(session_id, "assistant", answer_text)
    
    memory_writer.process_turn_for_long_term_memory(user_id, text)

    # 6. Build Final Response
    from app.services.tts_service import tts_service
    audio_content = None
    if answer_text:
        try:
            audio_content = await tts_service.speak(answer_text)
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            
    hf_state_data = state_manager.get_state(session_id)
            
    return build_final_response(
        session_id=session_id,
        intent=intent,
        language_mode=language_mode,
        text=text,
        answer_text=answer_text,
        quiz_payload=quiz_payload,
        next_actions=next_actions,
        confidence=confidence,
        requires_clarification=requires_clarification,
        avatar_state=avatar_state,
        source_refs=source_refs,
        visuals=visuals,
        videos=videos,
        visual_reason=visual_reason,
        video_reason=video_reason,
        audio_content=audio_content,
        title=title,
        source_mode=source_mode,
        hands_free_mode=is_hf,
        assistant_state=hf_state_data["assistant_state"]
    )
