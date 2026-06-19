/**
 * apiClient.ts — Centralized API client for Shiksha Sahayak
 *
 * All backend calls go through this file. No raw fetch() calls in components.
 *
 * URL strategy:
 *   - Uses relative /api/* URLs in all environments.
 *   - In dev: Next.js rewrites proxy these to http://localhost:8000/api/*
 *   - In prod: your reverse proxy does the same forwarding
 *   - This means NO hardcoded backend URLs and NO CORS issues.
 *
 * Error handling:
 *   - Network errors return { status: "error", error: { code, message } }
 *   - HTTP errors return the backend error envelope if available
 *   - Timeouts abort cleanly after DEFAULT_TIMEOUT_MS
 *   - No raw stack traces are ever surfaced to the UI
 */

// ─── Types ────────────────────────────────────────────────────────────────────

export interface VisualRef {
  title: string;
  url: string;
  alt: string;
  source: string;
  reason?: string;
}

export interface VideoRef {
  title: string;
  youtube_id: string;
  url: string;
  duration?: number;
  reason?: string;
}

export interface VideoPayload {
  best_video: VideoRef | null;
  candidate_videos: VideoRef[];
  language?: string;
}

export interface QuizQuestion {
  id?: number;
  question: string;
  options: string[];
  correct_answer?: string;
  correct_index?: number;
  explanation?: string;
}

export interface SourceRef {
  title: string;
  snippet: string;
  page_number?: number;
  section_label?: string;
  source_id?: string;
  url?: string;
}

export interface TranscriptEntry {
  role: "user" | "assistant";
  text: string;
  mode?: string;
  language_mode?: string;
}

/** Full assistant response payload returned inside data: {} */
export interface AssistantPayload {
  session_id: string;
  mode: "explain" | "quiz" | "unclear" | "clarify" | "stop" | string;
  language_mode: "hinglish" | "english" | "hindi" | string;

  // Avatar / state
  avatar_state: "idle" | "speaking" | "listening" | "thinking" | string;
  assistant_state: string;
  hands_free_mode: boolean;

  // Explain
  title?: string;
  response_text?: string;
  answer_text?: string;
  bullets?: string[];
  example?: string;
  recap?: string;
  grade_level?: number;

  // Quiz
  questions?: QuizQuestion[];

  // Media
  visuals?: VisualRef[];
  videos?: VideoPayload;

  // Sources / citations
  source_refs?: SourceRef[];
  citations?: SourceRef[];
  source_mode?: boolean;

  // Clarification
  requires_clarification?: boolean;
  message?: string;
  suggestions?: string[];
  next_actions?: string[];

  // Injected by the backend for frontend convenience
  transcript_entry?: TranscriptEntry;
  audio_base64?: string;
}

export interface SessionState {
  session_id: string;
  mode: string;
  language_mode: string;
  assistant_state: string;
  hands_free: boolean;
  source_mode: boolean;
  recent_turns_count: number;
  last_topic?: string;
  last_updated?: string;
}

export interface LastInteraction {
  session_id: string;
  has_history: boolean;
  last_assistant_turn?: { role: string; content: string } | null;
  language_mode: string;
  mode: string;
  assistant_state: string;
}

/** Unified response envelope — every API call returns this shape */
export interface ApiResponse<T = unknown> {
  status: "success" | "error";
  data?: T | null;
  error?: { code: string; message: string };
}

// ─── Config ───────────────────────────────────────────────────────────────────

const DEFAULT_TIMEOUT_MS = 25_000;
const API_BASE = "/api"; // always relative — proxied by Next.js

// ─── Core fetch wrapper ───────────────────────────────────────────────────────

async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
  timeoutMs = DEFAULT_TIMEOUT_MS
): Promise<ApiResponse<T>> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...init.headers,
      },
    });

    clearTimeout(timer);

    // Parse response body — handle both JSON and non-JSON gracefully
    let body: any;
    const contentType = res.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      body = await res.json();
    } else {
      body = { status: "error", error: { code: "NON_JSON", message: `Unexpected response type: ${contentType}` } };
    }

    if (!res.ok) {
      // Backend may return { detail: ... } (FastAPI 422) or our GlobalResponse
      const message =
        body?.error?.message ||
        body?.detail?.message ||
        (typeof body?.detail === "string" ? body.detail : null) ||
        `Request failed (HTTP ${res.status})`;
      return {
        status: "error",
        error: { code: `HTTP_${res.status}`, message },
      };
    }

    return body as ApiResponse<T>;
  } catch (err: any) {
    clearTimeout(timer);
    if (err.name === "AbortError") {
      return {
        status: "error",
        error: { code: "TIMEOUT", message: "The assistant took too long to respond. Please try again." },
      };
    }
    console.error("[apiClient] Network error:", err);
    return {
      status: "error",
      error: {
        code: "NETWORK_ERROR",
        message: "Could not reach the classroom server. Check your connection and try again.",
      },
    };
  }
}

