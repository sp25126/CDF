import React from 'react';
import { Send, Headset, Book, RotateCcw, Trash2 } from 'lucide-react';
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
  onCommandChange: (cmd: string) => void;
  onCommandSubmit: () => void;
  onListenClick: () => void;
  onHandsFreeToggle: () => void;
  onSourceModeToggle: () => void;
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
      className="teacher-console-zone p-6 relative"
      style={{
        backgroundColor: theme.colors.console.bg,
        color: theme.colors.console.ink,
        boxShadow: '0 -4px 15px rgba(0,0,0,0.1)',
      }}
    >
      <div className="grid grid-cols-4 items-center gap-6 h-full">
        {/* Left Zone: Transcript Strip */}
        <div className="col-span-1">
          <TranscriptStrip />
        </div>

        {/* Center Zone: Input & Listen */}
        <div className="col-span-2 flex items-center justify-center gap-4">
          <div className="flex-1 flex items-center">
            <input
              type="text"
              value={props.command}
              onChange={(e) => props.onCommandChange(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && props.onCommandSubmit()}
              placeholder="Enter teacher command..."
              className="flex-1 px-5 py-4 rounded-l-xl text-xl border-2 border-r-0"
              style={{
                backgroundColor: 'oklch(0.3 0.03 260)',
                borderColor: theme.colors.console.border,
              }}
              disabled={props.isHandsFree || props.isLoading}
            />
            <button
              onClick={props.onCommandSubmit}
              className="p-4 rounded-r-xl"
              style={{ backgroundColor: theme.colors.primary, border: `2px solid ${theme.colors.primary}` }}
              disabled={props.isLoading}
            >
              {props.isLoading ? (
                <div className="w-8 h-8 border-4 border-t-transparent border-white rounded-full animate-spin" />
              ) : (
                <Send size={32} />
              )}
            </button>
          </div>
          <MicButton isListening={props.isListening} onClick={props.onListenClick} />
        </div>

        {/* Right Zone: Toggles & Actions */}
        <div className="col-span-1 flex items-center justify-end gap-3">
            <ToggleButton
                label="Hands Free"
                isActive={props.isHandsFree}
                onClick={props.onHandsFreeToggle}
                icon={<Headset size={20} />}
            />
            <ToggleButton
                label="Source Mode"
                isActive={props.isSourceMode}
                onClick={props.onSourceModeToggle}
                icon={<Book size={20} />}
            />
            <button onClick={props.onRepeatClick} className="p-3 rounded-lg bg-[oklch(0.35_0.03_260)] hover:bg-[oklch(0.4_0.03_260)]"><RotateCcw size={24} /></button>
            <button onClick={props.onClearClick} className="p-3 rounded-lg bg-[oklch(0.35_0.03_260)] hover:bg-[oklch(0.4_0.03_260)]"><Trash2 size={24} /></button>
        </div>
      </div>
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2">
        <MacroPills pills={['Explain', 'Quiz', 'Simpler', 'Example', 'Deep Dive']} onPillClick={props.onMacroPillClick} />
      </div>
    </footer>
  );
};

export default TeacherConsole;
