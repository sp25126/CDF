import React from 'react';
import { motion } from 'framer-motion';
import { PlayCircle } from 'lucide-react';

export interface Video {
  title: string;
  thumbnail: string;
  source: string;
  reason: string;
}

/**
 * BestVideoCard: Displays the primary recommended video from a video payload object.
 */
export const BestVideoCard: React.FC<{ video: Video }> = ({ video }) => {
  if (!video || !video.thumbnail) return null;

  return (
    <a 
      href={video.source}
      target="_blank"
      rel="noreferrer"
      className="block"
    >
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative rounded-lg overflow-hidden cursor-pointer group border-2 border-indigo-500 shadow-lg"
      >
        <img src={video.thumbnail} alt={video.title} className="w-full h-auto object-cover transition-transform group-hover:scale-105" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
        <div className="absolute inset-0 flex items-center justify-center">
          <PlayCircle size={64} className="text-white/80 transition-all group-hover:text-white group-hover:scale-110" />
        </div>
        <div className="absolute bottom-0 left-0 p-4">
          <h4 className="font-bold text-white text-lg">{video.title}</h4>
          <p className="text-sm text-indigo-200">{video.reason}</p>
        </div>
      </motion.div>
    </a>
  );
};

export default BestVideoCard;
