import React from 'react';
import { motion } from 'framer-motion';
import { theme } from '../../design/theme';
import AnalogyCard from './AnalogyCard';
import FollowUpPills from './FollowUpPills';

export interface Explanation {
  title: string;
  points: string[];
  analogy: string;
}

interface ExplainCardProps {
  explanation: Explanation;
  actions: string[];
  onActionClick: (action: string) => void;
}

/**
 * ExplainCard: Displays a full explanation with title, bullets, and analogy from live data.
 */
export const ExplainCard: React.FC<ExplainCardProps> = ({ explanation, actions, onActionClick }) => {
  if (!explanation) return null;

  const { title, points, analogy } = explanation;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="space-y-8"
    >
      <h1 style={{ fontSize: theme.typography.fontSize['3xl'], color: theme.colors.canvas.ink }} className="font-bold">
        {title}
      </h1>

      {points && points.length > 0 && (
        <ul className="space-y-4">
          {points.slice(0, 7).map((point, index) => ( // Max 7 bullets
            <li key={index} className="flex items-start gap-4">
              <span style={{ color: theme.colors.primary }} className="text-2xl font-bold mt-1">
                •
              </span>
              <p style={{ fontSize: theme.typography.fontSize.lg, color: theme.colors.canvas.ink }}>
                {point}
              </p>
            </li>
          ))}
        </ul>
      )}
      
      {analogy && <AnalogyCard text={analogy} />}
      
      {actions && actions.length > 0 && (
        <FollowUpPills options={actions} onPillClick={onActionClick} />
      )}

    </motion.div>
  );
};

export default ExplainCard;
