import React from 'react';
import { motion } from 'framer-motion';

interface ToggleButtonProps {
  label: string;
  isActive: boolean;
  onClick: () => void;
  icon?: React.ReactNode;
}

/**
 * ToggleButton: A generic toggle button for the teacher console.
 */
export const ToggleButton: React.FC<ToggleButtonProps> = ({ label, isActive, onClick, icon }) => {
  return (
    <motion.button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-3 rounded-lg font-bold shadow-md
        ${
          isActive
            ? 'bg-green-600 text-white'
            : 'bg-[oklch(0.35_0.03_260)] text-slate-300'
        }`}
      whileHover={{ scale: 1.05, backgroundColor: isActive ? '#15803d' : 'oklch(0.4 0.03 260)' }}
      whileTap={{ scale: 0.95 }}
    >
      {icon}
      <span>{label}</span>
    </motion.button>
  );
};

export default ToggleButton;
