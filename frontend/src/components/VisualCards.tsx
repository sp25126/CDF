import React from 'react';
import { motion } from 'framer-motion';
import { ImageFallback } from './ImageFallback';

interface VisualRef {
    type: string;
    url: string;
    description?: string;
    visual_id?: string;
    title?: string;
    alt_text?: string;
    source?: string;
    reason?: string;
}

interface VisualCardsProps {
    visuals: VisualRef[];
    reason?: string;
}

export const VisualCards: React.FC<VisualCardsProps> = ({ visuals, reason }) => {
    const [failedImages, setFailedImages] = React.useState<Record<number, boolean>>({});

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
                        className="overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm max-w-sm bg-white dark:bg-gray-800 flex flex-col"
                    >
                        {vis.title && (
                            <div className="p-3 bg-gray-50 dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700 font-medium text-sm text-gray-800 dark:text-gray-200">
                                {vis.title}
                            </div>
                        )}
                        <div className="relative">
                            {failedImages[idx] ? (
                                <ImageFallback />
                            ) : (
                                <img 
                                    src={vis.url} 
                                    alt={vis.alt_text || vis.description || "Visual aid"} 
                                    className="w-full h-auto object-contain max-h-64 bg-gray-50 dark:bg-gray-900"
                                    onError={() => setFailedImages(prev => ({ ...prev, [idx]: true }))}
                                />
                            )}
                        </div>
                        {(vis.description || vis.source) && (
                            <div className="p-3 bg-gray-50 dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300">
                                {vis.description && <p className="mb-1">{vis.description}</p>}
                                {vis.source && (
                                    <p className="text-xs text-gray-500 dark:text-gray-400">
                                        Source: {vis.source}
                                    </p>
                                )}
                            </div>
                        )}
                    </motion.div>
                ))}
            </div>
        </div>
    );
};
