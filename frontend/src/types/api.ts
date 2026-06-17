/**
 * Type definitions for CDF classroom assistant responses.
 * These mirror the backend AssistantResponse schema.
 */

export type Mode = "explain" | "quiz" | "followup" | "stop" | "unclear" | "clarify";
export type LanguageMode = "hinglish" | "english" | "hindi";
export type AvatarState = "idle" | "speaking" | "listening" | "thinking";

export interface SourceRef {
  title: string;
  snippet: string;
  page_number?: number;
  section_label?: string;
  source_id?: string;
  url?: string;
}

export interface VisualRef {
  type: string;
  url: string;
  description?: string;
  visual_id?: string;
}

export interface VideoRef {
  title: string;
  youtube_id: string;
  duration?: number;
  video_id?: string;
  url?: string;
}

export interface QuizQuestion {
  question: string;
  options: string[];
  correct_index: number;
  explanation: string;
}

export interface QuizPayload {
  title: string;
  topic: string;
  questions: QuizQuestion[];
  current_index: number;
  total_questions: number;
}

export interface AssistantResponse {
  session_id: string;
  mode: Mode;
  language_mode: LanguageMode;
  transcript_text?: string;
  answer_text?: string;
  quiz?: QuizPayload;
  next_actions: string[];
  confidence: number;
  requires_clarification: boolean;
  avatar_state: AvatarState;
  source_refs: SourceRef[];
  visuals: VisualRef[];
  videos: VideoRef[];

  // Backwards compatibility
  title?: string;
  grade_level?: number;
  bullets: string[];
  example?: string;
  recap?: string;
  questions: QuizQuestion[];
  audio_base64?: string;
}
