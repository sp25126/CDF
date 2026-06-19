import React from 'react';
import { theme } from '../design/theme';
import StatusChip from './StatusChip';
import TopicBreadcrumb from './TopicBreadcrumb';

interface TopContextBarProps {
  languageMode?: string;
  isHandsFree?: boolean;
  isSourceMode?: boolean;
  confidence?: number;
  /** Topic title from the last assistant response. Undefined until first command. */
  currentTopic?: string;
}

/**
 * TopContextBar: Student-facing context anchor.
 * Always rendered (SSR + client) so there is never a hydration mismatch.
 * The topic text is only shown once a response has been received.
 */
export const TopContextBar: React.FC<TopContextBarProps> = ({
  languageMode = 'Hinglish',
  isHandsFree = false,
  isSourceMode = false,
  confidence,
  currentTopic,
}) => {
  return (
    <header
      className="h-16 flex items-center justify-between px-8 bg-white border-b"
      style={{ borderColor: theme.colors.canvas.border }}
    >
      {/* Left Zone: App Name */}
      <div className="flex items-baseline gap-3">
        <h1 className="text-2xl font-bold" style={{ color: theme.colors.canvas.ink }}>
          Shiksha Sahayak
        </h1>
        <p className="text-md font-medium" style={{ color: theme.colors.canvas.muted }}>
          AI Classroom Assistant
        </p>
      </div>

      {/* Center Zone: Topic — stable DOM node, content changes */}
      <div className="absolute left-1/2 -translate-x-1/2">
        {currentTopic
          ? <TopicBreadcrumb topic={currentTopic} />
          : <span className="text-sm font-medium" style={{ color: theme.colors.canvas.muted }}>Awaiting topic…</span>
        }
      </div>

      {/* Right Zone: Status Chips */}
      <div className="flex items-center gap-3">
        <StatusChip label="LANG" value={languageMode} color="primary" />
        {isHandsFree && <StatusChip label="HANDS-FREE" value="ON" color="success" />}
        {isSourceMode && <StatusChip label="SOURCE" value="ON" color="warning" />}
        {confidence && confidence > 0 && (
          <StatusChip label="CONF" value={`${Math.round(confidence * 100)}%`} color="neutral" />
        )}
      </div>
    </header>
  );
};

export default TopContextBar;
