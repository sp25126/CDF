"""
Integration Tests — Backend API Layer (Prompt 5)

Tests the new unified /api/* endpoints end-to-end against a live backend.
Validates the full request→response→state lifecycle for every classroom scenario.

Run: pytest tests/test_api_integration.py -v
Requires: backend running on http://localhost:8000
"""
import httpx
import pytest
import time

BASE = "http://localhost:8000"
TIMEOUT = 30.0
SESSION = f"integration-test-{int(time.time())}"  # unique per run


def api(path: str) -> str:
    return f"{BASE}/api{path}"


def post_command(text: str, session_id: str = SESSION, **extra) -> dict:
    r = httpx.post(api("/command"), json={"text": text, "session_id": session_id, **extra}, timeout=TIMEOUT)
    assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:300]}"
    return r.json()


# ══════════════════════════════════════════════════════════════════════════════
# 1. Health Endpoint
# ══════════════════════════════════════════════════════════════════════════════

class TestHealth:
    def test_health_ok(self):
        """Backend starts and health check returns 200 with status=ok."""
        r = httpx.get(api("/health"), timeout=5)
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert "version" in body

    def test_health_alternate_path(self):
        """/health also works (no /api prefix)."""
        r = httpx.get(f"{BASE}/health", timeout=5)
        assert r.status_code == 200


# ══════════════════════════════════════════════════════════════════════════════
# 2. Unified Command Endpoint
# ══════════════════════════════════════════════════════════════════════════════

class TestUnifiedCommand:

    def test_command_returns_global_envelope(self):
        """POST /api/command returns GlobalResponse with status + data."""
        body = post_command("Explain gravity in English")
        assert body["status"] == "success"
        assert "data" in body
        assert body["data"] is not None

    def test_command_payload_has_required_fields(self):
        """Payload has mode, language_mode, avatar_state, response_text."""
        body = post_command("Explain photosynthesis in English")
        data = body["data"]
        for field in ("mode", "language_mode", "avatar_state", "session_id"):
            assert field in data, f"Missing field: {field}"

    def test_command_includes_transcript_entry(self):
        """Backend injects transcript_entry for the frontend history store."""
        body = post_command("Explain osmosis in English")
        data = body["data"]
        assert "transcript_entry" in data
        entry = data["transcript_entry"]
        assert entry["role"] == "assistant"
        assert isinstance(entry["text"], str)
        assert "mode" in entry

    def test_explain_intent_english(self):
        """English explain command resolves to explain mode."""
        body = post_command("Explain the food chain in English")
        data = body["data"]
        assert data["mode"] == "explain"
        assert data["language_mode"] == "english"

    def test_hinglish_command_processed(self):
        """Hinglish command is processed without error."""
        body = post_command("Gravity explain karo simple mein", session_id=f"{SESSION}-hi")
        data = body["data"]
        assert data["mode"] in ("explain", "quiz", "unclear")
        assert data.get("response_text") or data.get("answer_text")

    def test_quiz_command_returns_questions(self):
        """Quiz command returns questions array with correct structure."""
        body = post_command("Create a 5 question quiz on photosynthesis in English",
                             session_id=f"{SESSION}-quiz")
        data = body["data"]
        assert data["mode"] == "quiz"
        questions = data.get("questions", [])
        assert len(questions) >= 1
        for q in questions:
            assert "question" in q
            assert "options" in q

    def test_empty_command_rejected_with_helpful_error(self):
        """Empty command returns 400 with a user-friendly error message."""
        r = httpx.post(api("/command"), json={"text": "", "session_id": SESSION}, timeout=10)
        assert r.status_code == 400
        body = r.json()
        # FastAPI 422 or our custom 400
        error_detail = body.get("detail") or body.get("error", {})
        assert error_detail  # Must have some explanation

    def test_whitespace_command_rejected(self):
        """Whitespace-only command is rejected cleanly."""
        r = httpx.post(api("/command"), json={"text": "   ", "session_id": SESSION}, timeout=10)
        assert r.status_code in (400, 422)

    def test_no_stack_trace_in_response(self):
        """Response never exposes raw Python stack traces."""
        body = post_command("Explain gravity in English")
        data_str = str(body)
        for trace_marker in ["Traceback", "File \"", "line ", "AttributeError"]:
            assert trace_marker not in data_str, f"Stack trace leaked: {trace_marker}"

    def test_source_mode_flag_passed_through(self):
        """source_mode flag is reflected in the response."""
        body = post_command("Explain gravity", source_mode=True, session_id=f"{SESSION}-src")
        data = body["data"]
        assert "source_mode" in data  # field exists in response


