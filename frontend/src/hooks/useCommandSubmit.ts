/**
 * useCommandSubmit.ts — Command submission with full state sync
 *
 * Connects the teacher's command to the backend and wires every part of the
 * response into the correct frontend store:
 *
 *   1. Set loading state + avatar to 'thinking'
 *   2. Add user command to transcript immediately (optimistic)
 *   3. Call POST /api/command via apiClient (relative URL, timeout-safe)
 *   4. On success:
 *      a. Adapt flat backend payload → nested component shape
 *      b. Transition app state to 'explaining' or 'quiz_active'
 *      c. Dispatch RESPONSE_RECEIVED → event bus (avatar reacts)
 *      d. Dispatch TTS_START → JULI-E starts speaking animation
 *      e. Play audio_base64 if present
 *      f. Update transcript with assistant response + mode + language
 *      g. Persist preferences to backend session
 *   5. On failure:
 *      a. Transition to 'error' state
 *      b. Dispatch ERROR event
 *      c. JULI-E returns to idle (never stuck in 'thinking')
 *      d. Transcript entry marked as failed
 */
import { useState, useCallback, useRef } from "react";
import { submitCommand, saveSessionPrefs, AssistantPayload } from "../lib/apiClient";
import { useAppState } from "../state/useAppState";
import { useAppEvents } from "../state/useAppEvents";
import { useTranscriptStore } from "../state/transcriptStore";
import { getSessionId } from "../state/sessionStore";

// ─── Payload Adapter ──────────────────────────────────────────────────────────
//
// The backend returns a *flat* AssistantPayload with fields like:
//   title, bullets, answer_text, example, recap, questions, visuals, videos, etc.
//
// The frontend card components expect *nested* shapes:
//   payload.explanation = { title, points, analogy }
//   payload.quiz        = { questions: [...] }
//   payload.visual      (singular VisualRef)
//   payload.best_video  (singular VideoRef)
//   payload.summary     (string)
//
// This adapter bridges the two worlds without changing either side.
// ─────────────────────────────────────────────────────────────────────────────

function adaptPayload(raw: AssistantPayload): AssistantPayload & {
  explanation?: { title: string; points: string[]; analogy: string };
  quiz?: { questions: any[] };
  visual?: any;
  best_video?: any;
  alternative_videos?: any[];
  summary?: string;
} {
  const adapted: any = { ...raw };

  // ── Explain card: { title, points (from bullets), analogy (from example or recap) }
  if (raw.mode === "explain" || raw.mode === "example" || raw.mode === "simpler") {
    adapted.explanation = {
      title: raw.title || "Explanation",
      points: raw.bullets && raw.bullets.length > 0
        ? raw.bullets
        : raw.answer_text
          ? raw.answer_text
              // Strip markdown bold markers and asterisks
              .replace(/\*\*/g, "")
              .replace(/\*/g, "")
              .split(/\n+/)
              .map((s: string) => s.replace(/^[-•]\s*/, "").trim())
              .filter((s: string) => s.length > 0)
          : [],
      analogy: raw.example || raw.recap || "",
    };
    // Fallback summary for MediaRail
    adapted.summary = raw.recap || raw.example || "";
  }

  // ── Quiz card: flatten questions array
  if (raw.mode === "quiz" || raw.mode === "ask_question") {
    const qs = raw.questions && raw.questions.length > 0 ? raw.questions : [];
    adapted.quiz = {
      questions: qs.map((q: any) => ({
        question: q.question,
        options: q.options || [],
        // Handle both correct_index and correct_answer (string→index)
        correct_index:
          q.correct_index != null
            ? q.correct_index
            : q.options
              ? q.options.findIndex((o: string) => o === q.correct_answer)
              : 0,
        explanation: q.explanation || "",
      })),
    };
  }

  // ── Visuals: take first item from the visuals array
  if (raw.visuals && raw.visuals.length > 0) {
    const v = raw.visuals[0] as any;
    adapted.visual = {
      src: v.url,
      alt: v.alt_text || v.title || v.description || "Visual",
    };
  }

  // ── Videos: unwrap the nested videos object
  if (raw.videos) {
    const vids = raw.videos as any;
    
    const mapVideo = (v: any) => ({
      title: v.title,
      thumbnail: v.youtube_id ? `https://img.youtube.com/vi/${v.youtube_id}/hqdefault.jpg` : "",
      source: v.url || (v.youtube_id ? `https://www.youtube.com/watch?v=${v.youtube_id}` : ""),
      reason: "Recommended video"
    });

    if (vids.best_video) {
      adapted.best_video = mapVideo(vids.best_video);
    }
    
    if (vids.candidate_videos && Array.isArray(vids.candidate_videos)) {
      adapted.alternative_videos = vids.candidate_videos.map(mapVideo);
    } else {
      adapted.alternative_videos = [];
    }
  }

  return adapted;
}

// ─── Audio Player ─────────────────────────────────────────────────────────────

