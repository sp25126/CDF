import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle } from 'lucide-react';
import { theme } from '../design/theme';

interface ErrorStateCardProps {
  title?: string;
  message: string;
  onRetry: () => void;
}

/**
 * ErrorStateCard: A friendly fallback card for when API calls or rendering fails.
 */
export const ErrorStateCard: React.FC<ErrorStateCardProps> = ({ 
  title = "An Error Occurred", 
  message, 
  onRetry 
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center h-full text-center p-8 bg-red-50 rounded-lg border-2 border-dashed border-red-200"
    >
      <AlertTriangle size={48} className="text-red-500 mb-4" />
      <h2 className="text-2xl font-bold text-red-800">{title}</h2>
      <p className="text-lg text-red-600 mt-2 mb-6 max-w-md">{message}</p>
      <button
        onClick={onRetry}
        className="px-8 py-3 rounded-lg font-bold text-white bg-red-600 hover:bg-red-700 transition-colors"
      >
        Try Again
      </button>
    </motion.div>
  );
};

export default ErrorStateCard;
