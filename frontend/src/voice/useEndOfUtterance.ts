"use client";

/**
 * useEndOfUtterance.ts
 * ─────────────────────────────────────────────────────────
 * Manages a rolling silence timer.
 *
 * Call `onSpeechActivity(transcript)` every time SpeechRecognition
 * emits any result (interim or final).  If no activity arrives for
 * `thresholdMs` milliseconds the latest transcript is validated and
 * passed to `onUtterance`.
 *
 * Rules that prevent dispatch:
 *  - transcript shorter than VOICE_CONFIG.minUtteranceLength
 *  - transcript is in VOICE_CONFIG.fillerPhrases
 *  - transcript starts with a VOICE_CONFIG.fillerPrefix
 */

import { useRef, useCallback, useEffect } from "react";
import { VOICE_CONFIG } from "./voiceConfig";

// ─── Types ────────────────────────────────────────────────────────────────────

interface UseEndOfUtteranceProps {
  /** Called with the finalised transcript when silence threshold is reached. */
  onUtterance: (transcript: string) => void;
  /** Silence duration in ms before finalising. Defaults to VOICE_CONFIG.silenceThresholdMs */
  thresholdMs?: number;
  /** Whether the timer is active at all. */
  enabled: boolean;
}

interface UseEndOfUtteranceReturn {
  /**
   * Call this on every SpeechRecognition result event.
   * Resets the silence timer and stores the latest transcript.
   */
  onSpeechActivity: (transcript: string) => void;
  /** Immediately cancel any pending timer without dispatching. */
  cancelTimer: () => void;
}

// ─── Validation ───────────────────────────────────────────────────────────────

function isMeaningfulUtterance(text: string): boolean {
  const t = text.toLowerCase().trim();

  if (t.length < VOICE_CONFIG.minUtteranceLength) return false;

  // Exact match against filler list
  if (VOICE_CONFIG.fillerPhrases.includes(t)) return false;

  // Starts with a filler prefix
  if (VOICE_CONFIG.fillerPrefixes.some((p) => t.startsWith(p))) return false;

  // Contains only punctuation / numbers
  if (/^[\d\s.,!?]+$/.test(t)) return false;

  return true;
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useEndOfUtterance({
  onUtterance,
  thresholdMs,
  enabled,
}: UseEndOfUtteranceProps): UseEndOfUtteranceReturn {
  const timerRef          = useRef<ReturnType<typeof setTimeout> | null>(null);
  const latestTranscript  = useRef<string>("");
  const onUtteranceRef    = useRef(onUtterance);
  const enabledRef        = useRef(enabled);
  const threshold         = thresholdMs ?? VOICE_CONFIG.silenceThresholdMs;

  // Keep refs fresh without re-creating callbacks
  useEffect(() => { onUtteranceRef.current = onUtterance; }, [onUtterance]);
  useEffect(() => { enabledRef.current     = enabled;     }, [enabled]);

  const cancelTimer = useCallback(() => {
    if (timerRef.current !== null) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const fireUtterance = useCallback(() => {
    const text = latestTranscript.current.trim();
    latestTranscript.current = "";
    timerRef.current = null;

    if (!enabledRef.current) return;
    if (!isMeaningfulUtterance(text)) {
      console.info("[useEndOfUtterance] discarded non-meaningful utterance:", text);
      return;
    }

    onUtteranceRef.current(text);
  }, []);

  const onSpeechActivity = useCallback(
    (transcript: string) => {
      if (!enabledRef.current) return;

      // Accumulate / update transcript
      if (transcript.trim()) {
        latestTranscript.current = transcript;
      }

      // Reset the silence timer
      cancelTimer();
      timerRef.current = setTimeout(fireUtterance, threshold);
    },
    [cancelTimer, fireUtterance, threshold],
  );

  // Cleanup on unmount or when disabled
  useEffect(() => {
    if (!enabled) {
      cancelTimer();
      latestTranscript.current = "";
    }
    return () => {
      cancelTimer();
    };
  }, [enabled, cancelTimer]);

  return { onSpeechActivity, cancelTimer };
}
