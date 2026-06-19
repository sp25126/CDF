/**
 * sessionStore.ts — Session ID management
 *
 * Generates a stable session UUID that persists for the life of the browser tab
 * (stored in sessionStorage, not localStorage, so each new tab is a fresh session).
 *
 * getSessionId() is the single source of truth for the session identifier sent
 * to the backend. No component should hardcode a session ID.
 */
import { create } from "zustand";
import { AppState } from "./appState";

// ─── Session UUID ─────────────────────────────────────────────────────────────

const SESSION_ID_KEY = "cdf-session-id";

function generateUUID(): string {
  // Prefer crypto.randomUUID when available (all modern browsers + Node 15+)
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Fallback for older environments
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Returns the stable session ID for this browser tab.
 * Creates one if it doesn't exist yet.
 *
 * Uses sessionStorage (tab-scoped) so:
 *   - Refreshing the page keeps the same session (teacher can resume)
 *   - Opening a new tab gets a fresh session (new class / new teacher)
 */
export function getSessionId(): string {
  if (typeof window === "undefined") return "ssr-session"; // SSR safety
  let id = sessionStorage.getItem(SESSION_ID_KEY);
  if (!id) {
    id = generateUUID();
    sessionStorage.setItem(SESSION_ID_KEY, id);
  }
  return id;
}

/** Force a new session ID — call when the teacher explicitly resets. */
export function rotateSessionId(): string {
  if (typeof window === "undefined") return "ssr-session";
  const id = generateUUID();
  sessionStorage.setItem(SESSION_ID_KEY, id);
  return id;
}

// ─── Zustand store (lightweight app-level session preferences) ────────────────

interface SessionState extends Omit<AppState, "name" | "juliState" | "consoleBehavior"> {
  // We only persist a subset of the AppState
}

interface SessionStore {
  session: SessionState | null;
  setSession: (session: SessionState) => void;
  clearSession: () => void;
}

export const useSessionStore = create<SessionStore>((set) => ({
  session: null,
  setSession: (session) => set({ session }),
  clearSession: () => set({ session: null }),
}));