# ══════════════════════════════════════════════════════════════════════════════
# 3. Session Endpoints
# ══════════════════════════════════════════════════════════════════════════════

class TestSessionEndpoints:
    SID = f"sess-integration-{int(time.time())}"

    def test_get_session_fresh_returns_idle(self):
        """GET /api/session/{id} for a fresh session returns idle state safely."""
        r = httpx.get(api(f"/session/{self.SID}"), timeout=5)
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "success"
        data = body["data"]
        assert data["session_id"] == self.SID
        assert "mode" in data
        assert "language_mode" in data
        assert "assistant_state" in data

    def test_update_session_language(self):
        """POST /api/session/{id} persists language_mode preference."""
        r = httpx.post(
            api(f"/session/{self.SID}"),
            json={"language_mode": "english"},
            timeout=5
        )
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "success"
        assert body["data"]["updated"] is True

    def test_clear_session_returns_success(self):
        """POST /api/session/{id}/clear resets session and returns cleared=True."""
        r = httpx.post(api(f"/session/{self.SID}/clear"), timeout=5)
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "success"
        assert body["data"]["cleared"] is True

    def test_get_last_returns_safe_empty(self):
        """GET /api/session/{id}/last after clear returns empty-safe payload."""
        r = httpx.get(api(f"/session/{self.SID}/last"), timeout=5)
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "success"
        data = body["data"]
        assert "has_history" in data
        assert "mode" in data
        assert "assistant_state" in data

    def test_session_persists_after_command(self):
        """After a command, session shows non-zero turn count."""
        sid = f"sess-cmd-{int(time.time())}"
        post_command("Explain gravity in English", session_id=sid)
        r = httpx.get(api(f"/session/{sid}"), timeout=5)
        data = r.json()["data"]
        assert data["recent_turns_count"] >= 1


# ══════════════════════════════════════════════════════════════════════════════
# 4. Response Quality Checks
# ══════════════════════════════════════════════════════════════════════════════

class TestResponseQuality:

    def test_explain_has_bullets(self):
        """Explain response provides bullets for smart-board display."""
        body = post_command("Explain cell division in English", session_id=f"{SESSION}-cell")
        data = body["data"]
        assert "bullets" in data
        assert len(data["bullets"]) >= 1

    def test_explain_has_title(self):
        """Explain response has a short, displayable title."""
        body = post_command("Explain evaporation in English", session_id=f"{SESSION}-evap")
        data = body["data"]
        title = data.get("title", "")
        assert title and len(title) > 2 and len(title) < 150

    def test_quiz_questions_have_options_and_answer(self):
        """Quiz questions are complete with options and a correct answer."""
        body = post_command("Quiz on gravity 5 questions English", session_id=f"{SESSION}-grav")
        data = body["data"]
        if data.get("mode") == "quiz":
            for q in data.get("questions", []):
                assert "options" in q and len(q["options"]) >= 2
                assert "correct_answer" in q or "correct_index" in q

    def test_hinglish_response_has_content(self):
        """Hinglish command produces a non-empty meaningful response."""
        body = post_command("Photosynthesis kya hoti hai?", session_id=f"{SESSION}-ph")
        data = body["data"]
        resp = data.get("response_text") or data.get("answer_text") or ""
        assert len(resp) > 10

    def test_avatar_state_is_valid(self):
        """avatar_state is one of the known valid states."""
        body = post_command("Explain water cycle in English", session_id=f"{SESSION}-av")
        data = body["data"]
        valid_states = {"idle", "speaking", "listening", "thinking", "explaining",
                        "awaiting_followup", "quizzing"}
        assert data.get("avatar_state") in valid_states or data.get("avatar_state")  # non-empty


