/**
 * transcriptStore.ts — Classroom conversation history
 *
 * Stores the chronological log of teacher commands and assistant responses.
 * Each entry has both sides of the turn so the transcript panel can display
 * a full Q&A history for the classroom.
 *
 * Changes from v1:
 *   - addEntry now takes (command, responseSummary) like before, but also
 *     accepts an optional `mode` and `languageMode` for richer transcript display
 *   - addAssistantTurn() added for the command hook to update the last entry
 *     with the assistant response after the API call returns
 */
import { create } from "zustand";

export interface TranscriptEntry {
  id: string;
  timestamp: string;
  command: string;
  responseSummary: string;
  mode?: string;
  languageMode?: string;
  payload?: any;
}

interface TranscriptState {
  history: TranscriptEntry[];
  /** Add a complete turn (user + assistant). */
  addEntry: (command: string, responseSummary: string, meta?: { mode?: string; languageMode?: string }) => void;
  /** Update the most recent entry's assistant response after the API returns. */
  updateLastResponse: (responseSummary: string, meta?: { mode?: string; languageMode?: string; payload?: any }) => void;
  clearHistory: () => void;
}

const MAX_HISTORY = 20;

export const useTranscriptStore = create<TranscriptState>((set) => ({
  history: [],

  addEntry: (command, responseSummary, meta = {}) =>
    set((state) => {
      const newEntry: TranscriptEntry = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        command,
        responseSummary,
        mode: meta.mode,
        languageMode: meta.languageMode,
      };
      const newHistory = [newEntry, ...state.history].slice(0, MAX_HISTORY);
      return { history: newHistory };
    }),

  updateLastResponse: (responseSummary, meta = {}) =>
    set((state) => {
      if (state.history.length === 0) return state;
      const [latest, ...rest] = state.history;
      return {
        history: [
          {
            ...latest,
            responseSummary,
            mode: meta.mode ?? latest.mode,
            languageMode: meta.languageMode ?? latest.languageMode,
            payload: meta.payload ?? latest.payload,
          },
          ...rest,
        ],
      };
    }),

  clearHistory: () => set({ history: [] }),
}));
