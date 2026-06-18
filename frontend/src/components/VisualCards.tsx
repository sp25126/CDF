import React from 'react';
import { motion } from 'framer-motion';

interface VisualRef {
    type: string;
    url: string;
    description?: string;
    visual_id?: string;
}

interface VisualCardsProps {
    visuals: VisualRef[];
    reason?: string;
}

export const VisualCards: React.FC<VisualCardsProps> = ({ visuals, reason }) => {
    if (!visuals || visuals.length === 0) return null;

    return (
        <div className="mt-4 space-y-3">
            {reason && (
                <p className="text-sm text-gray-600 dark:text-gray-400 italic">
                    {reason}
                </p>
            )}
            <div className="flex flex-wrap gap-4">
                {visuals.map((vis, idx) => (
                    <motion.div 
                        key={vis.visual_id || idx}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 * idx }}
                        className="overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm max-w-sm bg-white dark:bg-gray-800"
                    >
                        <img 
                            src={vis.url} 
                            alt={vis.description || "Visual aid"} 
                            className="w-full h-auto object-contain max-h-64 bg-gray-50 dark:bg-gray-900"
                        />
                        {vis.description && (
                            <div className="p-3 bg-gray-50 dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700 text-sm text-center text-gray-700 dark:text-gray-300">
                                {vis.description}
                            </div>
                        )}
                    </motion.div>
                ))}
            </div>
        </div>
    );
};
