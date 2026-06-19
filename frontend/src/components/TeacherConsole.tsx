import React from 'react';
import { Send, Headset, Book, RotateCcw, Trash2, PenTool } from 'lucide-react';
import { theme } from '../design/theme';
import MicButton from './MicButton';
import MacroPills from './MacroPills';
import TranscriptStrip from './TranscriptStrip';
import ToggleButton from './ToggleButton';

// This component now receives the state and functions from a higher-level hook
interface TeacherConsoleProps {
  isListening: boolean;
  isHandsFree: boolean;
  isSourceMode: boolean;
  command: string;
  lastCommands: string[];
  isLoading: boolean; // For showing loading state on submit
  isWhiteboardActive: boolean;
  onCommandChange: (cmd: string) => void;
  onCommandSubmit: () => void;
  onListenClick: () => void;
  onHandsFreeToggle: () => void;
  onSourceModeToggle: () => void;
  onWhiteboardToggle: () => void;
  onRepeatClick: () => void;
  onClearClick: () => void;
  onMacroPillClick: (pill: string) => void;
}

/**
 * TeacherConsole: The persistent control bar at the bottom of the screen.
 */
export const TeacherConsole: React.FC<TeacherConsoleProps> = (props) => {
  return (
    <footer
      className="teacher-console-zone p-4 flex flex-col gap-3"
      style={{
        backgroundColor: theme.colors.console.bg,
        color: theme.colors.console.ink,
        boxShadow: '0 -4px 15px rgba(0,0,0,0.1)',
      }}
    >
      {/* Top Row: Macro Pills & Toggles */}
      <div className="flex flex-col md:flex-row items-center justify-between px-2 gap-3 md:gap-0">
        <div className="flex items-center w-full md:w-auto overflow-x-auto pb-1 md:pb-0 hide-scrollbar">
            <MacroPills pills={['Explain', 'Quiz', 'Simpler', 'Example', 'Deep Dive']} onPillClick={props.onMacroPillClick} />
        </div>
        <div className="flex items-center gap-3 flex-wrap justify-center w-full md:w-auto">
            <ToggleButton
                label="Hands Free"
                isActive={props.isHandsFree}
                onClick={props.onHandsFreeToggle}
                icon={<Headset size={18} />}
            />
            <ToggleButton
                label="Source Mode"
                isActive={props.isSourceMode}
                onClick={props.onSourceModeToggle}
                icon={<Book size={18} />}
            />
            <ToggleButton
                label="Whiteboard"
                isActive={props.isWhiteboardActive}
                onClick={props.onWhiteboardToggle}
                icon={<PenTool size={18} />}
            />
        </div>
      </div>

      {/* Bottom Row: Transcript, Input, Utilities */}
      <div className="flex flex-col md:flex-row items-center gap-4 px-2 w-full">
        {/* Left: Transcript */}
        <div className="w-full md:w-1/4">
          <TranscriptStrip />
        </div>

        {/* Center: Search Bar */}
        <div className="w-full md:flex-1 flex items-center bg-[oklch(0.3_0.03_260)] rounded-full border border-slate-700 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20 transition-all shadow-inner px-2 py-1">
          <input
            type="text"
            value={props.command}
            onChange={(e) => props.onCommandChange(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && props.onCommandSubmit()}
            placeholder="Type a command or speak..."
            className="flex-1 bg-transparent px-4 py-3 text-lg outline-none placeholder-slate-400"
            disabled={props.isHandsFree || props.isLoading}
          />
          <div className="flex items-center gap-2 pr-2">
            <MicButton isListening={props.isListening} onClick={props.onListenClick} />
            <button
              onClick={props.onCommandSubmit}
              className="p-3 rounded-full text-white shadow-md transition-all hover:scale-105 active:scale-95"
              style={{ backgroundColor: theme.colors.primary }}
              disabled={props.isLoading}
              title="Send Command"
            >
              {props.isLoading ? (
                <div className="w-6 h-6 border-4 border-t-transparent border-white rounded-full animate-spin" />
              ) : (
                <Send size={22} />
              )}
            </button>
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2 shrink-0">
          <button onClick={props.onRepeatClick} className="p-3 rounded-full bg-[oklch(0.35_0.03_260)] hover:bg-[oklch(0.4_0.03_260)] transition-colors text-slate-300 hover:text-white" title="Repeat Audio">
            <RotateCcw size={22} />
          </button>
          <button onClick={props.onClearClick} className="p-3 rounded-full bg-[oklch(0.35_0.03_260)] hover:bg-red-500/20 hover:text-red-400 transition-colors text-slate-300" title="Clear Session">
            <Trash2 size={22} />
          </button>
        </div>
      </div>
    </footer>
  );
};

export default TeacherConsole;
