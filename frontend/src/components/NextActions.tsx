/**
 * NextActions component.
 * Displays suggested next actions/commands for the teacher.
 */

import { ArrowRight } from "lucide-react";

interface NextActionsProps {
  next_actions: string[];
  onActionClick?: (action: string) => void;
}

export function NextActions({ next_actions, onActionClick }: NextActionsProps) {
  if (!next_actions || next_actions.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      <p className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
        What would you like to do next?
      </p>
      <div className="grid gap-2">
        {next_actions.map((action, idx) => (
          <button
            key={idx}
            onClick={() => onActionClick?.(action)}
            className="group text-left w-full px-4 py-3 bg-white border-2 border-gray-300 hover:border-indigo-500 hover:bg-indigo-50 rounded-lg transition-all duration-200 flex items-center justify-between"
          >
            <span className="text-gray-800 group-hover:text-indigo-700 font-medium">
              {action}
            </span>
            <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-indigo-600 transition-colors" />
          </button>
        ))}
      </div>
    </div>
  );
}
