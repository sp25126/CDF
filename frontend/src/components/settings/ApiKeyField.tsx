"use client";
import React, { useState } from 'react';
import { Eye, EyeOff, CheckCircle2, XCircle, Loader2 } from 'lucide-react';

interface ApiKeyFieldProps {
  value: string;
  onChange: (val: string) => void;
  isSaved: boolean;
  validationState: 'idle' | 'checking' | 'valid' | 'invalid';
  validationError: string | null;
  onEdit: () => void;
  maskedKey: string;
}

/**
 * ApiKeyField — a secure input for LLM API keys.
 * After saving, shows a masked key with an Edit button.
 * Raw key is never displayed in plain text once saved.
 */
export const ApiKeyField: React.FC<ApiKeyFieldProps> = ({
  value,
  onChange,
  isSaved,
  validationState,
  validationError,
  onEdit,
  maskedKey,
}) => {
  const [revealed, setRevealed] = useState(false);

  if (isSaved) {
    return (
      <div className="space-y-2">
        <label className="block text-sm font-medium text-slate-300">API Key</label>
        <div className="flex items-center gap-3">
          <div className="flex-1 flex items-center gap-3 bg-slate-800/60 border border-slate-600 rounded-xl px-4 py-3">
            <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
            <span className="font-mono text-sm text-slate-300 tracking-wider flex-1">{maskedKey}</span>
          </div>
          <button
            onClick={onEdit}
            className="px-4 py-3 rounded-xl text-sm font-medium bg-slate-700 hover:bg-slate-600 text-slate-200 transition-colors"
          >
            Edit
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-slate-300">
        API Key
        <span className="ml-2 text-xs text-slate-500 font-normal">
          (Your key stays on this device)
        </span>
      </label>
      <div className={`flex items-center gap-2 bg-slate-800/60 border rounded-xl px-4 py-3 transition-colors ${
        validationState === 'invalid' ? 'border-red-500/60' :
        validationState === 'valid' ? 'border-emerald-500/60' :
        'border-slate-600 focus-within:border-blue-500/60'
      }`}>
        <input
          type={revealed ? 'text' : 'password'}
          value={value}
          onChange={e => onChange(e.target.value)}
          placeholder="Paste your API key here…"
          autoComplete="off"
          spellCheck={false}
          className="flex-1 bg-transparent text-sm text-slate-100 placeholder-slate-500 outline-none font-mono"
        />
        <div className="flex items-center gap-2 shrink-0">
          {validationState === 'checking' && (
            <Loader2 size={16} className="text-blue-400 animate-spin" />
          )}
          {validationState === 'valid' && (
            <CheckCircle2 size={16} className="text-emerald-400" />
          )}
          {validationState === 'invalid' && (
            <XCircle size={16} className="text-red-400" />
          )}
          <button
            type="button"
            onClick={() => setRevealed(r => !r)}
            className="p-1 text-slate-500 hover:text-slate-300 transition-colors"
            title={revealed ? 'Hide key' : 'Show key'}
          >
            {revealed ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </div>
      </div>
      {validationError && (
        <p className="text-xs text-red-400 flex items-center gap-1">
          <XCircle size={12} />
          {validationError}
        </p>
      )}
      {validationState === 'valid' && (
        <p className="text-xs text-emerald-400 flex items-center gap-1">
          <CheckCircle2 size={12} />
          Key accepted. Ready to save.
        </p>
      )}
    </div>
  );
};

export default ApiKeyField;
