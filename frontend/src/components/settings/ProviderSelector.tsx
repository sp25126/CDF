"use client";
import React from 'react';
import { Provider, PROVIDER_LABELS } from '../../state/settingsStore';

interface ProviderSelectorProps {
  value: Provider;
  onChange: (provider: Provider) => void;
}

const PROVIDER_META: Record<Provider, { color: string; desc: string; badge?: string }> = {
  groq: {
    color: '#f97316',
    desc: 'Very fast inference. Best for classroom speed.',
    badge: 'Recommended',
  },
  openai: {
    color: '#10a37f',
    desc: 'GPT-4o and GPT-3.5. Great for detailed answers.',
  },
  anthropic: {
    color: '#d4a27a',
    desc: 'Claude models. Excellent for long explanations.',
  },
};

export const ProviderSelector: React.FC<ProviderSelectorProps> = ({ value, onChange }) => {
  const providers: Provider[] = ['groq', 'openai', 'anthropic'];
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-slate-300">AI Provider</label>
      <div className="grid grid-cols-1 gap-2">
        {providers.map(p => {
          const meta = PROVIDER_META[p];
          const isSelected = value === p;
          return (
            <button
              key={p}
              onClick={() => onChange(p)}
              className={`w-full text-left flex items-center gap-4 px-4 py-3 rounded-xl border transition-all ${
                isSelected
                  ? 'border-blue-500/70 bg-blue-500/10'
                  : 'border-slate-700 bg-slate-800/40 hover:border-slate-500'
              }`}
            >
              {/* Colour dot */}
              <span
                className="w-3 h-3 rounded-full shrink-0"
                style={{ backgroundColor: meta.color }}
              />
              <span className="flex-1 min-w-0">
                <span className="text-sm font-semibold text-slate-100">{PROVIDER_LABELS[p]}</span>
                {meta.badge && (
                  <span className="ml-2 px-1.5 py-0.5 text-[10px] font-bold rounded bg-emerald-500/20 text-emerald-400 uppercase tracking-wide">
                    {meta.badge}
                  </span>
                )}
                <p className="text-xs text-slate-500 mt-0.5 truncate">{meta.desc}</p>
              </span>
              {/* Radio indicator */}
              <span className={`w-4 h-4 rounded-full border-2 shrink-0 flex items-center justify-center transition-colors ${
                isSelected ? 'border-blue-500 bg-blue-500' : 'border-slate-600'
              }`}>
                {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-white" />}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default ProviderSelector;
