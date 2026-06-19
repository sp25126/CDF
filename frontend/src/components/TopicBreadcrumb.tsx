import React from 'react';
import { ChevronRight } from 'lucide-react';

interface TopicBreadcrumbProps {
  topic?: string;
  subtopic?: string;
}

/**
 * TopicBreadcrumb: Displays the current topic and subtopic.
 */
export const TopicBreadcrumb: React.FC<TopicBreadcrumbProps> = ({ topic, subtopic }) => {
  return (
    <div className="flex items-center text-xl text-slate-500 font-semibold">
      {topic ? (
        <>
          <span>{topic}</span>
          {subtopic && (
            <>
              <ChevronRight size={24} className="mx-2 text-slate-400" />
              <span className="text-slate-800 font-bold">{subtopic}</span>
            </>
          )}
        </>
      ) : (
        <span className="italic">No topic active</span>
      )}
    </div>
  );
};

export default TopicBreadcrumb;
