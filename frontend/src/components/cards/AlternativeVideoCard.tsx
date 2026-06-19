import React from 'react';
import { ChevronDown } from 'lucide-react';
import { Video } from './BestVideoCard'; // Import the Video type

interface AlternativeVideoCardProps {
  videos: Video[];
}

/**
 * AlternativeVideoCard: A collapsed list of other video options from the payload.
 */
export const AlternativeVideoCard: React.FC<AlternativeVideoCardProps> = ({ videos }) => {
  const [isOpen, setIsOpen] = React.useState(false);

  if (!videos || videos.length === 0) return null;

  return (
    <div className="bg-slate-50 rounded-lg border border-slate-200">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex justify-between items-center p-4 font-bold text-slate-700"
      >
        <span>Alternative Videos ({videos.length})</span>
        <ChevronDown size={20} className={`transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      {isOpen && (
        <div className="p-4 border-t border-slate-200 space-y-3">
          {videos.map((video, i) => (
            <a 
              key={i}
              href={video.source}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-3 cursor-pointer hover:bg-slate-100 p-2 rounded-md block w-full text-left"
            >
              <img src={video.thumbnail} alt={video.title} className="w-24 h-14 rounded object-cover" />
              <p className="flex-1 font-semibold text-slate-600 text-sm">{video.title}</p>
            </a>
          ))}
        </div>
      )}
    </div>
  );
};

export default AlternativeVideoCard;
