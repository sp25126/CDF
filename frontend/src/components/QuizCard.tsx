/**
 * QuizCard component.
 * Displays one question at a time in an interactive card format.
 * One-question-at-a-time friendly for smart board and voice navigation.
 */

import { QuizPayload } from "@/types/api";
import { useState } from "react";
import { ChevronLeft, ChevronRight, CheckCircle, XCircle } from "lucide-react";

interface QuizCardProps {
  quiz: QuizPayload;
  onAnswerSubmit?: (questionIndex: number, selectedIndex: number) => void;
  onNavigate?: (newIndex: number) => void;
}

export function QuizCard({
  quiz,
  onAnswerSubmit,
  onNavigate,
}: QuizCardProps) {
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);

  const currentQuestion = quiz.questions[quiz.current_index];
  if (!currentQuestion) {
    return null;
  }

  const isCorrect = selectedAnswer === currentQuestion.correct_index;

  const handleSubmitAnswer = () => {
    if (selectedAnswer !== null) {
      setShowExplanation(true);
      onAnswerSubmit?.(quiz.current_index, selectedAnswer);
    }
  };

  const handleNextQuestion = () => {
    if (quiz.current_index < quiz.questions.length - 1) {
      setSelectedAnswer(null);
      setShowExplanation(false);
      onNavigate?.(quiz.current_index + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (quiz.current_index > 0) {
      setSelectedAnswer(null);
      setShowExplanation(false);
      onNavigate?.(quiz.current_index - 1);
    }
  };

  return (
    <div className="space-y-6">
      {/* Quiz Header */}
      <div className="space-y-2">
        <h2 className="text-2xl font-bold text-gray-900">{quiz.title}</h2>
        <p className="text-lg text-gray-600">Topic: {quiz.topic}</p>
        <div className="flex items-center justify-between">
          <p className="text-sm font-semibold text-indigo-600">
            Question {quiz.current_index + 1} of {quiz.total_questions}
          </p>
          <div className="w-48 bg-gray-200 rounded-full h-2">
            <div
              className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
              style={{
                width: `${((quiz.current_index + 1) / quiz.total_questions) * 100}%`,
              }}
            />
          </div>
        </div>
      </div>

      {/* Question Card */}
      <div className="bg-white border-2 border-indigo-300 rounded-xl p-8 space-y-6">
        {/* Question Text */}
        <div className="text-xl font-semibold text-gray-900">
          {currentQuestion.question}
        </div>

        {/* Options */}
        <div className="space-y-3">
          {currentQuestion.options.map((option, idx) => {
            const isSelected = selectedAnswer === idx;
            const isCorrectOption = idx === currentQuestion.correct_index;
            const shouldHighlightCorrect = showExplanation && isCorrectOption;
            const shouldHighlightIncorrect =
              showExplanation && isSelected && !isCorrect;

            let buttonClass =
              "w-full text-left p-4 rounded-lg border-2 transition-all duration-200 ";

            if (showExplanation) {
              if (shouldHighlightCorrect) {
                buttonClass +=
                  "border-green-500 bg-green-50 text-green-900 cursor-default";
              } else if (shouldHighlightIncorrect) {
                buttonClass +=
                  "border-red-500 bg-red-50 text-red-900 cursor-default";
              } else {
                buttonClass +=
                  "border-gray-300 bg-gray-100 text-gray-600 cursor-default opacity-50";
              }
            } else {
              buttonClass +=
                isSelected
                  ? "border-indigo-500 bg-indigo-100 text-indigo-900 cursor-pointer"
                  : "border-gray-300 bg-white text-gray-900 cursor-pointer hover:border-indigo-300 hover:bg-indigo-50";
            }

            return (
              <button
                key={idx}
                onClick={() => {
                  if (!showExplanation) {
                    setSelectedAnswer(idx);
                  }
                }}
                disabled={showExplanation}
                className={buttonClass}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{option}</span>
                  {showExplanation && shouldHighlightCorrect && (
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  )}
                  {showExplanation && shouldHighlightIncorrect && (
                    <XCircle className="w-6 h-6 text-red-600" />
                  )}
                </div>
              </button>
            );
          })}
        </div>

        {/* Explanation */}
        {showExplanation && (
          <div
            className={`p-4 rounded-lg border-l-4 ${
              isCorrect
                ? "bg-green-50 border-green-500 text-green-900"
                : "bg-blue-50 border-blue-500 text-blue-900"
            }`}
          >
            <p className="font-semibold mb-2">
              {isCorrect ? "Correct! 🎉" : "Explanation:"}
            </p>
            <p>{currentQuestion.explanation}</p>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between gap-4">
        {/* Previous Button */}
        <button
          onClick={handlePreviousQuestion}
          disabled={quiz.current_index === 0}
          className="flex items-center gap-2 px-4 py-2 bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed text-gray-800 rounded-lg transition-colors"
        >
          <ChevronLeft className="w-5 h-5" />
          <span>Previous</span>
        </button>

        {/* Submit/Next Button */}
        {!showExplanation ? (
          <button
            onClick={handleSubmitAnswer}
            disabled={selectedAnswer === null}
            className="flex-1 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors"
          >
            Submit Answer
          </button>
        ) : (
          <button
            onClick={handleNextQuestion}
            disabled={quiz.current_index === quiz.total_questions - 1}
            className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors"
          >
            {quiz.current_index === quiz.total_questions - 1
              ? "Quiz Complete ✓"
              : "Next Question"}
          </button>
        )}

        {/* Next Button */}
        <button
          onClick={handleNextQuestion}
          disabled={quiz.current_index === quiz.total_questions - 1}
          className="flex items-center gap-2 px-4 py-2 bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed text-gray-800 rounded-lg transition-colors"
        >
          <span>Next</span>
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      {/* Questions Summary */}
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="bg-indigo-50 p-4 rounded-lg">
          <p className="text-indigo-700 font-semibold">
            {quiz.total_questions} questions total
          </p>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <p className="text-purple-700 font-semibold">
            Navigable with voice commands
          </p>
        </div>
      </div>
    </div>
  );
}
