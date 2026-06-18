import React from 'react';
import { motion } from 'framer-motion';
import { Play } from 'lucide-react';

interface VideoRef {
    title: string;
    youtube_id: string;
    url?: string;
}

interface VideoCardsProps {
    videos: VideoRef[];
    reason?: string;
}

export const VideoCards: React.FC<VideoCardsProps> = ({ videos, reason }) => {
    if (!videos || videos.length === 0) return null;

    return (
        <div className="mt-4 space-y-3">
            {reason && (
                <p className="text-sm text-gray-600 dark:text-gray-400 italic">
                    {reason}
                </p>
            )}
            <div className="flex flex-col gap-4">
                {videos.map((vid, idx) => (
                    <motion.div 
                        key={vid.youtube_id || idx}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 * idx }}
                        className="flex flex-col md:flex-row gap-4 p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-sm"
                    >
                        <div className="relative w-full md:w-48 h-32 flex-shrink-0 rounded-lg overflow-hidden bg-gray-900 group">
                            <img 
                                src={`https://img.youtube.com/vi/${vid.youtube_id}/mqdefault.jpg`}
                                alt={vid.title}
                                className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"
                            />
                            <div className="absolute inset-0 flex items-center justify-center">
                                <div className="w-10 h-10 bg-red-600 rounded-full flex items-center justify-center text-white shadow-lg group-hover:scale-110 transition-transform">
                                    <Play size={20} className="ml-1" />
                                </div>
                            </div>
                            <a 
                                href={vid.url || `https://www.youtube.com/watch?v=${vid.youtube_id}`}
                                target="_blank" 
                                rel="noreferrer"
                                className="absolute inset-0 z-10"
                                aria-label={`Play ${vid.title}`}
                            />
                        </div>
                        <div className="flex flex-col justify-center">
                            <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
                                {vid.title}
                            </h4>
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                                YouTube Video
                            </p>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
};
