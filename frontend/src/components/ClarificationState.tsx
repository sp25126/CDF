/**
 * ClarificationState component.
 * Displays when the assistant needs clarification (unclear intent).
 */

import { AlertCircle } from "lucide-react";

interface ClarificationStateProps {
  message?: string;
  suggestions?: string[];
  onSuggestionClick?: (suggestion: string) => void;
}

export function ClarificationState({
  message = "I didn't understand that. Please try again or select a suggestion below.",
  suggestions = [],
  onSuggestionClick,
}: ClarificationStateProps) {
  return (
    <div className="space-y-6">
      {/* Clarification Alert */}
      <div className="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-6 flex gap-4">
        <AlertCircle className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="font-semibold text-yellow-900 text-lg mb-2">
            Clarification Needed
          </h3>
          <p className="text-yellow-800 text-base">{message}</p>
        </div>
      </div>

      {/* Suggestions */}
      {suggestions && suggestions.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
            Try one of these:
          </p>
          <div className="grid gap-2">
            {suggestions.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => onSuggestionClick?.(suggestion)}
                className="w-full text-left px-4 py-3 bg-gradient-to-r from-indigo-50 to-blue-50 border-2 border-indigo-200 hover:border-indigo-500 hover:from-indigo-100 hover:to-blue-100 rounded-lg transition-all duration-200 font-medium text-indigo-900"
              >
                → {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Help Text */}
      <div className="bg-blue-50 border-l-4 border-blue-500 pl-4 py-3">
        <p className="text-sm text-blue-900">
          <span className="font-semibold">Tip:</span> You can ask to explain a
          topic, quiz a topic, or use simple commands.
        </p>
      </div>
    </div>
  );
}
