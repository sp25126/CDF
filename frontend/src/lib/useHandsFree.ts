/**
 * useHandsFree.ts
 * ─────────────────────────────────────────────────────────
 * Backward-compatible shim over useVoiceSession.
 *
 * The original interface is preserved so page.tsx keeps compiling
 * with zero changes to its import / call-site.  The real logic now
 * lives in ../voice/voiceRouter.ts.
 */

import { useCallback } from "react";
import { useVoiceSession } from "../voice/voiceRouter";

interface UseHandsFreeProps {
  onCommand: (text: string) => void;
  onStateChange?: (state: "idle" | "listening" | "speaking" | "thinking") => void;
}

export function useHandsFree({ onCommand, onStateChange }: UseHandsFreeProps) {
  const {
    voiceState,
    isHandsFreeOn,
    isListening,
    enable,
    disable,
    notifyAnswerStarted,
    notifyAnswerEnded,
  } = useVoiceSession({ onCommand, onStateChange });

  // Legacy setIsActive shim: true → enable, false → disable
  const setIsActive = useCallback(
    (active: boolean) => {
      if (active) enable();
      else         disable();
    },
    [enable, disable],
  );

  // Legacy startListening / stopListening (no-ops now; router manages this)
  const startListening = useCallback(() => {}, []);
  const stopListening  = useCallback(() => {}, []);

  return {
    isActive:    isHandsFreeOn,
    setIsActive,
    isListening,
    startListening,
    stopListening,
    voiceState,
    notifyAnswerStarted,
    notifyAnswerEnded,
  };
}
