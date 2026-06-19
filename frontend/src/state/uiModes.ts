import { AppState, AppStateName } from './appState';

const baseState: Omit<AppState, 'name' | 'canvasMode' | 'juliState'> = {
  consoleBehavior: {
    micActive: false,
    macros: ['Explain', 'Quiz', 'Simpler', 'Example'],
  },
  topBar: {
    language: 'Hinglish',
    handsFree: false,
    sourceMode: false,
    isWhiteboardActive: false,
  },
};

export const uiModes: Record<AppStateName, AppState> = {
  idle: {
    ...baseState,
    name: 'idle',
    canvasMode: 'idle',
    juliState: 'idle',
  },
  listening: {
    ...baseState,
    name: 'listening',
    canvasMode: 'idle',
    juliState: 'listening',
    consoleBehavior: { ...baseState.consoleBehavior, micActive: true },
  },
  processing: {
    ...baseState,
    name: 'processing',
    canvasMode: 'idle',
    juliState: 'thinking',
  },
  explaining: {
    ...baseState,
    name: 'explaining',
    canvasMode: 'explain',
    juliState: 'speaking',
  },
  quiz_active: {
    ...baseState,
    name: 'quiz_active',
    canvasMode: 'quiz',
    juliState: 'quiz',
  },
  source_mode: {
    ...baseState,
    name: 'source_mode',
    canvasMode: 'materials',
    juliState: 'idle',
    topBar: { ...baseState.topBar, sourceMode: true },
  },
  hands_free_active: {
    ...baseState,
    name: 'hands_free_active',
    canvasMode: 'idle',
    juliState: 'listening',
    topBar: { ...baseState.topBar, handsFree: true },
  },
  error: {
    ...baseState,
    name: 'error',
    canvasMode: 'idle',
    juliState: 'idle',
  },
  loading: {
    ...baseState,
    name: 'loading',
    canvasMode: 'idle',
    juliState: 'thinking',
  }
};