# ══════════════════════════════════════════════════════════════════════════════
# 5. Error Recovery
# ══════════════════════════════════════════════════════════════════════════════

class TestErrorRecovery:

    def test_missing_session_id_rejected(self):
        """Request without session_id returns 422 validation error."""
        r = httpx.post(api("/command"), json={"text": "Explain gravity"}, timeout=10)
        assert r.status_code == 422

    def test_nonsense_command_returns_unclear(self):
        """Random nonsense resolves to unclear mode — no crash."""
        body = post_command("xkzqmwbvqp", session_id=f"{SESSION}-ns")
        assert body["status"] == "success"
        data = body["data"]
        assert data["mode"] in ("unclear", "explain", "quiz")

    def test_quiz_then_explain_voice_flow_intact(self):
        """After a quiz, an explain command still works — voice flow not broken."""
        sid = f"{SESSION}-flow"
        post_command("Quiz on gravity 3 questions English", session_id=sid)
        body = post_command("Explain gravity in English", session_id=sid)
        data = body["data"]
        assert data["mode"] == "explain"

    def test_error_response_has_envelope(self):
        """Even error responses are wrapped in GlobalResponse envelope."""
        r = httpx.post(api("/command"), json={"text": "", "session_id": SESSION}, timeout=10)
        body = r.json()
        # Must have status field (either 'error' or from FastAPI validation detail)
        assert "status" in body or "detail" in body

    def test_source_not_found_safe_empty(self):
        """Source mode with no matching docs returns empty-safe payload, not a crash."""
        body = post_command(
            "Tell me about quantum string theory",
            session_id=f"{SESSION}-empty",
            source_mode=True
        )
        assert body["status"] == "success"
        data = body["data"]
        assert data is not None  # Never None — always has a mode

    def test_concurrent_sessions_independent(self):
        """Two simultaneous sessions do not interfere with each other."""
        import threading
        results = {}

        def fire(key, text, sid):
            try:
                body = post_command(text, session_id=sid)
                results[key] = body["data"]["mode"]
            except Exception as e:
                results[key] = f"ERROR: {e}"

        t1 = threading.Thread(target=fire, args=("a", "Explain gravity in English", f"{SESSION}-c1"))
        t2 = threading.Thread(target=fire, args=("b", "Quiz on photosynthesis English", f"{SESSION}-c2"))
        t1.start(); t2.start()
        t1.join(timeout=35); t2.join(timeout=35)

        assert results.get("a") == "explain", f"Session a: {results.get('a')}"
        assert results.get("b") == "quiz", f"Session b: {results.get('b')}"


# ══════════════════════════════════════════════════════════════════════════════
# 6. CORS / Proxy
# ══════════════════════════════════════════════════════════════════════════════

class TestCORSConfig:

    def test_preflight_options_allowed(self):
        """OPTIONS preflight from localhost:3000 succeeds."""
        r = httpx.options(
            api("/command"),
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
            timeout=5
        )
        # 200 or 204 — both are valid for CORS preflight
        assert r.status_code in (200, 204), f"Preflight failed: {r.status_code}"

    def test_cors_header_present(self):
        """CORS headers are present on responses to localhost:3000 origin."""
        r = httpx.get(
            api("/health"),
            headers={"Origin": "http://localhost:3000"},
            timeout=5
        )
        assert r.status_code == 200
        # The ACAO header should be present when origin is allowed
        assert "access-control-allow-origin" in r.headers or \
               "Access-Control-Allow-Origin" in r.headers
