/**
 * voiceSessionState.ts
 * ─────────────────────────────────────────────────────────
 * Pure state machine: states, events, reducer, and helpers.
 * No React or browser APIs here — fully testable in isolation.
 */

// ─── States ───────────────────────────────────────────────────────────────────

export type VoiceSessionState =
  | "idle"               // hands-free disabled or explicitly stopped
  | "wake_listening"     // hands-free on, waiting for wake word
  | "command_listening"  // wake word heard, now capturing the user's question
  | "processing"         // transcript sent, waiting for backend response
  | "speaking"           // JULI-E is playing/reading out the answer
  | "stopped";           // explicit stop word heard (will auto-return to wake_listening)

// ─── Events ───────────────────────────────────────────────────────────────────

export type VoiceEvent =
  | { type: "ENABLE" }             // user toggles hands-free ON
  | { type: "DISABLE" }            // user toggles hands-free OFF
  | { type: "WAKE_WORD" }          // wake phrase detected in audio stream
  | { type: "STOP_WORD" }          // stop phrase detected in audio stream
  | { type: "SPEECH_START" }       // microphone picking up voice
  | { type: "SPEECH_UPDATE"; transcript: string }  // interim transcript update
  | { type: "SILENCE_TIMEOUT"; transcript: string }// 3-second silence → finalise
  | { type: "COMMAND_SENT" }       // transcript dispatched to backend
  | { type: "ANSWER_STARTED" }     // audio / text response began playing
  | { type: "ANSWER_ENDED" }       // audio / text response finished
  | { type: "ERROR"; message: string };            // unrecoverable error

// ─── Reducer (pure) ───────────────────────────────────────────────────────────

/**
 * Deterministic state machine.  All transitions are listed explicitly;
 * any unlisted (state, event) pair is a no-op.
 */
export function voiceReducer(
  state: VoiceSessionState,
  event: VoiceEvent,
): VoiceSessionState {
  switch (event.type) {

    // ── Lifecycle ──────────────────────────────────────────────────────────
    case "ENABLE":
      if (state === "idle" || state === "stopped") return "wake_listening";
      return state;

    case "DISABLE":
      return "idle";

    // ── Wake / Stop ────────────────────────────────────────────────────────
    case "WAKE_WORD":
      if (state === "wake_listening") return "command_listening";
      return state;

    case "STOP_WORD":
      // Stop word works from any active state
      if (state !== "idle") return "wake_listening";
      return state;

    // ── Speech activity (resets silence timer — no state change needed) ───
    case "SPEECH_START":
    case "SPEECH_UPDATE":
      return state; // timer reset is handled externally; state is unchanged

    // ── End of utterance ───────────────────────────────────────────────────
    case "SILENCE_TIMEOUT":
      if (state === "command_listening") return "processing";
      return state;

    case "COMMAND_SENT":
      if (state === "processing") return "processing"; // wait for ANSWER_STARTED
      return state;

    case "ANSWER_STARTED":
      if (state === "processing") return "speaking";
      return state;

    case "ANSWER_ENDED":
      if (state === "speaking") return "wake_listening";
      return state;

    // ── Error ──────────────────────────────────────────────────────────────
    case "ERROR":
      console.error("[VoiceSession] error:", event.message);
      return "wake_listening"; // keep trying rather than dying silently

    default:
      return state;
  }
}

// ─── Avatar State Mapping ─────────────────────────────────────────────────────

/** Maps the voice session state to the avatar animation state string. */
export function voiceStateToAvatarState(
  vs: VoiceSessionState,
): "idle" | "listening" | "thinking" | "speaking" | "waving" {
  switch (vs) {
    case "idle":
    case "stopped":
      return "idle";
    case "wake_listening":
    case "command_listening":
      return "listening";
    case "processing":
      return "thinking";
    case "speaking":
      return "speaking";
  }
}

// ─── Label Helper ─────────────────────────────────────────────────────────────

/** Human-readable label for UI badges. */
export function voiceStateLabel(vs: VoiceSessionState): string {
  switch (vs) {
    case "idle":             return "Idle";
    case "wake_listening":   return "Say wake word…";
    case "command_listening":return "Listening…";
    case "processing":       return "Thinking…";
    case "speaking":         return "Speaking";
    case "stopped":          return "Stopped";
  }
}
