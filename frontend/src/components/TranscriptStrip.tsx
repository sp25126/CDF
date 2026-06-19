import React from 'react';
import { useTranscriptStore } from '../state/transcriptStore';

/**
 * TranscriptStrip: A small strip showing the last commands from the global store.
 */
export const TranscriptStrip: React.FC = () => {
  const history = useTranscriptStore((state) => state.history);

  return (
    <div className="h-full flex flex-col justify-center gap-1 text-right">
      {history.slice(0, 2).map((entry) => (
        <p key={entry.id} className="text-sm text-slate-400 truncate">
          &raquo; {entry.command}
        </p>
      ))}
    </div>
  );
};

export default TranscriptStrip;
