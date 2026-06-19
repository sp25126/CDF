import React from 'react';
import { motion } from 'framer-motion';
import { SearchX } from 'lucide-react';
import { theme } from '../design/theme';

interface EmptyStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

/**
 * EmptyState: Shown when a search or request returns no results.
 */
export const EmptyState: React.FC<EmptyStateProps> = ({ 
  title = "No Results Found", 
  message,
  onRetry
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center h-full text-center p-8 bg-slate-50 rounded-lg"
    >
      <SearchX size={48} className="text-slate-400 mb-4" />
      <h2 className="text-2xl font-bold text-slate-700">{title}</h2>
      <p className="text-lg text-slate-500 mt-2 mb-6 max-w-md">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-8 py-3 rounded-lg font-bold text-white"
          style={{backgroundColor: theme.colors.primary}}
        >
          Try Again
        </button>
      )}
    </motion.div>
  );
};

export default EmptyState;
