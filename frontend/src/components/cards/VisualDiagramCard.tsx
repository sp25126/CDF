import React from 'react';
import { motion } from 'framer-motion';

export interface Visual {
  src: string;
  alt: string;
}

/**
 * VisualDiagramCard: Displays a diagram or image from a visual payload object.
 */
export const VisualDiagramCard: React.FC<{ visual: Visual }> = ({ visual }) => {
  if (!visual || !visual.src) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-lg overflow-hidden border border-slate-200 shadow-sm"
    >
      <img src={visual.src} alt={visual.alt} className="w-full h-auto object-cover" />
    </motion.div>
  );
};

export default VisualDiagramCard;
