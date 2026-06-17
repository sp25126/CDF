/**
 * Example page demonstrating ResponseRenderer usage.
 * This is a demo/test page for Phase 1 frontend.
 */

"use client";

import { useState } from "react";
import { ResponseRenderer } from "@/components";
import { AssistantResponse } from "@/types/api";
import { Send, Loader2 } from "lucide-react";

export default function DemoPage() {
  const [response, setResponse] = useState<AssistantResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [sessionId] = useState(`demo_${Date.now()}`);

  const API_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleSubmit = async (text: string) => {
    if (!text.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/api/v1/command/text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          text: text.trim(),
        }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }

      const data = await res.json();
      if (data.status === "success" && data.data) {
        setResponse(data.data);
        setInput("");
      } else {
        throw new Error("Invalid response format");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const handleQuizNavigate = (index: number) => {
    if (!response?.quiz) return;
    const updatedQuiz = { ...response.quiz, current_index: index };
    setResponse({ ...response, quiz: updatedQuiz });
  };

  const handleQuizSubmit = (questionIndex: number, selectedIndex: number) => {
    console.log(`Quiz: Q${questionIndex} answered with option ${selectedIndex}`);
  };

  const handleNextAction = (action: string) => {
    handleSubmit(action);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            CDF Classroom Assistant - Phase 1 Demo
          </h1>
          <p className="text-gray-600 text-sm mt-1">
            Test the backend response rendering
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 py-8 space-y-8">
        {/* Input Area */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Send a Command
          </h2>

          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !loading) {
                  handleSubmit(input);
                }
              }}
              placeholder="e.g., 'Explain photosynthesis' or 'Quiz me on fractions'"
              className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500 transition-colors"
              disabled={loading}
            />
            <button
              onClick={() => handleSubmit(input)}
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors flex items-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Loading...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Send</span>
                </>
              )}
            </button>
          </div>

          {/* Quick Commands */}
          <div className="mt-4 space-y-2">
            <p className="text-sm font-medium text-gray-700">
              Quick test commands:
            </p>
            <div className="flex flex-wrap gap-2">
              {[
                "Explain photosynthesis",
                "Quiz on fractions",
                "Explain in English",
                "Explain in Hindi",
                "Stop",
              ].map((cmd) => (
                <button
                  key={cmd}
                  onClick={() => handleSubmit(cmd)}
                  disabled={loading}
                  className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 disabled:opacity-50 text-gray-700 rounded transition-colors"
                >
                  {cmd}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border-2 border-red-300 rounded-xl p-4">
            <p className="text-red-900 font-semibold">Error:</p>
            <p className="text-red-800 text-sm mt-1">{error}</p>
            <p className="text-red-700 text-xs mt-2">
              Make sure the backend is running at {API_URL}
            </p>
          </div>
        )}

        {/* Response Display */}
        {response && (
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Response</h2>
              <code className="text-xs bg-gray-100 px-2 py-1 rounded text-gray-600">
                Session: {sessionId.substring(0, 12)}...
              </code>
            </div>

            {/* Response Details */}
            <ResponseRenderer
              response={response}
              onNextAction={handleNextAction}
              onQuizNavigate={handleQuizNavigate}
              onQuizAnswerSubmit={handleQuizSubmit}
            />
          </div>
        )}

        {/* Debug Panel */}
        {process.env.NODE_ENV === "development" && response && (
          <details className="bg-white rounded-xl shadow p-6">
            <summary className="cursor-pointer text-sm font-semibold text-gray-700 hover:text-gray-900">
              📋 Raw Response (Development)
            </summary>
            <pre className="mt-4 bg-gray-100 p-4 rounded text-xs overflow-auto max-h-96 text-gray-800">
              {JSON.stringify(response, null, 2)}
            </pre>
          </details>
        )}

        {/* Info Panel */}
        {!response && (
          <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-6 space-y-4">
            <h3 className="font-semibold text-blue-900">Getting Started</h3>
            <ol className="list-decimal list-inside space-y-2 text-blue-900 text-sm">
              <li>
                Start the backend: <code className="bg-white px-2 py-1 rounded">cd backend && python -m app.main</code>
              </li>
              <li>Try one of the quick commands above</li>
              <li>The response will render below</li>
              <li>Try different modes: explain, quiz, English, Hindi, etc.</li>
            </ol>
            <p className="text-blue-800 text-sm pt-2">
              📚 Learn more: See <code className="bg-white px-2 py-1 rounded">INTEGRATION.md</code> and <code className="bg-white px-2 py-1 rounded">backend/TESTING.md</code>
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white mt-12 py-4">
        <div className="max-w-5xl mx-auto px-4 text-center text-sm text-gray-600">
          <p>Phase 1 Frontend Demo - CDF Classroom Assistant</p>
        </div>
      </footer>
    </div>
  );
}
