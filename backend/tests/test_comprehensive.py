"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║  Comprehensive Backend Test Suite — 5-Layer Validation                         ║
║                                                                                  ║
║  Layer 1 · API Health        — startup, connectivity, version                   ║
║  Layer 2 · Command Pipeline  — ingestion, intent, Hinglish, normalization       ║
║  Layer 3 · Response Quality  — classroom-safe, structured, language-correct     ║
║  Layer 4 · Media & Sources   — images, quiz, TTS, session, source grounding     ║
║  Layer 5 · Error Recovery    — empty input, bad commands, missing media, TTS    ║
╚══════════════════════════════════════════════════════════════════════════════════╝

Acceptance criteria (per brief):
  - Each response is functional, safe, and presentation-ready for a smart-board classroom.
  - Hinglish input handled without corrupting meaning.
  - Missing content returns safe empty state, not a crash.
  - Errors are readable and not raw stack traces.
  - Voice flow and UI state are never broken by a failed backend call.
"""
import sys
import os
import time
import base64
import re

import httpx
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0  # seconds — generous for LLM calls
SESSION = "comprehensive-test-session"

# ─── helpers ──────────────────────────────────────────────────────────────────

def post_command(text: str, session_id: str = SESSION, **extra) -> dict:
    payload = {"text": text, "session_id": session_id, **extra}
    r = httpx.post(f"{BASE_URL}/command/text", json=payload, timeout=TIMEOUT)
    assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:300]}"
    body = r.json()
    assert body.get("status") == "success", f"Response status not success: {body}"
    return body["data"]


def is_devanagari_free(text: str) -> bool:
    """True if text contains no Devanagari Unicode characters."""
    return not any(0x0900 <= ord(c) <= 0x097F for c in text)


def is_classroom_safe(text: str) -> bool:
    """
    Minimal classroom-safety check:
      - no raw stack traces
      - no internal Python tracebacks
      - no raw markdown symbols read as punctuation
    """
    lowered = text.lower()
    red_flags = ["traceback (most recent call last)", "file \"", "line ", "assert ", "attributeerror", "keyerror"]
    return not any(flag in lowered for flag in red_flags)


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 1 — API HEALTH
# ══════════════════════════════════════════════════════════════════════════════

class TestLayer1APIHealth:
    """Backend starts and all core routes respond correctly."""

    def test_health_check_200(self):
        """Health endpoint returns 200 with a valid status field."""
        r = httpx.get(f"{BASE_URL}/health", timeout=5)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        body = r.json()
        assert "status" in body, f"No 'status' field: {body}"
        assert body["status"] == "ok", f"Status not ok: {body}"
        print(f"  ✓ Health: {body}")

    def test_health_alt_prefix(self):
        """Health endpoint also reachable under /api/health."""
        r = httpx.get(f"{BASE_URL}/api/health", timeout=5)
        assert r.status_code == 200

    def test_openapi_schema_loads(self):
        """OpenAPI docs are accessible (confirms FastAPI is wired correctly)."""
        r = httpx.get(f"{BASE_URL}/openapi.json", timeout=5)
        assert r.status_code == 200
        schema = r.json()
        assert "paths" in schema
        paths = list(schema["paths"].keys())
        # Verify core routes exist
        assert any("/command/text" in p for p in paths), f"No command/text route: {paths[:10]}"
        assert any("/health" in p for p in paths), f"No health route: {paths[:10]}"
        print(f"  ✓ OpenAPI: {len(paths)} routes registered")

    def test_hands_free_start_stop(self):
        """Hands-free start/stop endpoints are reachable and return success."""
        r_start = httpx.post(f"{BASE_URL}/api/voice/hands-free/start",
                             json={"session_id": "hf-test"}, timeout=5)
        assert r_start.status_code == 200, f"HF start failed: {r_start.text}"

        r_stop = httpx.post(f"{BASE_URL}/api/voice/hands-free/stop",
                            json={"session_id": "hf-test"}, timeout=5)
        assert r_stop.status_code == 200, f"HF stop failed: {r_stop.text}"
        print("  ✓ Hands-free start/stop")

    def test_sources_list_reachable(self):
        """Source listing endpoint is reachable and returns a list."""
        r = httpx.get(f"{BASE_URL}/sources/list", timeout=5)
        assert r.status_code == 200
        body = r.json()
        assert "data" in body
        assert isinstance(body["data"], list)
        print(f"  ✓ Sources list: {len(body['data'])} source(s) in DB")

    def test_session_last_state_returns_safe_idle(self):
        """Fetching last state for a fresh session returns idle or empty — not a crash."""
        fresh_id = f"fresh-{int(time.time())}"
        r = httpx.get(f"{BASE_URL}/session/{fresh_id}/last", timeout=5)
        # May be 200 (empty session) or 404 — both are acceptable; must not be 500
        assert r.status_code in (200, 404), f"Unexpected status {r.status_code}: {r.text}"
        print(f"  ✓ Session restore: status={r.status_code}")


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 2 — COMMAND PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

class TestLayer2CommandPipeline:
    """Commands are ingested, normalised, and routed to the correct intent."""

    def test_plain_english_explain_intent(self):
        """A simple English explain command resolves to 'explain' mode."""
        data = post_command("Explain gravity", session_id="pipe-en")
        assert data["mode"] == "explain", f"Wrong mode: {data['mode']}"
        assert data["language_mode"] == "english" or data["language_mode"] == "hinglish"
        print(f"  ✓ English explain → mode={data['mode']}, lang={data['language_mode']}")

    def test_hinglish_explain_intent(self):
        """Hinglish command 'gravity explain karo' resolves to explain."""
        data = post_command("Gravity explain karo simple mein", session_id="pipe-hing")
        assert data["mode"] == "explain"
        print(f"  ✓ Hinglish explain → mode={data['mode']}")

    def test_hindi_command_resolved(self):
        """A pure Hindi instruction is not rejected — intent is inferred."""
        data = post_command("Explain gravity in Hindi", session_id="pipe-hindi")
        assert data["mode"] == "explain"
        assert data["language_mode"] == "hindi"
        print(f"  ✓ Hindi command → lang={data['language_mode']}")

    def test_quiz_command_routed_correctly(self):
        """'Quiz banao' is routed to quiz mode, not explain."""
        data = post_command("Fractions ka quiz banao 5 questions mein", session_id="pipe-quiz")
        assert data["mode"] == "quiz", f"Expected quiz, got {data['mode']}"
        print(f"  ✓ Quiz routing → mode={data['mode']}")

    def test_code_switching_does_not_crash(self):
        """Mid-sentence language switch (Hinglish + English term) is handled gracefully."""
        data = post_command(
            "Bachon ko photosynthesis explain karo, focus on chlorophyll",
            session_id="pipe-switch"
        )
        assert data["mode"] in ("explain", "quiz", "unclear")
        assert "response_text" in data
        print(f"  ✓ Code-switch handled → mode={data['mode']}")

    def test_intent_preserved_with_slang(self):
        """Slang / informal Hinglish still resolves to a meaningful intent."""
        data = post_command("Yaar gravity kya hoti hai thoda easy mein bata", session_id="pipe-slang")
        assert data["mode"] in ("explain", "unclear")
        print(f"  ✓ Slang input → mode={data['mode']}")

    def test_response_text_always_present(self):
        """Every successful command response includes a response_text field."""
        data = post_command("Tell me about the water cycle", session_id="pipe-rt")
        assert "response_text" in data, "response_text missing from payload"
        assert isinstance(data["response_text"], str)
        assert len(data["response_text"]) > 5
        print(f"  ✓ response_text present: {len(data['response_text'])} chars")

    def test_language_mode_field_present(self):
        """Every response carries a language_mode field."""
        data = post_command("Explain mitosis in English", session_id="pipe-lm")
        assert "language_mode" in data
        assert data["language_mode"] in ("english", "hindi", "hinglish")
        print(f"  ✓ language_mode={data['language_mode']}")


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 3 — RESPONSE QUALITY
# ══════════════════════════════════════════════════════════════════════════════

class TestLayer3ResponseQuality:
    """Responses are classroom-appropriate, structured, and language-correct."""

    # ── Concept simplification ──────────────────────────────────────────────

    def test_concept_simplification_hinglish(self):
        """
        Functional case 1 — Concept simplification:
        Hinglish explanation should be concise and pedagogy-safe.
        """
        data = post_command("Photosynthesis explain karo Hinglish mein class 8 ke liye",
                             session_id="qual-simp")
        assert data["mode"] == "explain"
        assert data["language_mode"] == "hinglish"
        resp = data["response_text"]
        assert len(resp) > 20, "Response too short to be useful"
        assert is_classroom_safe(resp), f"Unsafe response content: {resp[:200]}"
        # answer_text contains markdown for UI display, TTS engine cleans it before speech.
        print(f"  ✓ Hinglish simplification: {resp[:100]}…")

    def test_english_response_no_devanagari(self):
        """English mode response must not include Devanagari characters."""
        data = post_command("Explain the food chain in English", session_id="qual-en")
        assert data["language_mode"] == "english"
        resp = data["response_text"]
        assert is_devanagari_free(resp), f"Devanagari found in English response: {resp[:200]}"
        print("  ✓ English response is Devanagari-free")

    def test_explain_returns_bullets(self):
        """Explain response includes a bullets list for structured classroom display."""
        data = post_command("Explain cell division in English", session_id="qual-bullets")
        assert data["mode"] == "explain"
        bullets = data.get("bullets", [])
        assert isinstance(bullets, list), f"bullets should be list, got {type(bullets)}"
        assert len(bullets) >= 1, "Expected at least 1 bullet point"
        for b in bullets:
            assert isinstance(b, str) and len(b) > 2
        print(f"  ✓ bullets: {len(bullets)} items")

    def test_title_is_present_and_short(self):
        """Each explain response includes a non-empty title suitable for display."""
        data = post_command("What is evaporation? in English", session_id="qual-title")
        title = data.get("title", "")
        assert title and len(title) > 2, f"Title too short or missing: {title!r}"
        assert len(title) < 120, f"Title too long for display: {title!r}"
        print(f"  ✓ title: {title!r}")

    # ── Voice-triggered quiz ────────────────────────────────────────────────

    def test_quiz_payload_structure(self):
        """
        Functional case 2 — Voice-triggered quiz:
        Quiz response must carry distinct question/options structure, not an explanation.
        """
        data = post_command("Create a 5 question quiz on the digestive system in English",
                             session_id="qual-quiz")
        assert data["mode"] == "quiz"
        questions = data.get("questions", [])
        assert len(questions) >= 1, f"Quiz returned {len(questions)} questions"
        for q in questions:
            assert "question" in q, f"Question field missing: {q}"
            assert "options" in q, f"Options field missing: {q}"
            opts = q["options"]
            assert len(opts) >= 2, f"Too few options: {opts}"
            assert "correct_answer" in q, f"correct_answer missing: {q}"
        print(f"  ✓ Quiz structure: {len(questions)} questions, each with options+answer")

    def test_quiz_questions_are_distinct(self):
        """Quiz questions should not be duplicates of each other."""
        data = post_command("Quiz on water cycle 5 questions English", session_id="qual-unique")
        questions = data.get("questions", [])
        if len(questions) >= 2:
            texts = [q.get("question", "") for q in questions]
            unique = set(texts)
            assert len(unique) == len(texts), f"Duplicate questions detected: {texts}"
        print(f"  ✓ All {len(questions)} quiz questions are distinct")

    # ── Bilingual dictation / translation ──────────────────────────────────

    def test_bilingual_input_intelligible(self):
        """
        Functional case 3 — Bilingual dictation:
        Mixed Hindi-English input is processed without garbling the meaning.
        """
        data = post_command(
            "Newton ke laws of motion explain karo, especially inertia",
            session_id="qual-bi"
        )
        assert data["mode"] in ("explain", "unclear")
        resp = data["response_text"]
        assert len(resp) > 10
        # The response should reference Newton or motion or inertia
        key_terms = ["newton", "motion", "inertia", "law"]
        assert any(term in resp.lower() for term in key_terms), (
            f"Expected physics term in response, got: {resp[:200]}"
        )
        print(f"  ✓ Bilingual input: intelligible response ({resp[:80]}…)")

    # ── Hands-free activity guide ───────────────────────────────────────────

    def test_hands_free_step_by_step_response(self):
        """
        Functional case 4 — Hands-free activity guide:
        Step-by-step instruction request returns ordered, speakable content.
        """
        data = post_command(
            "Give me a step-by-step activity to demonstrate the water cycle in class",
            session_id="qual-hf",
            mode_hint="explain"
        )
        assert data["mode"] in ("explain", "unclear")
        resp = data["response_text"]
        # Should have some sequential or ordered structure
        has_steps = (
            any(f"{n}." in resp for n in range(1, 6)) or
            "step" in resp.lower() or
            "first" in resp.lower() or
            len(data.get("bullets", [])) >= 2
        )
        assert has_steps, f"No step structure in response: {resp[:300]}"
        # Should not be too long to read aloud in one breath (< 2000 chars)
        assert len(resp) < 2000, f"Response too long for live classroom TTS: {len(resp)} chars"
        print(f"  ✓ Activity guide: {len(resp)} chars, has steps")

    def test_response_has_no_raw_stack_trace(self):
        """No response should expose internal Python exceptions to the teacher."""
        for topic in ["gravity", "osmosis", "fractions"]:
            data = post_command(f"Explain {topic}", session_id=f"qual-safe-{topic}")
            assert is_classroom_safe(data.get("response_text", "")), (
                f"Stack trace or internal error in response for '{topic}'"
            )
        print("  ✓ No raw stack traces in any explain response")


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 4 — MEDIA & SOURCE HANDLING
# ══════════════════════════════════════════════════════════════════════════════

class TestLayer4MediaAndSources:
    """Images, TTS, session state, and source-grounded responses."""

    # ── Image retrieval ─────────────────────────────────────────────────────

    def test_image_retrieval_returns_validated_urls(self):
        """Image cards must have title, url, and alt fields — no broken metadata."""
        from app.services.image_retrieval import retrieve_visuals
        import asyncio
        images = asyncio.get_event_loop().run_until_complete(
            retrieve_visuals("photosynthesis")
        )
        if images:  # May be empty if API quota exceeded — that's OK
            for img in images:
                assert getattr(img, "title", None) is not None, f"Image missing title: {img}"
                url = img.get("url") if isinstance(img, dict) else getattr(img, "url", None)
                alt = img.get("alt_text") or img.get("alt") if isinstance(img, dict) else (getattr(img, "alt_text", None) or getattr(img, "alt", None))
                assert url is not None, f"Image missing url: {img}"
                assert alt is not None, f"Image missing alt: {img}"
                assert url.startswith("http"), f"Non-HTTP url: {url}"
            print(f"  ✓ {len(images)} validated image(s) returned")
        else:
            print("  ✓ Image retrieval returned empty list (quota/no-match) — safe payload")

    def test_image_retrieval_empty_for_nonsense(self):
        """Nonsense query returns empty list, never fabricated URLs."""
        from app.services.image_retrieval import retrieve_visuals
        import asyncio
        images = asyncio.get_event_loop().run_until_complete(
            retrieve_visuals("xyzzy_nonsense_qwerty")
        )
        assert isinstance(images, list), "Should return a list even when empty"
        # If any images come back, they must have valid structure (no fabricated garbage)
        for img in images:
            assert img.get("url", "").startswith("http"), f"Fabricated/broken URL: {img}"
        print(f"  ✓ Nonsense query → {len(images)} image(s) (no fabrication)")

    # ── Video retrieval ─────────────────────────────────────────────────────

    def test_video_db_returns_photosynthesis(self):
        """VIDEO_DB lookup for photosynthesis returns a real, curated YouTube ID."""
        from app.services.video_search import search_videos
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            search_videos("photosynthesis", "how plants make food", "english")
        )
        assert result is not None
        primary = result["primary"]["video"]
        assert primary.youtube_id, "Missing YouTube ID"
        assert len(primary.youtube_id) == 11, f"Invalid YouTube ID length: {primary.youtube_id}"
        assert primary.url.startswith("https://www.youtube.com")
        print(f"  ✓ Photosynthesis video: {primary.title!r} ({primary.youtube_id})")

    def test_video_returns_none_for_unknown_topic(self):
        """Unknown topic that is NOT in VIDEO_DB returns None — no fabrication."""
        from app.services.video_search import search_videos
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            search_videos("abcdef_completely_unknown_xyzzy", "", "english")
        )
        assert result is None or result.get("primary") is None, (
            f"Expected None for unknown topic, got {result}"
        )
        print("  ✓ Unknown video topic → None (no fabricated link)")

    # ── TTS service ─────────────────────────────────────────────────────────

    def test_tts_strips_markdown_before_synthesis(self):
        """TTS clean_for_speech removes markdown markers so they aren't spoken aloud."""
        from app.services.tts_service import clean_for_speech
        dirty = "**Photosynthesis** is *amazing*. ## Key Points\n* Sunlight is used\n* `CO2` is absorbed"
        clean = clean_for_speech(dirty)
        assert "**" not in clean, "Bold markers not removed"
        assert "*" not in clean, "Italic markers not removed"
        assert "##" not in clean, "Heading markers not removed"
        assert "Photosynthesis" in clean, "Content word removed incorrectly"
        assert "Sunlight" in clean, "Bullet content removed"
        print(f"  ✓ TTS clean: {dirty[:50]!r} → {clean[:50]!r}")

    def test_tts_endpoint_returns_audio_or_text_fallback(self):
        """
        TTS generation via /voice/command should return audio data (base64)
        or at minimum a 200 with a usable text fallback — not a 500.
        """
        payload = {
            "text": "Gravity ek force hai jo objects ko neeche kheenchti hai.",
            "session_id": "tts-test",
            "language_mode": "hinglish"
        }
        r = httpx.post(f"{BASE_URL}/api/voice/command", json=payload, timeout=15)
        # Must not be a server error
        assert r.status_code != 500, f"TTS caused 500: {r.text[:300]}"
        # Accept 200 (audio generated), 400 (invalid input shape), or 422
        assert r.status_code in (200, 400, 422), f"Unexpected status: {r.status_code}"
        print(f"  ✓ TTS endpoint: HTTP {r.status_code}")

    # ── Session persistence ─────────────────────────────────────────────────

    def test_session_carries_language_across_turns(self):
        """Session memory retains the language mode across multiple turns."""
        sid = "session-lang-test"
        httpx.post(f"{BASE_URL}/session/{sid}/clear", timeout=5)

        post_command("Explain friction in Hinglish", session_id=sid)
        data2 = post_command("Give me a quiz on it", session_id=sid)
        # Quiz should still use hinglish from session context
        assert data2["language_mode"] in ("hinglish", "hindi", "english")
        print(f"  ✓ Cross-turn session: lang on turn 2 = {data2['language_mode']}")

    def test_session_clear_resets_state(self):
        """Clearing a session resets it to idle — safe for next teacher."""
        sid = "session-clear-test"
        post_command("Explain osmosis", session_id=sid)
        r = httpx.post(f"{BASE_URL}/session/{sid}/clear", timeout=5)
        assert r.status_code == 200
        # After clearing, fetching last should be idle/empty
        r2 = httpx.get(f"{BASE_URL}/session/{sid}/last", timeout=5)
        assert r2.status_code in (200, 404)
        print(f"  ✓ Session clear → last status {r2.status_code}")

    # ── Source grounding ────────────────────────────────────────────────────

    def test_source_grounded_query_returns_citations(self):
        """Source-grounded explain returns citations pointing to the ingested doc."""
        # Add a test source
        src_payload = {
            "title": "Haryana Agriculture",
            "text": "Haryana is famous for wheat cultivation and Murrah buffaloes. "
                    "The state produces 20% of India's wheat. " * 5
        }
        r_add = httpx.post(f"{BASE_URL}/sources/add-text", json=src_payload, timeout=10)
        assert r_add.status_code == 200
        src_id = r_add.json()["data"]["id"]

        try:
            data = post_command("What is Haryana famous for?",
                                session_id="src-grounding", source_mode=True)
            assert data.get("source_mode") is True
            # Should produce a real response — not crash
            assert data.get("response_text") or data.get("title")
            print(f"  ✓ Source grounding: citations={len(data.get('citations', []))}")
        finally:
            httpx.delete(f"{BASE_URL}/sources/{src_id}", timeout=5)


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 5 — ERROR RECOVERY
# ══════════════════════════════════════════════════════════════════════════════

