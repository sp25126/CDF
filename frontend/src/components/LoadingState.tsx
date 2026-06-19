import React from 'react';
import { motion } from 'framer-motion';
import { Skeletons } from './Skeletons';

/**
 * LoadingState: A full-canvas loading placeholder with skeletons.
 */
export const LoadingState: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <Skeletons.ExplainCard />
    </motion.div>
  );
};

export default LoadingState;