export function playAudio(
  base64DataUri: string,
  onEnded?: () => void,
  onDuration?: (duration: number) => void
): HTMLAudioElement | null {
  try {
    const audio = new Audio(base64DataUri);
    audio.volume = 1.0;
    if (onEnded) audio.onended = onEnded;
    if (onDuration) {
      audio.onloadedmetadata = () => {
        if (audio.duration && !isNaN(audio.duration)) {
          onDuration(audio.duration);
        }
      };
      // fallback in case loadedmetadata already fired or fails
      setTimeout(() => {
        if (audio.duration && !isNaN(audio.duration)) {
          onDuration(audio.duration);
        }
      }, 500);
    }
    audio.play().catch((e) => {
      console.warn("[useCommandSubmit] Audio play blocked:", e.message);
      if (onEnded) onEnded();
    });
    return audio;
  } catch (e) {
    console.warn("[useCommandSubmit] Could not create Audio:", e);
    if (onEnded) onEnded();
    return null;
  }
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export const useCommandSubmit = () => {
  const { state, transitionTo } = useAppState();
  const { dispatch } = useAppEvents();
  const { addEntry, updateLastResponse } = useTranscriptStore();

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const highlightIntervalRef = useRef<any>(null);

  const submit = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed) return;

      const sessionId = getSessionId(); // stable UUID — never hardcoded

      // Clean up previous speech/highlighting if any
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      if (highlightIntervalRef.current) {
        clearInterval(highlightIntervalRef.current);
        highlightIntervalRef.current = null;
      }
      import("../state/speechStore").then(({ useSpeechStore }) => {
        useSpeechStore.getState().reset();
      });

      // ── 1. Optimistic UI: loading immediately ─────────────────────────────
      setIsLoading(true);
      setError(null);
      transitionTo("processing");
      dispatch({ type: "COMMAND_SUBMITTED" });

      // ── 2. Add user turn to transcript before API call ────────────────────
      addEntry(trimmed, "…thinking…");

      // ── 3. Call the backend ───────────────────────────────────────────────
      const response = await submitCommand({
        text: trimmed,
        sessionId,
        sourceMode: state.topBar.sourceMode ?? false,
      });

      setIsLoading(false);

      // ── 4a. Error path ────────────────────────────────────────────────────
      if (response.status === "error" || !response.data) {
        const msg =
          response.error?.message ||
          "The assistant ran into a problem. Please try again.";

        setError(msg);
        transitionTo("error", { error: response.error });
        dispatch({ type: "ERROR" });

        // Update transcript with error note instead of leaving "…thinking…"
        updateLastResponse(`[Error] ${msg}`);
        return;
      }

      // ── 4b. Adapt flat backend payload → nested component shapes ──────────
      const rawPayload = response.data;
      const payload = adaptPayload(rawPayload);
      const mode = payload.mode || "explain";

      // Determine which canvas state to transition to
      let nextState: "explaining" | "quiz_active" = "explaining";
      if (mode === "quiz" || mode === "ask_question") nextState = "quiz_active";

      // Transition app state and attach adapted payload for ResponseRenderer
      transitionTo(nextState, { payload });

      // Fire RESPONSE_RECEIVED so event-bus subscribers (JuliEPanel, etc.) react
      dispatch({ type: "RESPONSE_RECEIVED", payload });

      // Fire TTS_START so JULI-E enters the speaking animation
      dispatch({ type: "TTS_START" });

      const rawText =
        payload.answer_text ||
        payload.response_text ||
        payload.message ||
        "";
      const cleanSpokenText = rawText.replace(/\*\*/g, "").replace(/\*/g, "");

      const startHighlighting = (durationSeconds: number) => {
        import("../state/speechStore").then(({ useSpeechStore }) => {
          const store = useSpeechStore.getState();
          store.reset();
          store.setPlaying(true);
          store.setSpokenText(cleanSpokenText);

          const words = cleanSpokenText.split(/\s+/).filter(w => w.length > 0);
          const wordCount = words.length;
          if (wordCount === 0) return;

          const durationMs = durationSeconds * 1000;
          const stepMs = durationMs / wordCount;

          let currentIdx = 0;
          store.setWordIndex(0);

          highlightIntervalRef.current = setInterval(() => {
            currentIdx++;
            if (currentIdx < wordCount) {
              store.setWordIndex(currentIdx);
            } else {
              clearInterval(highlightIntervalRef.current);
              highlightIntervalRef.current = null;
            }
          }, stepMs);
        });
      };

      const stopHighlighting = () => {
        if (highlightIntervalRef.current) {
          clearInterval(highlightIntervalRef.current);
          highlightIntervalRef.current = null;
        }
        import("../state/speechStore").then(({ useSpeechStore }) => {
          useSpeechStore.getState().reset();
        });
      };

      // ── 4c. Play audio if backend returned TTS audio_base64 ───────────────
      if (payload.audio_base64) {
        const audio = playAudio(
          payload.audio_base64,
          () => {
            dispatch({ type: "TTS_END" });
            stopHighlighting();
          },
          (duration) => {
            startHighlighting(duration);
          }
        );
        audioRef.current = audio;
      } else {
        startHighlighting(3.0);
        setTimeout(() => {
          dispatch({ type: "TTS_END" });
          stopHighlighting();
        }, 3000);
      }

      // ── 4d. Update transcript with assistant response ─────────────────────
      // Strip markdown bold markers before showing in transcript
      const assistantText = cleanSpokenText || (payload.title ? `[${payload.title}]` : "") || "…";

      updateLastResponse(assistantText, {
        mode,
        languageMode: payload.language_mode,
      });

      // ── 4e. Persist lightweight session preferences to the backend ─────────
      // Fire-and-forget — we don't block the UI for this
      saveSessionPrefs(sessionId, {
        language_mode: payload.language_mode,
        hands_free: state.topBar.handsFree ?? false,
        source_mode: state.topBar.sourceMode ?? false,
      }).catch((err) => {
        console.warn("[useCommandSubmit] Could not persist session prefs:", err);
      });
    },
    [state, transitionTo, dispatch, addEntry, updateLastResponse]
  );

  return { submit, isLoading, error };
};
