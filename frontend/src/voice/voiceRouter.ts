/**
 * voiceRouter.ts
 * ─────────────────────────────────────────────────────────
 * Master orchestration hook for the hands-free voice session.
 *
 * Combines:
 *   - voiceReducer (state machine)
 *   - useWakeWord  (wake / stop word detection)
 *   - useEndOfUtterance (3-second silence → dispatch)
 *   - a command-listening SpeechRecognition instance
 *
 * Public API (returned from useVoiceSession):
 *   voiceState     — current VoiceSessionState (subscribe for avatar mapping)
 *   isHandsFreeOn  — whether hands-free mode is enabled
 *   isListening    — mic is actively open
 *   isSpeechSupported — false when browser lacks SpeechRecognition
 *   enable()       — turn hands-free ON
 *   disable()      — turn hands-free OFF
 *   notifyAnswerStarted() — call when JULI-E begins speaking
 *   notifyAnswerEnded()   — call when JULI-E finishes speaking
 */

"use client";

import {
  useReducer,
  useRef,
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  voiceReducer,
  voiceStateToAvatarState,
  type VoiceSessionState,
} from "./voiceSessionState";
import { useWakeWord }        from "./useWakeWord";
import { useEndOfUtterance }  from "./useEndOfUtterance";
import { VOICE_CONFIG }       from "./voiceConfig";

// ─── Browser capability check ─────────────────────────────────────────────────

function hasSpeechRecognition(): boolean {
  if (typeof window === "undefined") return false;
  return !!(
    (window as any).SpeechRecognition ||
    (window as any).webkitSpeechRecognition
  );
}

// ─── Types ────────────────────────────────────────────────────────────────────

export interface UseVoiceSessionProps {
  /** Called with the finalised, meaningful transcript. */
  onCommand: (text: string) => void;
  /** Called on every voice state change so the parent can update avatarState. */
  onStateChange?: (avatarState: "idle" | "listening" | "thinking" | "speaking" | "waving") => void;
}

