import React from 'react';
import { useTranscriptStore } from '../state/transcriptStore';
import { useAppState } from '../state/useAppState';
import { useAppEvents } from '../state/useAppEvents';

/**
 * TranscriptStrip: A small strip showing the last commands from the global store.
 * Clicking a command restores its context without a backend call.
 */
export const TranscriptStrip: React.FC = () => {
  const history = useTranscriptStore((state) => state.history);
  const { transitionTo } = useAppState();
  const { dispatch } = useAppEvents();

  const handleRestore = (entry: any) => {
    if (entry.payload) {
      const mode = entry.payload.mode || "explain";
      let nextState = "explaining";
      if (mode === "quiz" || mode === "ask_question") nextState = "quiz_active";
      transitionTo(nextState as any, { payload: entry.payload });
      dispatch({ type: "RESPONSE_RECEIVED", payload: entry.payload });
    }
  };

  return (
    <div className="h-full flex flex-col justify-center gap-1 text-right pr-2">
      {history.slice(0, 3).map((entry) => (
        <p 
          key={entry.id} 
          className={`text-sm truncate ${entry.payload ? 'text-slate-400 cursor-pointer hover:text-blue-400 transition-colors' : 'text-slate-500'}`}
          onClick={() => handleRestore(entry)}
          title={entry.payload ? "Click to restore this context" : "Context not available"}
        >
          &raquo; {entry.command}
        </p>
      ))}
    </div>
  );
};

export default TranscriptStrip;
