/**
 * voiceConfig.ts
 * ─────────────────────────────────────────────────────────
 * Single source of truth for all voice-session configuration.
 * Tweak here; nothing else needs to change.
 */

export const VOICE_CONFIG = {
  /** SpeechRecognition language tag — en-IN handles English wake words with Indian accents */
  lang: "en-IN" as string,

  /**
   * Milliseconds of silence that constitute end-of-utterance.
   * After this threshold the transcript is finalised and dispatched.
   */
  silenceThresholdMs: 3000 as number,

  /**
   * Minimum character count for a transcript to be dispatched.
   * Shorter strings are likely filler or noise.
   */
  minUtteranceLength: 4 as number,

  /**
   * Phrases to ignore entirely — filler / apology / partial speech.
   * Compared against the normalised (lower-cased, trimmed) transcript.
   */
  fillerPhrases: [
    "uh", "um", "hmm", "hm", "ah", "oh", "err",
    "sorry", "excuse me", "never mind", "wait",
    "okay", "ok", "yes", "no", "yeah",
  ] as string[],

  /**
   * Any normalised transcript that starts with one of these prefixes
   * is treated as a filler and ignored.
   */
  fillerPrefixes: [
    "uh ", "um ", "hmm ", "ah ", "oh ",
  ] as string[],

  /**
   * Wake words / phrases that move the session from
   * wake_listening → command_listening.
   * Matched via case-insensitive substring.
   */
  wakeWords: [
    "juli-e start",
    "juli e start",
    "juliе start",   // cyrillic-е variant (robust)
    "hey juli",
    "start listening",
    "juli listen",
    "juli, listen",
    "ok juli",
    "okay juli",
  ] as string[],

  /**
   * Stop words / phrases that immediately abort the session
   * and return to idle from ANY state.
   */
  stopWords: [
    "juli-e stop",
    "juli e stop",
    "stop listening",
    "juli stop",
    "stop juli",
    "halt",
    "cancel",
    "never mind",
    "shut up",
  ] as string[],

  /**
   * Fade duration (seconds) used by the avatar animation blending.
   * Not used directly here but kept centralised for reference.
   */
  animFadeSecs: 0.25 as number,
} as const;

export type VoiceConfig = typeof VOICE_CONFIG;
