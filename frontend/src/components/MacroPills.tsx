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
    <div className="flex flex-nowrap md:flex-wrap items-center gap-2 md:gap-3">
      {pills.map((pill) => (
        <motion.button
          key={pill}
          onClick={() => onPillClick(pill)}
          className="whitespace-nowrap px-3 py-1.5 md:px-5 md:py-2 rounded-full text-sm md:text-lg font-bold bg-[oklch(0.35_0.03_260)] text-white"
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
