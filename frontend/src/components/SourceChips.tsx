import React from 'react';
import { motion } from 'framer-motion';

interface SourceRef {
    title: string;
    snippet: string;
    page_number?: number;
    section_label?: string;
}

interface SourceChipsProps {
    citations: SourceRef[];
}

export const SourceChips: React.FC<SourceChipsProps> = ({ citations }) => {
    if (!citations || citations.length === 0) return null;

    return (
        <div className="mt-4 flex flex-wrap gap-2">
            <span className="text-sm font-semibold text-gray-600 dark:text-gray-400 mt-1">Sources:</span>
            {citations.map((cite, index) => (
                <motion.div 
                    key={index}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.1 * index }}
                    className="group relative cursor-help"
                >
                    <div className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-full border border-blue-200 dark:border-blue-800 transition-colors hover:bg-blue-200 dark:hover:bg-blue-800/50">
                        {cite.title} {cite.page_number ? `(p. ${cite.page_number})` : ''}
                    </div>
                    {/* Tooltip */}
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-2 bg-gray-900 text-white text-xs rounded shadow-lg opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-10 text-center">
                        <span className="line-clamp-3">{cite.snippet}</span>
                        {cite.section_label && <div className="mt-1 font-bold">{cite.section_label}</div>}
                    </div>
                </motion.div>
            ))}
        </div>
    );
};
