/**
 * useWakeWord.ts
 * ─────────────────────────────────────────────────────────
 * Maintains a continuous SpeechRecognition stream and fires
 * `onWake` / `onStop` when the normalised transcript contains
 * a configured wake word or stop word.
 *
 * This hook owns ONE recognition instance.  It is NOT the same
 * instance used for command capture — that is managed by voiceRouter.
 */

import { useEffect, useRef, useCallback } from "react";
import { VOICE_CONFIG } from "./voiceConfig";

// ─── Types ────────────────────────────────────────────────────────────────────

interface UseWakeWordProps {
  /** Fire when a wake phrase is detected. */
  onWake: () => void;
  /** Fire when a stop phrase is detected. */
  onStop: () => void;
  /** Language for SpeechRecognition. Defaults to VOICE_CONFIG.lang */
  lang?: string;
  /** Whether this hook should run at all. */
  enabled: boolean;
}

// ─── Normalisation helper ─────────────────────────────────────────────────────

function normalise(text: string): string {
  return text.toLowerCase().trim().replace(/[.,!?]+$/, "");
}

function containsPhrase(haystack: string, phrases: readonly string[]): boolean {
  const h = normalise(haystack);
  return phrases.some((p) => h.includes(normalise(p)));
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useWakeWord({
  onWake,
  onStop,
  lang,
  enabled,
}: UseWakeWordProps): void {
  const recRef     = useRef<any>(null);
  const enabledRef = useRef(enabled);
  const onWakeRef  = useRef(onWake);
  const onStopRef  = useRef(onStop);

  // Keep refs fresh so the recognition callbacks always see the latest props
  useEffect(() => { enabledRef.current = enabled; }, [enabled]);
  useEffect(() => { onWakeRef.current  = onWake;  }, [onWake]);
  useEffect(() => { onStopRef.current  = onStop;  }, [onStop]);

  const startRecognition = useCallback(() => {
    if (typeof window === "undefined") return;
    const SR =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;
    if (!SR) {
      console.warn("[useWakeWord] SpeechRecognition not supported in this browser.");
      return;
    }

    // Tear down any previous instance
    try { recRef.current?.stop(); } catch (_) {}

    const rec = new SR();
    rec.continuous     = true;
    rec.interimResults = true;
    rec.lang           = lang ?? VOICE_CONFIG.lang;

    rec.onresult = (event: any) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const text = event.results[i][0].transcript as string;

        if (containsPhrase(text, VOICE_CONFIG.stopWords)) {
          onStopRef.current();
          return;
        }
        if (containsPhrase(text, VOICE_CONFIG.wakeWords)) {
          onWakeRef.current();
          return;
        }
      }
    };

    rec.onerror = (e: any) => {
      // Transient errors: restart silently
      if (
        e.error === "no-speech" ||
        e.error === "network"   ||
        e.error === "aborted"
      ) {
        setTimeout(() => {
          if (enabledRef.current) startRecognition();
        }, 800);
      } else {
        console.error("[useWakeWord] recognition error:", e.error);
      }
    };

    rec.onend = () => {
      // Auto-restart so we keep listening for wake words
      if (enabledRef.current) {
        setTimeout(() => startRecognition(), 300);
      }
    };

    recRef.current = rec;
    try {
      rec.start();
    } catch (err) {
      console.error("[useWakeWord] failed to start:", err);
    }
  }, [lang]);

  useEffect(() => {
    if (enabled) {
      startRecognition();
    } else {
      try { recRef.current?.stop(); } catch (_) {}
      recRef.current = null;
    }

    return () => {
      try { recRef.current?.stop(); } catch (_) {}
      recRef.current = null;
    };
  }, [enabled, startRecognition]);
}
