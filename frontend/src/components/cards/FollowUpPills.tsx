import React from 'react';
import { theme } from '../../design/theme';

interface FollowUpPillsProps {
  options: string[];
  onPillClick: (option: string) => void;
}

/**
 * FollowUpPills: A list of pill-shaped buttons for next actions.
 */
export const FollowUpPills: React.FC<FollowUpPillsProps> = ({ options, onPillClick }) => {
  return (
    <div className="flex flex-wrap items-center gap-4 pt-4">
      <p className="font-semibold text-lg" style={{ color: theme.colors.canvas.muted }}>
        Next:
      </p>
      {options.map((option) => (
        <button
          key={option}
          onClick={() => onPillClick(option)}
          className="px-6 py-3 rounded-full font-bold bg-white border transition-all hover:bg-slate-50 hover:shadow-sm active:scale-95"
          style={{ 
            color: theme.colors.primary, 
            borderColor: 'oklch(0.85 0.05 260)',
            fontSize: theme.typography.fontSize.base,
          }}
        >
          {option}
        </button>
      ))}
    </div>
  );
};

export default FollowUpPills;