// ─── Command ──────────────────────────────────────────────────────────────────

export interface SubmitCommandOptions {
  text: string;
  sessionId: string;
  sourceMode?: boolean;
  modeHint?: string;
  /** User-supplied API key (passed per-request, never stored server-side) */
  userApiKey?: string;
  /** Provider to use with the user key: 'groq' | 'openai' | 'anthropic' */
  userProvider?: string;
  /** Optional model override when user key is set */
  userModel?: string;
}

/**
 * Submit a teacher command to the backend.
 * Returns AssistantPayload on success, structured error on failure.
 *
 * Uses POST /api/command (unified endpoint).
 */
export async function submitCommand(
  opts: SubmitCommandOptions
): Promise<ApiResponse<AssistantPayload>> {
  return apiFetch<AssistantPayload>("/command", {
    method: "POST",
    body: JSON.stringify({
      text: opts.text,
      session_id: opts.sessionId,
      source_mode: opts.sourceMode ?? false,
      mode_hint: opts.modeHint ?? null,
      // Include user key fields only if provided (omit otherwise to avoid confusion)
      ...(opts.userApiKey ? {
        user_api_key: opts.userApiKey,
        user_provider: opts.userProvider ?? 'groq',
        user_model: opts.userModel ?? null,
      } : {}),
    }),
  });
}

// ─── Session ──────────────────────────────────────────────────────────────────

/** Fetch live session state (used on page load for restore). */
export async function fetchSession(
  sessionId: string
): Promise<ApiResponse<SessionState>> {
  return apiFetch<SessionState>(`/session/${sessionId}`, { method: "GET" });
}

/** Fetch the last assistant interaction (canvas restore on refresh). */
export async function fetchLastInteraction(
  sessionId: string
): Promise<ApiResponse<LastInteraction>> {
  return apiFetch<LastInteraction>(`/session/${sessionId}/last`, { method: "GET" });
}

/** Persist lightweight session preferences to the backend. */
export async function saveSessionPrefs(
  sessionId: string,
  prefs: { language_mode?: string; hands_free?: boolean; source_mode?: boolean }
): Promise<ApiResponse<{ session_id: string; updated: boolean }>> {
  return apiFetch(`/session/${sessionId}`, {
    method: "POST",
    body: JSON.stringify(prefs),
  });
}

/** Reset a session — clears memory, sources, and returns the teacher to idle. */
export async function resetSession(
  sessionId: string
): Promise<ApiResponse<{ session_id: string; cleared: boolean; message: string }>> {
  return apiFetch(`/session/${sessionId}/clear`, { method: "POST" });
}

// ─── Health ───────────────────────────────────────────────────────────────────

/** Quick connectivity check — used to detect if the backend is reachable. */
export async function checkHealth(): Promise<boolean> {
  try {
    const res = await apiFetch<{ status: string }>("/health", { method: "GET" }, 3_000);
    return res.status === "success" && res.data?.status === "ok";
  } catch {
    return false;
  }
}

// ─── Settings (user-supplied keys) ────────────────────────────────────────────

export interface ValidateKeyResult {
  valid: boolean;
  provider: string;
  model_used?: string;
  error?: string;
}

export interface UsageInfo {
  provider: string;
  used: number | null;
  remaining: number | null;
  limit: number | null;
  reset_at: string | null;
  last_checked: string | null;
  available: boolean;
}

/** Validate a user-supplied API key against the provider. */
export async function validateUserKey(
  provider: string,
  apiKey: string,
  model?: string
): Promise<ApiResponse<ValidateKeyResult>> {
  return apiFetch<ValidateKeyResult>("/settings/validate", {
    method: "POST",
    body: JSON.stringify({ provider, api_key: apiKey, model }),
  }, 15_000);
}

/** Fetch quota/usage info for a user-supplied key (returns null values if provider doesn't expose it). */
export async function fetchUserKeyUsage(
  provider: string,
  apiKey: string
): Promise<ApiResponse<UsageInfo>> {
  return apiFetch<UsageInfo>("/settings/usage", {
    method: "POST",
    body: JSON.stringify({ provider, api_key: apiKey }),
  }, 10_000);
}
