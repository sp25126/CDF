import React from 'react';
import { motion } from 'framer-motion';
import { useReducedMotion } from '../hooks/useReducedMotion';

interface JuliEStateRingProps {
  state: 'idle' | 'listening' | 'speaking' | 'thinking' | 'quiz';
}

const stateColors = {
  idle: 'oklch(0.9 0.01 260)',
  listening: 'oklch(0.8 0.15 85)', // Amber
  speaking: 'oklch(0.7 0.1 220)', // Blue
  thinking: 'oklch(0.85 0.08 260)',
  quiz: 'oklch(0.65 0.15 150)', // Green
};

const pulseVariants = {
  animate: { 
    scale: [1, 1.05, 1],
    opacity: [0.8, 1, 0.8],
    transition: {
      duration: 2.5,
      repeat: Infinity,
      ease: 'easeInOut'
    }
  }
};

const shimmerVariants = {
    animate: {
        opacity: [0.7, 1, 0.7],
        transition: {
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut'
        }
    }
}

/**
 * JuliEStateRing: A colored ring around the avatar indicating the current state.
 */
export const JuliEStateRing: React.FC<JuliEStateRingProps> = ({ state }) => {
  const prefersReducedMotion = useReducedMotion();
  const color = stateColors[state] || stateColors.idle;
  
  let variants = {};
  if (!prefersReducedMotion) {
    if (state === 'listening' || state === 'speaking') {
      variants = pulseVariants;
    }
    if (state === 'thinking') {
        variants = shimmerVariants;
    }
  }

  return (
    <motion.div
      className="absolute inset-0 rounded-full"
      style={{
        boxShadow: `0 0 0 6px ${color}`,
        transition: 'box-shadow 0.4s ease',
      }}
      variants={variants}
      animate="animate"
    />
  );
};

export default JuliEStateRing;
