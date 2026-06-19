import React from 'react';
import { motion } from 'framer-motion';

interface MacroPillsProps {
  pills: string[];
  onPillClick: (pill: string) => void;
}

/**
 * MacroPills: A row of common command shortcuts.
 */
export const MacroPills: React.FC<MacroPillsProps> = ({ pills, onPillClick }) => {
  return (
    <div className="flex items-center gap-3">
      {pills.map((pill) => (
        <motion.button
          key={pill}
          onClick={() => onPillClick(pill)}
          className="px-5 py-2 rounded-full text-lg font-bold bg-[oklch(0.35_0.03_260)] text-white"
          whileHover={{ scale: 1.05, backgroundColor: 'oklch(0.4 0.03 260)' }}
          whileTap={{ scale: 0.95 }}
        >
          {pill}
        </motion.button>
      ))}
    </div>
  );
};

export default MacroPills;
