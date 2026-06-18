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

    const primaryVideo = videos[0];
    const alternativeVideos = videos.slice(1);

    return (
        <div className="mt-4 space-y-4">
            {reason && (
                <p className="text-sm text-gray-600 dark:text-gray-400 italic">
                    {reason}
                </p>
            )}
            <div className="flex flex-col gap-4">
                {/* Primary Video */}
                <motion.div 
                    key={primaryVideo.youtube_id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex flex-col md:flex-row gap-4 p-4 rounded-xl border-2 border-blue-200 dark:border-blue-800 bg-white dark:bg-gray-800 shadow-md relative overflow-hidden"
                >
                    <div className="absolute top-0 left-0 bg-blue-500 text-white text-xs font-bold px-2 py-1 rounded-br-lg z-20">
                        Top Recommendation
                    </div>
                    <div className="relative w-full md:w-64 h-40 flex-shrink-0 rounded-lg overflow-hidden bg-gray-900 group mt-4 md:mt-0">
                        <img 
                            src={`https://img.youtube.com/vi/${primaryVideo.youtube_id}/mqdefault.jpg`}
                            alt={primaryVideo.title}
                            className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"
                        />
                        <div className="absolute inset-0 flex items-center justify-center">
                            <div className="w-12 h-12 bg-red-600 rounded-full flex items-center justify-center text-white shadow-lg group-hover:scale-110 transition-transform">
                                <Play size={24} className="ml-1" />
                            </div>
                        </div>
                        <a 
                            href={primaryVideo.url || `https://www.youtube.com/watch?v=${primaryVideo.youtube_id}`}
                            target="_blank" 
                            rel="noreferrer"
                            className="absolute inset-0 z-10"
                            aria-label={`Play ${primaryVideo.title}`}
                        />
                    </div>
                    <div className="flex flex-col justify-center">
                        <h4 className="font-bold text-lg text-gray-900 dark:text-white mb-2">
                            {primaryVideo.title}
                        </h4>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                            YouTube Video • Primary Selection
                        </p>
                    </div>
                </motion.div>

                {/* Alternative Videos */}
                {alternativeVideos.length > 0 && (
                    <div className="mt-2">
                        <h5 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Alternatives</h5>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            {alternativeVideos.map((vid, idx) => (
                                <motion.div 
                                    key={vid.youtube_id || idx}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: 0.2 + (0.1 * idx) }}
                                    className="flex flex-row gap-3 p-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 hover:bg-white dark:hover:bg-gray-800 transition-colors"
                                >
                                    <div className="relative w-24 h-16 flex-shrink-0 rounded bg-gray-900 group overflow-hidden">
                                        <img 
                                            src={`https://img.youtube.com/vi/${vid.youtube_id}/default.jpg`}
                                            alt={vid.title}
                                            className="w-full h-full object-cover opacity-70 group-hover:opacity-100 transition-opacity"
                                        />
                                        <div className="absolute inset-0 flex items-center justify-center">
                                            <div className="w-6 h-6 bg-red-600/80 rounded-full flex items-center justify-center text-white">
                                                <Play size={12} className="ml-0.5" />
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
                                    <div className="flex flex-col justify-center overflow-hidden">
                                        <h4 className="font-medium text-sm text-gray-800 dark:text-gray-200 truncate">
                                            {vid.title}
                                        </h4>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
