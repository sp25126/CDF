/**
 * ResponseRenderer component.
 * Main component that renders the backend AssistantResponse deterministically.
 * Routes to appropriate sub-components based on mode.
 */

import { AssistantResponse } from "@/types/api";
import { AnswerBubble } from "./AnswerBubble";
import { QuizCard } from "./QuizCard";
import { LanguageBadge } from "./LanguageBadge";
import { NextActions } from "./NextActions";
import { ClarificationState } from "./ClarificationState";
import { AlertCircle, CheckCircle } from "lucide-react";

interface ResponseRendererProps {
  response: AssistantResponse;
  onNextAction?: (action: string) => void;
  onQuizNavigate?: (questionIndex: number) => void;
  onQuizAnswerSubmit?: (questionIndex: number, selectedIndex: number) => void;
}

export function ResponseRenderer({
  response,
  onNextAction,
  onQuizNavigate,
  onQuizAnswerSubmit,
}: ResponseRendererProps) {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header with Language Badge and Confidence */}
      <div className="flex items-center justify-between gap-4">
        <LanguageBadge language_mode={response.language_mode} />
        <div className="text-sm text-gray-600 flex items-center gap-2">
          <span>Confidence: {(response.confidence * 100).toFixed(0)}%</span>
        </div>
      </div>

      {/* Mode Indicator */}
      <div className="flex items-center gap-2 text-sm font-medium">
        <span className="px-3 py-1 rounded-full bg-gray-100 text-gray-700">
          Mode: {response.mode.toUpperCase()}
        </span>
        {response.requires_clarification && (
          <span className="px-3 py-1 rounded-full bg-yellow-100 text-yellow-700 flex items-center gap-1">
            <AlertCircle className="w-3 h-3" />
            Clarification needed
          </span>
        )}
      </div>

      {/* Main Content - Route by Mode */}
      {response.mode === "clarify" || response.mode === "unclear" || response.requires_clarification ? (
        <ClarificationState
          message={response.answer_text}
          suggestions={response.next_actions}
          onSuggestionClick={onNextAction}
        />
      ) : response.mode === "quiz" && response.quiz ? (
        <QuizCard
          quiz={response.quiz}
          onNavigate={onQuizNavigate}
          onAnswerSubmit={onQuizAnswerSubmit}
        />
      ) : response.mode === "stop" ? (
        <div className="bg-gray-50 border-2 border-gray-300 rounded-xl p-6 flex gap-4">
          <CheckCircle className="w-6 h-6 text-gray-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-gray-900 text-lg mb-2">
              Lesson Paused
            </h3>
            <p className="text-gray-700 text-base">{response.answer_text}</p>
          </div>
        </div>
      ) : response.mode === "followup" ? (
        <div className="bg-blue-50 border-2 border-blue-300 rounded-xl p-6">
          <h3 className="font-semibold text-blue-900 text-lg mb-2">
            Repeating...
          </h3>
          <AnswerBubble
            answer_text={response.answer_text}
            title={response.title}
            bullets={response.bullets}
            example={response.example}
            recap={response.recap}
            avatar_state={response.avatar_state}
            audio_base64={response.audio_base64}
          />
        </div>
      ) : (
        // Explain or other modes
        <AnswerBubble
          answer_text={response.answer_text}
          title={response.title}
          bullets={response.bullets}
          example={response.example}
          recap={response.recap}
          avatar_state={response.avatar_state}
          audio_base64={response.audio_base64}
        />
      )}

      {/* Next Actions Panel */}
      {response.next_actions.length > 0 && (
        <NextActions
          next_actions={response.next_actions}
          onActionClick={onNextAction}
        />
      )}

      {/* Source References (if available) */}
      {response.source_refs && response.source_refs.length > 0 && (
        <div className="border-t-2 border-gray-200 pt-4">
          <p className="text-sm font-semibold text-gray-700 mb-3">
            Source References:
          </p>
          <div className="space-y-2">
            {response.source_refs.map((ref, idx) => (
              <div
                key={idx}
                className="bg-gray-50 p-3 rounded border border-gray-200"
              >
                <p className="font-medium text-gray-900">{ref.title}</p>
                <p className="text-sm text-gray-600 mt-1">{ref.snippet}</p>
                {ref.page_number && (
                  <p className="text-xs text-gray-500 mt-2">
                    Page {ref.page_number}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer - Transcript for Debugging */}
      {process.env.NODE_ENV === "development" && response.transcript_text && (
        <div className="border-t-2 border-gray-200 pt-4 text-xs text-gray-500 bg-gray-50 p-2 rounded">
          <p className="font-mono">
            <span className="font-semibold">Debug - Input:</span> {response.transcript_text}
          </p>
        </div>
      )}
    </div>
  );
}
