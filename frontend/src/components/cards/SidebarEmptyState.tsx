import React from 'react';
import { motion } from 'framer-motion';
import { Image } from 'lucide-react';

/**
 * SidebarEmptyState: A placeholder shown in the media rail when no media is available.
 */
export const SidebarEmptyState: React.FC = () => {
  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col items-center justify-center h-full text-center p-8"
    >
      <div className="p-4 bg-slate-100 rounded-full mb-4">
        <Image size={32} className="text-slate-400" />
      </div>
      <h4 className="font-bold text-slate-600">No Media Available</h4>
      <p className="text-slate-500 text-sm">Supporting visuals will appear here.</p>
    </motion.div>
  );
};

export default SidebarEmptyState;
