import React from 'react';
import { Lightbulb } from 'lucide-react';
import { theme } from '../../design/theme';

interface AnalogyCardProps {
  text: string;
}

/**
 * AnalogyCard: A visually distinct card for displaying analogies.
 */
export const AnalogyCard: React.FC<AnalogyCardProps> = ({ text }) => {
  return (
    <div 
      className="p-6 rounded-lg flex items-start gap-5"
      style={{ backgroundColor: 'oklch(0.95 0.05 260)', border: `1px solid ${'oklch(0.9 0.08 260)'}` }}
    >
      <Lightbulb size={32} className="mt-1 flex-shrink-0" style={{ color: theme.colors.primary }} />
      <div>
        <h3 className="font-bold text-lg mb-1" style={{ color: theme.colors.canvas.ink }}>Analogy</h3>
        <p style={{ fontSize: theme.typography.fontSize.base, color: theme.colors.canvas.muted }}>
          {text}
        </p>
      </div>
    </div>
  );
};

export default AnalogyCard;
