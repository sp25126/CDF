import React from 'react';

export interface Source {
    id: string;
    title: string;
}

/**
 * SourceChips: A list of chips linking to source materials from the payload.
 */
export const SourceChips: React.FC<{ sources: Source[] }> = ({ sources }) => {
  if (!sources || sources.length === 0) return null;

  return (
    <div>
        <h4 className="font-bold text-slate-800 mb-2">Sources</h4>
        <div className="flex flex-wrap gap-2">
            {sources.map(source => (
                <button key={source.id} className="px-3 py-1 bg-slate-200 text-slate-700 rounded-full text-sm font-semibold hover:bg-slate-300 transition-colors">
                {source.title}
                </button>
            ))}
        </div>
    </div>
  );
};

export default SourceChips;
