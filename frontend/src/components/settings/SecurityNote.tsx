"use client";
import React from 'react';
import { ShieldCheck } from 'lucide-react';

interface SecurityNoteProps {
  persistEnabled: boolean;
}

export const SecurityNote: React.FC<SecurityNoteProps> = ({ persistEnabled }) => (
  <div className="flex items-start gap-3 px-4 py-3 bg-slate-800/30 border border-slate-700/50 rounded-xl">
    <ShieldCheck size={15} className="text-blue-400/70 shrink-0 mt-0.5" />
    <p className="text-xs text-slate-500 leading-relaxed">
      Your key is used only for this classroom app and is never shared with anyone else.{' '}
      {persistEnabled
        ? 'It is saved in your browser\'s local storage so it survives page refreshes. Clear it any time with the "Remove Key" button.'
        : 'It is kept only for this browser session and will be forgotten when you close the tab.'}
    </p>
  </div>
);

export default SecurityNote;
