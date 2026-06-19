import React from 'react';
import { motion } from 'framer-motion';
import { Mic } from 'lucide-react';
import { theme } from '../design/theme';

interface MicButtonProps {
  isListening: boolean;
  onClick: () => void;
}

/**
 * MicButton: The large "Listen" button in the teacher console.
 */
export const MicButton: React.FC<MicButtonProps> = ({ isListening, onClick }) => {
  return (
    <button onClick={onClick} className="relative">
      <motion.div
        className="w-24 h-24 rounded-full flex items-center justify-center text-white shadow-lg"
        style={{
          backgroundColor: isListening ? theme.colors.error : theme.colors.primary,
        }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.9 }}
        transition={{ duration: 0.1 }}
      >
        <Mic size={48} />
      </motion.div>
      {isListening && (
        <motion.div
          className="absolute inset-0 rounded-full"
          style={{
            border: `4px solid ${theme.colors.error}`,
          }}
          animate={{
            scale: [1, 1.4, 1],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      )}
    </button>
  );
};

export default MicButton;
