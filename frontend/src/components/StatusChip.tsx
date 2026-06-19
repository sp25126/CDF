import React from 'react';
import { theme } from '../design/theme';

interface StatusChipProps {
  label: string;
  value: string;
  color?: 'primary' | 'neutral' | 'success' | 'warning' | 'error';
}

/**
 * StatusChip: A small, colored badge for displaying a status.
 */
export const StatusChip: React.FC<StatusChipProps> = ({ label, value, color = 'neutral' }) => {
  const colors = {
    primary: {
      bg: 'bg-indigo-100',
      text: 'text-indigo-800',
    },
    neutral: {
      bg: 'bg-slate-100',
      text: 'text-slate-600',
    },
    success: {
      bg: 'bg-green-100',
      text: 'text-green-800',
    },
    warning: {
      bg: 'bg-amber-100',
      text: 'text-amber-800',
    },
    error: {
      bg: 'bg-red-100',
      text: 'text-red-800',
    },
  };
  
  const selectedColor = colors[color];

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${selectedColor.bg}`}>
      <span className={`text-sm font-bold uppercase tracking-wider ${selectedColor.text}`}>{label}</span>
      <span className={`text-sm font-semibold ${selectedColor.text}`}>{value}</span>
    </div>
  );
};

export default StatusChip;
