"use client";
import React from 'react';
import { Provider, PROVIDER_MODELS } from '../../state/settingsStore';

interface ModelSelectorProps {
  provider: Provider;
  value: string;
  onChange: (model: string) => void;
}

const MODEL_LABELS: Record<string, string> = {
  'llama3-70b-8192': 'LLaMA 3 70B — Best quality',
  'llama3-8b-8192': 'LLaMA 3 8B — Fastest',
  'mixtral-8x7b-32768': 'Mixtral 8x7B — Long context',
  'gpt-4o': 'GPT-4o — Most capable',
  'gpt-4o-mini': 'GPT-4o Mini — Faster & cheaper',
  'gpt-3.5-turbo': 'GPT-3.5 Turbo — Budget option',
  'claude-3-5-haiku-20241022': 'Claude 3.5 Haiku — Fast & affordable',
  'claude-3-5-sonnet-20241022': 'Claude 3.5 Sonnet — Highest quality',
};

export const ModelSelector: React.FC<ModelSelectorProps> = ({ provider, value, onChange }) => {
  const models = PROVIDER_MODELS[provider] ?? [];

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-slate-300">Model</label>
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        className="w-full bg-slate-800/60 border border-slate-600 text-slate-100 text-sm rounded-xl px-4 py-3 outline-none focus:border-blue-500/60 transition-colors appearance-none cursor-pointer"
      >
        {models.map(m => (
          <option key={m} value={m} className="bg-slate-800">
            {MODEL_LABELS[m] ?? m}
          </option>
        ))}
      </select>
    </div>
  );
};

export default ModelSelector;
