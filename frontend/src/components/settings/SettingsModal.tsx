"use client";
import React, { useEffect, useCallback } from 'react';
import { X, Key, Settings, Trash2, Save, Loader2, CheckCircle2 } from 'lucide-react';
import { useSettings } from '../../state/settingsStore';
import { ApiKeyField } from './ApiKeyField';
import { ProviderSelector } from './ProviderSelector';
import { ModelSelector } from './ModelSelector';
import { UsagePanel } from './UsagePanel';
import { SecurityNote } from './SecurityNote';

async function apiFetch(path: string, body: object) {
  const res = await fetch(`/api${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return res.json();
}

/**
 * SettingsModal — non-blocking settings overlay.
 *
 * Floats over the classroom UI without disrupting it.
 * Closes on Escape or backdrop click.
 */
export const SettingsModal: React.FC = () => {
  const {
    isOpen,
    closeSettings,
    provider, setProvider,
    model, setModel,
    apiKey, setApiKey,
    isSaved,
    persistKey, setPersistKey,
    usage, usageState,
    validationState, validationError,
    saveKey, clearKey,
    getMaskedKey,
    setUsage, setValidationState,
  } = useSettings();

  // Close on Escape
  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') closeSettings(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [isOpen, closeSettings]);

  const handleValidate = useCallback(async () => {
    if (!apiKey.trim() || apiKey.trim().length < 10) {
      setValidationState('invalid', 'That key looks too short. Please paste the full key.');
      return;
    }
    setValidationState('checking');
    try {
      const res = await apiFetch('/settings/validate', {
        provider,
        api_key: apiKey.trim(),
        model,
      });
      if (res.valid) {
        setValidationState('valid');
        // Automatically refresh model list after a valid key
        // The ModelSelector's autoFetch will pick this up via the apiKey prop
      } else {
        setValidationState('invalid', res.error ?? 'Key was rejected by the provider.');
      }
    } catch {
      setValidationState('invalid', 'Could not reach the server. Check your connection.');
    }
  }, [apiKey, provider, model, setValidationState]);

  const handleSave = useCallback(async () => {
    if (!apiKey.trim()) return;
    // Validate first if not already done
    if (validationState !== 'valid') {
      await handleValidate();
      // re-read state — check happens via handleValidate
      return;
    }
    saveKey();
    // Immediately check usage
    handleRefreshUsage();
  }, [apiKey, validationState, saveKey, handleValidate]);

  const handleRefreshUsage = useCallback(async () => {
    if (!isSaved && !apiKey.trim()) return;
    setUsage(null, 'loading');
    try {
      const res = await apiFetch('/settings/usage', {
        provider,
        api_key: apiKey.trim(),
      });
      if (res.status === 'success' && res.data) {
        const d = res.data;
        setUsage(d, d.available ? 'available' : 'unavailable');
      } else {
        setUsage(null, 'error');
      }
    } catch {
      setUsage(null, 'error');
    }
  }, [provider, apiKey, isSaved, setUsage]);

  const handleClear = useCallback(() => {
    if (window.confirm('Remove your saved key? The app will use the shared classroom key instead.')) {
      clearKey();
    }
  }, [clearKey]);

  if (!isOpen) return null;

  const canSave = apiKey.trim().length >= 10;
  const canValidate = apiKey.trim().length >= 10 && validationState !== 'checking';

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm"
        onClick={closeSettings}
        aria-hidden="true"
      />

      {/* Drawer */}
      <aside
        className="fixed right-0 top-0 bottom-0 z-50 w-full max-w-md flex flex-col bg-slate-900 border-l border-slate-700 shadow-2xl"
        role="dialog"
        aria-modal="true"
        aria-label="Settings"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700 shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-blue-500/15 text-blue-400">
              <Settings size={18} />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-100">Settings</h2>
              <p className="text-xs text-slate-500">LLM Provider &amp; API Key</p>
            </div>
          </div>
          <button
            onClick={closeSettings}
            className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
            aria-label="Close settings"
          >
            <X size={20} />
          </button>
        </div>

        {/* Scrollable content */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">

          {/* Info banner */}
          <div className="flex items-start gap-3 px-4 py-3 bg-blue-500/10 border border-blue-500/20 rounded-xl">
            <Key size={15} className="text-blue-400 shrink-0 mt-0.5" />
            <p className="text-xs text-blue-300/80 leading-relaxed">
              Add your own API key to use your own quota. Without one, the app uses a shared key that may have limited capacity.
            </p>
          </div>

          {/* Provider */}
          <ProviderSelector value={provider} onChange={setProvider} />

          {/* Model */}
          <ModelSelector
            provider={provider}
            apiKey={apiKey}
            value={model}
            onChange={setModel}
            autoFetch={validationState === 'valid' || isSaved}
          />

          {/* API Key */}
          <ApiKeyField
            value={apiKey}
            onChange={setApiKey}
            isSaved={isSaved}
            validationState={validationState}
            validationError={validationError}
            onEdit={handleClear}
            maskedKey={getMaskedKey()}
          />

          {/* Persist checkbox — only shown when editing */}
          {!isSaved && apiKey.trim().length > 0 && (
            <label className="flex items-center gap-3 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={persistKey}
                onChange={e => setPersistKey(e.target.checked)}
                className="w-4 h-4 rounded border-slate-600 bg-slate-800 accent-blue-500"
              />
              <span className="text-sm text-slate-400">
                Remember key across sessions{' '}
                <span className="text-xs text-slate-600">(saved in your browser)</span>
              </span>
            </label>
          )}

          {/* Security note */}
          <SecurityNote persistEnabled={persistKey} />

          {/* Usage */}
          <UsagePanel usageState={usageState} usage={usage} onRefresh={handleRefreshUsage} />
        </div>

        {/* Footer actions */}
        <div className="px-6 py-4 border-t border-slate-700 shrink-0 space-y-2">
          {!isSaved ? (
            <div className="flex gap-2">
              {/* Validate */}
              <button
                onClick={handleValidate}
                disabled={!canValidate}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-medium bg-slate-700 hover:bg-slate-600 text-slate-200 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                {validationState === 'checking' ? (
                  <><Loader2 size={16} className="animate-spin" /> Checking…</>
                ) : (
                  'Test Key'
                )}
              </button>
              {/* Save */}
              <button
                onClick={handleSave}
                disabled={!canSave}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-semibold bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-lg shadow-blue-900/30"
              >
                {validationState === 'checking' ? (
                  <><Loader2 size={16} className="animate-spin" /> Saving…</>
                ) : (
                  <><Save size={16} /> Save Key</>
                )}
              </button>
            </div>
          ) : (
            <div className="flex gap-2">
              <div className="flex-1 flex items-center gap-2 px-4 py-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl">
                <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
                <span className="text-sm font-medium text-emerald-300">Key saved</span>
              </div>
              <button
                onClick={handleClear}
                className="flex items-center gap-2 px-4 py-3 rounded-xl text-sm font-medium bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 transition-colors"
              >
                <Trash2 size={16} />
                Remove
              </button>
            </div>
          )}
          <button
            onClick={closeSettings}
            className="w-full py-2.5 rounded-xl text-sm text-slate-500 hover:text-slate-300 transition-colors"
          >
            Close
          </button>
        </div>
      </aside>
    </>
  );
};

export default SettingsModal;
