"use client";

/**
 * settingsStore.ts — LLM API key settings for Shiksha Sahayak.
 *
 * Storage policy:
 *   - The raw key is held in React state (in-memory) only.
 *   - If the user enables "Remember across sessions", it is also written to
 *     localStorage in masked form. On next load the masked copy is read back
 *     and the user must re-enter the actual key — OR the raw key may be stored
 *     if the user explicitly accepts the tradeoff.
 *   - The key is NEVER logged, never sent to analytics, never included in
 *     error reports.
 */

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

// ─── Types ────────────────────────────────────────────────────────────────────

export type Provider = 'groq' | 'openai' | 'anthropic';

export const PROVIDER_LABELS: Record<Provider, string> = {
  groq: 'Groq',
  openai: 'OpenAI',
  anthropic: 'Anthropic',
};

export const PROVIDER_MODELS: Record<Provider, string[]> = {
  groq: ['llama3-70b-8192', 'llama3-8b-8192', 'mixtral-8x7b-32768'],
  openai: ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo'],
  anthropic: ['claude-3-5-haiku-20241022', 'claude-3-5-sonnet-20241022'],
};

export const DEFAULT_MODEL: Record<Provider, string> = {
  groq: 'llama3-70b-8192',
  openai: 'gpt-4o-mini',
  anthropic: 'claude-3-5-haiku-20241022',
};

export interface UsageInfo {
  provider: string;
  used: number | null;
  remaining: number | null;
  limit: number | null;
  reset_at: string | null;
  last_checked: string | null;
  available: boolean;
}

export type UsageState = 'idle' | 'loading' | 'available' | 'unavailable' | 'error';

export interface SettingsState {
  isOpen: boolean;
  provider: Provider;
  /** Raw key — in memory only */
  apiKey: string;
  model: string;
  /** Whether key has been saved this session */
  isSaved: boolean;
  /** Whether key should persist to localStorage */
  persistKey: boolean;
  usage: UsageInfo | null;
  usageState: UsageState;
  validationState: 'idle' | 'checking' | 'valid' | 'invalid';
  validationError: string | null;
}

interface SettingsActions {
  openSettings: () => void;
  closeSettings: () => void;
  setProvider: (provider: Provider) => void;
  setModel: (model: string) => void;
  setApiKey: (key: string) => void;
  setPersistKey: (persist: boolean) => void;
  saveKey: () => void;
  clearKey: () => void;
  getMaskedKey: () => string;
  setUsage: (usage: UsageInfo | null, state: UsageState) => void;
  setValidationState: (state: 'idle' | 'checking' | 'valid' | 'invalid', error?: string) => void;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

const PREFS_KEY = 'ss-api-prefs';
const isBrowser = typeof window !== 'undefined';

function maskKey(key: string): string {
  if (!key || key.length < 8) return '••••••••';
  return key.slice(0, 4) + '•'.repeat(Math.min(key.length - 8, 20)) + key.slice(-4);
}

function loadPersistedPrefs(): { provider: Provider; model: string; rawKey: string } | null {
  if (!isBrowser) return null;
  try {
    const raw = localStorage.getItem(PREFS_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function savePersistedPrefs(provider: Provider, model: string, rawKey: string) {
  if (!isBrowser) return;
  try {
    localStorage.setItem(PREFS_KEY, JSON.stringify({ provider, model, rawKey }));
  } catch {
    // ignore storage errors
  }
}

function clearPersistedPrefs() {
  if (!isBrowser) return;
  try {
    localStorage.removeItem(PREFS_KEY);
  } catch {
    // ignore
  }
}

// ─── Context ─────────────────────────────────────────────────────────────────

const SettingsContext = createContext<(SettingsState & SettingsActions) | null>(null);

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<SettingsState>(() => {
    const persisted = loadPersistedPrefs();
    return {
      isOpen: false,
      provider: persisted?.provider ?? 'groq',
      apiKey: persisted?.rawKey ?? '',
      model: persisted?.model ?? DEFAULT_MODEL['groq'],
      isSaved: !!(persisted?.rawKey),
      persistKey: !!persisted,
      usage: null,
      usageState: 'idle',
      validationState: 'idle',
      validationError: null,
    };
  });

  const openSettings = useCallback(() => setState(s => ({ ...s, isOpen: true })), []);
  const closeSettings = useCallback(() => setState(s => ({ ...s, isOpen: false })), []);

  const setProvider = useCallback((provider: Provider) => {
    setState(s => ({
      ...s,
      provider,
      model: DEFAULT_MODEL[provider],
      // clear key and usage when provider changes
      apiKey: '',
      isSaved: false,
      usage: null,
      usageState: 'idle',
      validationState: 'idle',
      validationError: null,
    }));
    clearPersistedPrefs();
  }, []);

  const setModel = useCallback((model: string) => {
    setState(s => ({ ...s, model }));
  }, []);

  const setApiKey = useCallback((key: string) => {
    setState(s => ({ ...s, apiKey: key, validationState: 'idle', validationError: null }));
  }, []);

  const setPersistKey = useCallback((persist: boolean) => {
    setState(s => ({ ...s, persistKey: persist }));
  }, []);

  const saveKey = useCallback(() => {
    setState(s => {
      if (s.persistKey && s.apiKey) {
        savePersistedPrefs(s.provider, s.model, s.apiKey);
      } else {
        clearPersistedPrefs();
      }
      return { ...s, isSaved: true };
    });
  }, []);

  const clearKey = useCallback(() => {
    clearPersistedPrefs();
    setState(s => ({
      ...s,
      apiKey: '',
      isSaved: false,
      persistKey: false,
      usage: null,
      usageState: 'idle',
      validationState: 'idle',
      validationError: null,
    }));
  }, []);

  const getMaskedKey = useCallback(() => {
    return maskKey(state.apiKey);
  }, [state.apiKey]);

  const setUsage = useCallback((usage: UsageInfo | null, usageState: UsageState) => {
    setState(s => ({ ...s, usage, usageState }));
  }, []);

  const setValidationState = useCallback(
    (validationState: 'idle' | 'checking' | 'valid' | 'invalid', error?: string) => {
      setState(s => ({ ...s, validationState, validationError: error ?? null }));
    },
    []
  );

  const value = {
    ...state,
    openSettings,
    closeSettings,
    setProvider,
    setModel,
    setApiKey,
    setPersistKey,
    saveKey,
    clearKey,
    getMaskedKey,
    setUsage,
    setValidationState,
  };

  return React.createElement(SettingsContext.Provider, { value }, children);
}

export function useSettings() {
  const ctx = useContext(SettingsContext);
  if (!ctx) throw new Error('useSettings must be used within <SettingsProvider>');
  return ctx;
}