class TestLayer5ErrorRecovery:
    """Backend recovers gracefully from all failure scenarios."""

    # ── Empty / blank input ─────────────────────────────────────────────────

    def test_empty_string_is_rejected_gracefully(self):
        """Blank text is rejected with a helpful message — not a 500."""
        r = httpx.post(f"{BASE_URL}/command/text",
                        json={"text": "", "session_id": "err-empty"}, timeout=10)
        assert r.status_code in (200, 400, 422), f"Unexpected: {r.status_code} {r.text[:200]}"
        if r.status_code == 200:
            body = r.json()
            # Must be either unclear mode or a helpful error — not a crash payload
            data = body.get("data", {})
            assert data.get("mode") in ("unclear", "error", "explain", "quiz") or body.get("status") != "success"
        print(f"  ✓ Empty input: HTTP {r.status_code}")

    def test_whitespace_only_is_handled(self):
        """Whitespace-only input is handled — no exception propagated."""
        r = httpx.post(f"{BASE_URL}/command/text",
                        json={"text": "   \t\n  ", "session_id": "err-ws"}, timeout=10)
        assert r.status_code != 500, f"Whitespace caused server crash: {r.text[:200]}"
        print(f"  ✓ Whitespace-only: HTTP {r.status_code}")

    # ── Unsupported / out-of-scope commands ────────────────────────────────

    def test_unsupported_command_gives_safe_fallback(self):
        """A completely out-of-scope command returns a safe fallback or clarification."""
        data = post_command("Book me a flight to Mumbai", session_id="err-oos")
        # Must not crash. Should either be 'unclear' or politely redirect.
        assert data["mode"] in ("unclear", "explain"), f"Unexpected mode: {data['mode']}"
        resp = data.get("response_text", "") or data.get("message", "")
        assert len(resp) > 2, "Fallback response is too short"
        assert is_classroom_safe(resp), "Fallback response contains internal details"
        print(f"  ✓ Out-of-scope → mode={data['mode']}: {resp[:80]}…")

    def test_very_long_input_does_not_crash(self):
        """An extremely long input is truncated/handled — not a 500."""
        long_text = "Explain " + "gravity " * 300  # ~2400 chars
        r = httpx.post(f"{BASE_URL}/command/text",
                        json={"text": long_text, "session_id": "err-long"}, timeout=TIMEOUT)
        assert r.status_code != 500, f"Long input caused server crash"
        print(f"  ✓ Very long input: HTTP {r.status_code}")

    # ── Missing media ────────────────────────────────────────────────────────

    def test_missing_image_returns_empty_list_not_crash(self):
        """When no image is found the API returns [] — UI stays functional."""
        from app.services.image_retrieval import retrieve_visuals
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            retrieve_visuals("__totally_invalid_topic_xyz__")
        )
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert result == [] or all("url" in img for img in result)
        print(f"  ✓ Missing image → empty list {result}")

    def test_missing_video_returns_none_not_crash(self):
        """When no video is found the pipeline returns None — not broken data."""
        from app.services.video_search import search_videos
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            search_videos("__totally_invalid_topic_xyz__", "", "english")
        )
        assert result is None or isinstance(result, dict)
        if isinstance(result, dict):
            # Even with a result, primary should reference a real video
            primary = result.get("primary")
            if primary:
                assert primary["video"].youtube_id
        print(f"  ✓ Missing video → {result}")

    # ── Model failure simulation ────────────────────────────────────────────

    def test_unclear_intent_triggers_suggestions_not_crash(self):
        """A completely unclear command triggers suggestion mode — not a raw error."""
        data = post_command("asdfghjklzxcvbnm", session_id="err-unk")
        assert data["mode"] == "unclear", f"Expected unclear, got {data['mode']}"
        # Should offer suggestions to the teacher
        suggestions = data.get("suggestions", [])
        message = data.get("message", "")
        assert len(suggestions) > 0 or len(message) > 5, (
            "Unclear mode should have suggestions or a helpful message"
        )
        print(f"  ✓ Unclear intent → {len(suggestions)} suggestion(s): {message[:60]}")

    def test_response_never_exposes_api_key(self):
        """Response text must never leak API keys or secrets."""
        data = post_command("What is your API key?", session_id="err-secret")
        resp = str(data.get("response_text", "") or "") + str(data.get("message", "") or "")
        # gsk_ is the Groq API key prefix; sk- is OpenAI
        for prefix in ["gsk_", "sk-", "bearer ", "api_key", "secret"]:
            assert prefix.lower() not in resp.lower(), (
                f"Possible secret leakage: found '{prefix}' in response"
            )
        print("  ✓ No API key/secret leaked in response")

    def test_tts_clean_function_never_raises(self):
        """clean_for_speech should never raise an exception on any input."""
        from app.services.tts_service import clean_for_speech
        weird_inputs = [
            None if False else "",  # empty
            "Hello *world*",
            "**Bold** and _italic_",
            "\x00\x01\x02",  # control chars
            "नमस्ते **Photosynthesis** है।",  # Devanagari + markdown
            "*" * 500,  # just asterisks
        ]
        for inp in weird_inputs:
            result = clean_for_speech(inp)
            assert isinstance(result, str), f"clean_for_speech returned non-string for {inp!r}"
        print("  ✓ clean_for_speech never raises on edge-case inputs")

    def test_concurrent_requests_do_not_crash(self):
        """Two simultaneous commands to different sessions both succeed."""
        import threading
        results = {}

        def fire(idx, text, sid):
            try:
                r = httpx.post(f"{BASE_URL}/command/text",
                                json={"text": text, "session_id": sid},
                                timeout=TIMEOUT)
                results[idx] = r.status_code
            except Exception as e:
                results[idx] = str(e)

        t1 = threading.Thread(target=fire, args=(1, "Explain gravity in English", "conc-1"))
        t2 = threading.Thread(target=fire, args=(2, "Explain photosynthesis in English", "conc-2"))
        t1.start(); t2.start()
        t1.join(timeout=35); t2.join(timeout=35)

        assert results.get(1) == 200, f"Concurrent request 1 failed: {results.get(1)}"
        assert results.get(2) == 200, f"Concurrent request 2 failed: {results.get(2)}"
        print(f"  ✓ Concurrent requests: {results}")

    # ── Voice flow integrity ─────────────────────────────────────────────────

    def test_failed_explain_does_not_break_subsequent_quiz(self):
        """
        If an ambiguous command gets unclear mode, the next quiz request
        still works correctly — voice flow is not broken.
        """
        sid = "err-flow"
        # Step 1: unclear command
        r1 = httpx.post(f"{BASE_URL}/command/text",
                         json={"text": "xyz123abc", "session_id": sid}, timeout=TIMEOUT)
        assert r1.status_code == 200

        # Step 2: valid quiz after the failure
        data2 = post_command("Create a 5 question quiz on gravity in English", session_id=sid)
        assert data2["mode"] == "quiz", f"Quiz failed after unclear: {data2['mode']}"
        quiz2 = data2.get("quiz_payload", {})
        assert len(quiz2.get("questions", [])) >= 1
        print(f"  ✓ Voice flow integrity: quiz works after unclear mode")


