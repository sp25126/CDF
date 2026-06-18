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

const ImagePlaceholder: React.FC = () => (
    <div className="w-64 h-48 flex flex-col items-center justify-center bg-gray-100 dark:bg-gray-700 text-gray-400 p-4 select-none">
        <svg className="w-10 h-10 mb-2 opacity-60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Preview not available</span>
    </div>
);

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
                        className="overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm max-w-sm bg-white dark:bg-gray-800"
                    >
                        {failedImages[idx] ? (
                            <ImagePlaceholder />
                        ) : (
                            <img 
                                src={vis.url} 
                                alt={vis.description || "Visual aid"} 
                                className="w-full h-auto object-contain max-h-64 bg-gray-50 dark:bg-gray-900"
                                onError={() => setFailedImages(prev => ({ ...prev, [idx]: true }))}
                            />
                        )}
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
