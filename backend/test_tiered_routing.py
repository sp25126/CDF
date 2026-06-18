import asyncio
import logging
import sys
from app.services.llm_service import llm_service
from app.services.intent_service import detect_intent
from app.services.visual_classifier import detect_visual_need
from app.services.video_suggester import suggest_video

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TestTieredRouting")

async def test_all():
    logger.info("=== STARTING TIERED ROUTING TESTS ===")

    # 1. Test Intent Detection (should route to TIER_SMALL, e.g. qwen2:0.5b)
    logger.info("Testing Intent Detection...")
    intent1 = await detect_intent("explain the solar system")
    intent2 = await detect_intent("sawal pucho photo synthesis par")
    intent3 = await detect_intent("xyzabcde gibberish")
    logger.info(f"Intent 1: {intent1} (Expected: explain)")
    logger.info(f"Intent 2: {intent2} (Expected: quiz)")
    logger.info(f"Intent 3: {intent3} (Expected: clarify)")

    # 2. Test Visual Classifier (should route to TIER_MID, e.g. qwen2.5:3b or gemma2:2b)
    logger.info("Testing Visual Classifier...")
    vis_res = await detect_visual_need("Heart Anatomy", "How does the human heart pump blood?")
    logger.info(f"Visual Classifier Result: {vis_res}")

    # 3. Test Video Suggester (should route to TIER_MID, e.g. qwen2.5:3b or gemma2:2b)
    logger.info("Testing Video Suggester...")
    vid_res = await suggest_video("Photosynthesis", "How do plants convert sunlight to food?")
    logger.info(f"Video Suggester Result: {vid_res}")

    # 4. Test Explanation Completion (should route to TIER_STRONG, e.g. gemma4:e2b or OpenRouter)
    logger.info("Testing Explanation Generation...")
    explain_prompt = (
        "Output a JSON object explaining Photosynthesis in Hinglish. "
        "Fields must be: title, answer_text, next_actions."
    )
    explain_res = await llm_service.get_chat_completion(
        messages=[{"role": "user", "content": explain_prompt}],
        response_format={"type": "json_object"},
        task_type="explain"
    )
    logger.info(f"Explanation Result Title: {explain_res.get('title')}")
    logger.info(f"Explanation Result Length: {len(str(explain_res.get('answer_text')))} chars")

    # 5. Test Quiz Generation (should route to TIER_STRONG, e.g. gemma4:e2b or OpenRouter)
    logger.info("Testing Quiz Generation...")
    quiz_prompt = (
        "Generate a short quiz with 2 MCQs on Gravity. "
        "Output ONLY raw JSON matching: {\"questions\": [{\"question\": \"...\", \"options\": [\"...\", \"...\"], \"correct_index\": 0, \"explanation\": \"...\"}], \"title\": \"Gravity Quiz\", \"response_text\": \"...\"}"
    )
    quiz_res = await llm_service.get_chat_completion(
        messages=[{"role": "user", "content": quiz_prompt}],
        response_format={"type": "json_object"},
        task_type="quiz"
    )
    logger.info(f"Quiz Result Title: {quiz_res.get('title')}")
    logger.info(f"Quiz Result Questions Count: {len(quiz_res.get('questions', []))}")

    logger.info("=== ALL TESTS COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    asyncio.run(test_all())