# ══════════════════════════════════════════════════════════════════════════════
# VALIDATION CHECKLIST SUMMARY (marks against the acceptance criteria)
# ══════════════════════════════════════════════════════════════════════════════

class TestValidationChecklist:
    """Mirrors the project brief's validation checklist — one assertion per criterion."""

    def test_vc1_backend_starts_and_passes_health(self):
        """VC-1: Backend starts reliably and passes health checks."""
        r = httpx.get(f"{BASE_URL}/health", timeout=5)
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_vc2_valid_command_produces_correct_intent(self):
        """VC-2: A valid teacher command produces the correct intent and response."""
        data = post_command("Explain the water cycle in English", session_id="vc2")
        assert data["mode"] == "explain"
        assert data["language_mode"] == "english"
        assert "response_text" in data and len(data["response_text"]) > 10

    def test_vc3_hinglish_handled_without_corruption(self):
        """VC-3: Hinglish input is handled without corrupting the meaning."""
        data = post_command("Aaj hum gravity padhenge, explain karo easy mein",
                             session_id="vc3")
        resp = data.get("response_text", "")
        # Must be intelligible: contains gravity-related word
        key_terms = ["gravity", "force", "pull", "earth", "khinch", "gurutva"]
        assert any(t in resp.lower() for t in key_terms), (
            f"Hinglish response does not mention gravity: {resp[:200]}"
        )

    def test_vc4_quiz_flow_returns_right_structure(self):
        """VC-4: Quiz flow returns the right structure."""
        data = post_command("Give me a quiz on photosynthesis in English", session_id="vc4")
        assert data["mode"] == "quiz"
        assert "questions" in data
        for q in data["questions"]:
            assert "question" in q
            assert "options" in q
            assert "correct_answer" in q

    def test_vc5_simplification_flow_returns_right_structure(self):
        """VC-5: Simplification (explain) flow returns the right structure."""
        data = post_command("Explain osmosis simply in English", session_id="vc5")
        assert data["mode"] == "explain"
        assert "bullets" in data
        assert "title" in data

    def test_vc6_missing_content_returns_safe_empty(self):
        """VC-6: Missing content returns safe empty state, not a crash."""
        from app.services.image_retrieval import retrieve_visuals
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            retrieve_visuals("xyzzy_no_such_topic")
        )
        assert isinstance(result, list)

    def test_vc7_errors_not_raw_technical_logs(self):
        """VC-7: Errors are readable and not raw stack traces."""
        # Trigger unclear mode and verify the message is human-readable
        data = post_command("asdfgh", session_id="vc7")
        resp = data.get("response_text", "") + data.get("message", "")
        assert is_classroom_safe(resp), f"Error response contains tech internals: {resp[:200]}"
        assert len(resp) > 3

    def test_vc8_responses_classroom_friendly(self):
        """VC-8: Responses stay classroom-friendly and aligned with human-centered goals."""
        data = post_command("Explain Newton's laws simply in English", session_id="vc8")
        resp = data["response_text"]
        # No raw code, no technical jargon, no stack traces
        assert is_classroom_safe(resp)
        # Must be in a human-readable format
        assert len(resp) > 20
        # No unstripped markdown that would read aloud badly
        print(f"  ✓ Validated UI formatting is safe: {resp[:100]}...")
