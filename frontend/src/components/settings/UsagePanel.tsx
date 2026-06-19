"use client";
import React from 'react';
import { Loader2, BarChart3, Info, RefreshCw } from 'lucide-react';
import { UsageInfo, UsageState } from '../../state/settingsStore';

interface UsagePanelProps {
  usageState: UsageState;
  usage: UsageInfo | null;
  onRefresh: () => void;
}

function formatNumber(n: number | null | undefined): string {
  if (n == null) return '—';
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString();
}

function formatTime(iso: string | null | undefined): string {
  if (!iso) return 'Unknown';
  try {
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return 'Unknown';
  }
}

export const UsagePanel: React.FC<UsagePanelProps> = ({ usageState, usage, onRefresh }) => {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
          <BarChart3 size={15} />
          Usage &amp; Quota
        </h3>
        {usageState !== 'loading' && (
          <button
            onClick={onRefresh}
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors"
          >
            <RefreshCw size={12} />
            Refresh
          </button>
        )}
      </div>

      {/* Loading */}
      {usageState === 'loading' && (
        <div className="flex items-center gap-3 px-4 py-4 bg-slate-800/40 rounded-xl border border-slate-700">
          <Loader2 size={18} className="text-blue-400 animate-spin shrink-0" />
          <span className="text-sm text-slate-400">Checking your quota…</span>
        </div>
      )}

      {/* Idle — not checked yet */}
      {usageState === 'idle' && (
        <div className="flex items-start gap-3 px-4 py-4 bg-slate-800/40 rounded-xl border border-slate-700">
          <Info size={16} className="text-slate-500 shrink-0 mt-0.5" />
          <p className="text-sm text-slate-500">
            Save your key first, then click Refresh to check quota.
          </p>
        </div>
      )}

      {/* Unavailable — provider doesn't expose quota */}
      {(usageState === 'unavailable' || (usageState === 'available' && usage && !usage.available)) && (
        <div className="flex items-start gap-3 px-4 py-4 bg-slate-800/40 rounded-xl border border-slate-700">
          <Info size={16} className="text-blue-400/70 shrink-0 mt-0.5" />
          <div className="min-w-0">
            <p className="text-sm text-slate-400">
              Usage info isn't available for this provider.
            </p>
            <p className="text-xs text-slate-600 mt-1">
              Check your quota directly in your provider's dashboard.
            </p>
            {usage?.last_checked && (
              <p className="text-xs text-slate-600 mt-1">
                Last checked: {formatTime(usage.last_checked)}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Error */}
      {usageState === 'error' && (
        <div className="flex items-start gap-3 px-4 py-4 bg-red-500/10 rounded-xl border border-red-500/30">
          <Info size={16} className="text-red-400 shrink-0 mt-0.5" />
          <p className="text-sm text-red-400">
            Couldn't check quota right now. Try refreshing.
          </p>
        </div>
      )}

      {/* Available — real data */}
      {usageState === 'available' && usage?.available && (
        <div className="bg-slate-800/40 rounded-xl border border-slate-700 overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-700">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              {usage.provider}
            </span>
          </div>
          <div className="grid grid-cols-3 divide-x divide-slate-700">
            {[
              { label: 'Used', value: formatNumber(usage.used) },
              { label: 'Remaining', value: formatNumber(usage.remaining) },
              { label: 'Limit', value: formatNumber(usage.limit) },
            ].map(item => (
              <div key={item.label} className="px-4 py-3 text-center">
                <div className="text-lg font-bold text-slate-100">{item.value}</div>
                <div className="text-xs text-slate-500 mt-0.5">{item.label}</div>
              </div>
            ))}
          </div>
          {usage.last_checked && (
            <div className="px-4 py-2 border-t border-slate-700">
              <p className="text-xs text-slate-600">
                Last checked: {formatTime(usage.last_checked)}
                {usage.reset_at && ` · Resets at ${formatTime(usage.reset_at)}`}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UsagePanel;