export interface UseVoiceSessionReturn {
  voiceState: VoiceSessionState;
  isHandsFreeOn: boolean;
  isListening: boolean;
  isSpeechSupported: boolean;
  enable: () => void;
  disable: () => void;
  notifyAnswerStarted: () => void;
  notifyAnswerEnded: () => void;
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useVoiceSession({
  onCommand,
  onStateChange,
}: UseVoiceSessionProps): UseVoiceSessionReturn {
  // ── Core state machine ─────────────────────────────────────────────────────
  const [voiceState, dispatch] = useReducer(voiceReducer, "idle");
  const voiceStateRef          = useRef<VoiceSessionState>("idle");
  voiceStateRef.current        = voiceState;

  // ── Derived flags ──────────────────────────────────────────────────────────
  const isHandsFreeOn = voiceState !== "idle";
  const isListening   =
    voiceState === "wake_listening" ||
    voiceState === "command_listening";

  // ── Speech recognition for command capture ─────────────────────────────────
  const commandRecRef = useRef<any>(null);
  const [isSpeechSupported] = useState(() => hasSpeechRecognition());

  // ── Propagate avatar state changes ────────────────────────────────────────
  const onStateChangeRef = useRef(onStateChange);
  useEffect(() => { onStateChangeRef.current = onStateChange; }, [onStateChange]);

  useEffect(() => {
    const avatarState = voiceStateToAvatarState(voiceState);
    onStateChangeRef.current?.(avatarState);
  }, [voiceState]);

  // ── onUtterance: validate → dispatch ──────────────────────────────────────
  const onCommandRef = useRef(onCommand);
  useEffect(() => { onCommandRef.current = onCommand; }, [onCommand]);

  const handleUtterance = useCallback((text: string) => {
    if (voiceStateRef.current !== "command_listening") return;
    dispatch({ type: "SILENCE_TIMEOUT", transcript: text });
    // Give reducer time to move to "processing" before dispatching
    setTimeout(() => {
      dispatch({ type: "COMMAND_SENT" });
      onCommandRef.current(text);
    }, 0);
  }, []);

  // ── End-of-utterance silence detector ────────────────────────────────────
  const { onSpeechActivity, cancelTimer } = useEndOfUtterance({
    onUtterance: handleUtterance,
    thresholdMs: VOICE_CONFIG.silenceThresholdMs,
    enabled: voiceState === "command_listening",
  });

  // ── Command-listening SpeechRecognition ───────────────────────────────────
  const startCommandListening = useCallback(() => {
    if (!hasSpeechRecognition()) return;
    try { commandRecRef.current?.stop(); } catch (_) {}

    const SR =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;
    const rec = new SR();
    rec.continuous     = true;
    rec.interimResults = true;
    rec.lang           = VOICE_CONFIG.lang;

    rec.onresult = (event: any) => {
      let runningTranscript = "";
      for (let i = 0; i < event.results.length; i++) {
        runningTranscript += event.results[i][0].transcript + " ";
      }

      // Check for stop word even during command capture
      const norm = runningTranscript.toLowerCase().trim();
      const hasStop = VOICE_CONFIG.stopWords.some((w) =>
        norm.includes(w.toLowerCase()),
      );
      if (hasStop) {
        cancelTimer();
        dispatch({ type: "STOP_WORD" });
        stopCommandListening();
        return;
      }

      onSpeechActivity(runningTranscript.trim());
    };

    rec.onerror = (e: any) => {
      if (e.error === "no-speech") {
        // No speech is fine — the silence timer will handle dispatch
        return;
      }
      if (e.error === "network" || e.error === "aborted") {
        // Restart command recognition
        setTimeout(() => {
          if (voiceStateRef.current === "command_listening") {
            startCommandListening();
          }
        }, 600);
        return;
      }
      console.error("[CommandRec] error:", e.error);
      dispatch({ type: "ERROR", message: e.error });
    };

    rec.onend = () => {
      // If still in command_listening, restart (browser ended the session)
      if (voiceStateRef.current === "command_listening") {
        setTimeout(() => startCommandListening(), 200);
      }
    };

    commandRecRef.current = rec;
    try { rec.start(); } catch (err) {
      console.error("[CommandRec] start failed:", err);
    }
  }, [onSpeechActivity, cancelTimer]);

  const stopCommandListening = useCallback(() => {
    cancelTimer();
    try { commandRecRef.current?.stop(); } catch (_) {}
    commandRecRef.current = null;
  }, [cancelTimer]);

  // ── Start / stop command listening based on state ─────────────────────────
  useEffect(() => {
    if (voiceState === "command_listening") {
      startCommandListening();
    } else {
      stopCommandListening();
    }
  }, [voiceState, startCommandListening, stopCommandListening]);

  // ── Wake word / stop word listener (always-on when hands-free is on) ──────
  useWakeWord({
    enabled: isHandsFreeOn && voiceState === "wake_listening",
    onWake: useCallback(() => {
      if (voiceStateRef.current === "wake_listening") {
        dispatch({ type: "WAKE_WORD" });
      }
    }, []),
    onStop: useCallback(() => {
      if (voiceStateRef.current !== "idle") {
        dispatch({ type: "STOP_WORD" });
        stopCommandListening();
      }
    }, [stopCommandListening]),
    lang: VOICE_CONFIG.lang,
  });

  // ── Public controls ───────────────────────────────────────────────────────
  const enable = useCallback(() => dispatch({ type: "ENABLE" }), []);
  const disable = useCallback(() => {
    stopCommandListening();
    dispatch({ type: "DISABLE" });
  }, [stopCommandListening]);

  const notifyAnswerStarted = useCallback(() => {
    dispatch({ type: "ANSWER_STARTED" });
  }, []);

  const notifyAnswerEnded = useCallback(() => {
    dispatch({ type: "ANSWER_ENDED" });
  }, []);

  // ── Cleanup on unmount ────────────────────────────────────────────────────
  useEffect(() => {
    return () => {
      stopCommandListening();
      dispatch({ type: "DISABLE" });
    };
  }, [stopCommandListening]);

  return {
    voiceState,
    isHandsFreeOn,
    isListening,
    isSpeechSupported,
    enable,
    disable,
    notifyAnswerStarted,
    notifyAnswerEnded,
  };
}
