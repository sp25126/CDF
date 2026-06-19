"use client";
import React, { useEffect, useState, useCallback } from 'react';
import { Loader2, RefreshCw, AlertCircle } from 'lucide-react';
import { Provider } from '../../state/settingsStore';

interface ModelOption {
  id: string;
  label: string;
}

interface ModelSelectorProps {
  provider: Provider;
  apiKey: string;
  value: string;
  onChange: (model: string) => void;
  /** When true, immediately tries to fetch models (key has been saved/validated) */
  autoFetch?: boolean;
}

// Static fallbacks shown before the user enters a key
const STATIC_FALLBACKS: Record<Provider, ModelOption[]> = {
  groq: [
    { id: 'llama-3.3-70b-versatile', label: 'LLaMA 3.3 70B (Versatile)' },
    { id: 'llama-3.1-8b-instant', label: 'LLaMA 3.1 8B (Instant)' },
    { id: 'gemma2-9b-it', label: 'Gemma 2 9B' },
  ],
  openai: [
    { id: 'gpt-4o', label: 'GPT-4o' },
    { id: 'gpt-4o-mini', label: 'GPT-4o Mini' },
    { id: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
  ],
  anthropic: [
    { id: 'claude-3-5-haiku-20241022', label: 'Claude 3.5 Haiku' },
    { id: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet' },
  ],
};

type FetchState = 'idle' | 'loading' | 'done' | 'error';

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  provider,
  apiKey,
  value,
  onChange,
  autoFetch = false,
}) => {
  const [models, setModels] = useState<ModelOption[]>(STATIC_FALLBACKS[provider]);
  const [fetchState, setFetchState] = useState<FetchState>('idle');

  const fetchModels = useCallback(async () => {
    if (!apiKey || apiKey.trim().length < 10) return;
    setFetchState('loading');
    try {
      const res = await fetch('/api/settings/models', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, api_key: apiKey.trim() }),
      });
      const data = await res.json();
      if (data.status === 'success' && data.models?.length > 0) {
        const fetched: ModelOption[] = data.models;
        setModels(fetched);
        setFetchState('done');
        // Auto-select first model if current value isn't in the new list
        if (!fetched.find(m => m.id === value)) {
          onChange(fetched[0].id);
        }
      } else {
        // Fall back to static list
        setModels(STATIC_FALLBACKS[provider]);
        setFetchState('error');
      }
    } catch {
      setModels(STATIC_FALLBACKS[provider]);
      setFetchState('error');
    }
  }, [provider, apiKey, value, onChange]);

  // Reset to static fallbacks when provider changes
  useEffect(() => {
    setModels(STATIC_FALLBACKS[provider]);
    setFetchState('idle');
  }, [provider]);

  // Auto-fetch when key is available and autoFetch is enabled
  useEffect(() => {
    if (autoFetch && apiKey && apiKey.trim().length >= 10) {
      fetchModels();
    }
  }, [autoFetch, apiKey, provider]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-slate-300">Model</label>
        <div className="flex items-center gap-2">
          {fetchState === 'loading' && (
            <span className="flex items-center gap-1 text-xs text-blue-400">
              <Loader2 size={11} className="animate-spin" />
              Fetching models…
            </span>
          )}
          {fetchState === 'done' && (
            <span className="text-xs text-emerald-400">
              {models.length} model{models.length !== 1 ? 's' : ''} available
            </span>
          )}
          {fetchState === 'error' && (
            <span className="flex items-center gap-1 text-xs text-amber-400">
              <AlertCircle size={11} />
              Using defaults
            </span>
          )}
          {/* Manual refresh — only shown when key is present */}
          {apiKey && apiKey.trim().length >= 10 && fetchState !== 'loading' && (
            <button
              onClick={fetchModels}
              className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-300 transition-colors"
              title="Refresh model list"
            >
              <RefreshCw size={11} />
              Refresh
            </button>
          )}
        </div>
      </div>

      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        disabled={fetchState === 'loading'}
        className="w-full bg-slate-800/60 border border-slate-600 text-slate-100 text-sm rounded-xl px-4 py-3 outline-none focus:border-blue-500/60 transition-colors appearance-none cursor-pointer disabled:opacity-50"
      >
        {models.map(m => (
          <option key={m.id} value={m.id} className="bg-slate-800">
            {m.label}
          </option>
        ))}
      </select>

      {fetchState === 'idle' && !autoFetch && apiKey && apiKey.trim().length >= 10 && (
        <p className="text-xs text-slate-600">
          Click{' '}
          <button onClick={fetchModels} className="text-blue-400 hover:underline">
            Refresh
          </button>{' '}
          to load your available models.
        </p>
      )}

      {(!apiKey || apiKey.trim().length < 10) && (
        <p className="text-xs text-slate-600">
          Enter your API key above to see your available models.
        </p>
      )}
    </div>
  );
};

export default ModelSelector;
