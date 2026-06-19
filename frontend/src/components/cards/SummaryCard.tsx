import React from 'react';
import { motion } from 'framer-motion';

/**
 * SummaryCard: A short recap of the current explanation.
 */
export const SummaryCard: React.FC<{ text: string }> = ({ text }) => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-4 bg-slate-50 rounded-lg border border-slate-200"
    >
      <h4 className="font-bold text-slate-800 mb-1">Summary</h4>
      <p className="text-slate-600">{text}</p>
    </motion.div>
  );
};

export default SummaryCard;
