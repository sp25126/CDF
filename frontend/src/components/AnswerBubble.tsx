/**
 * AnswerBubble component.
 * Displays the main answer text with optional bullets and example.
 * Rendered directly from backend without modification.
 */

import { AvatarState } from "@/types/api";
import { Mic, Volume2 } from "lucide-react";

interface AnswerBubbleProps {
  answer_text?: string;
  title?: string;
  bullets?: string[];
  example?: string;
  recap?: string;
  avatar_state: AvatarState;
  audio_base64?: string;
}

const avatarStateLabels: Record<AvatarState, string> = {
  idle: "Ready",
  speaking: "Speaking",
  listening: "Listening",
  thinking: "Thinking",
};

const avatarStateColors: Record<AvatarState, string> = {
  idle: "bg-gray-100 text-gray-700",
  speaking: "bg-blue-100 text-blue-700 animate-pulse",
  listening: "bg-purple-100 text-purple-700",
  thinking: "bg-yellow-100 text-yellow-700",
};

export function AnswerBubble({
  answer_text,
  title,
  bullets,
  example,
  recap,
  avatar_state,
  audio_base64,
}: AnswerBubbleProps) {
  if (!answer_text) {
    return null;
  }

  const handlePlayAudio = () => {
    if (audio_base64) {
      const audio = new Audio(audio_base64);
      audio.play();
    }
  };

  return (
    <div className="space-y-4">
      {/* Avatar State */}
      <div className="flex items-center gap-2">
        <div
          className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${avatarStateColors[avatar_state]}`}
        >
          {avatar_state === "listening" && (
            <Mic className="w-4 h-4" />
          )}
          {avatar_state === "speaking" && (
            <Volume2 className="w-4 h-4" />
          )}
          <span>{avatarStateLabels[avatar_state]}</span>
        </div>
      </div>

      {/* Title */}
      {title && (
        <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
      )}

      {/* Main Answer */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-6">
        <p className="text-lg leading-relaxed text-gray-800 whitespace-pre-wrap">
          {answer_text}
        </p>
      </div>

      {/* Audio Player (if available) */}
      {audio_base64 && (
        <button
          onClick={handlePlayAudio}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
        >
          <Volume2 className="w-5 h-5" />
          <span>Play Audio</span>
        </button>
      )}

      {/* Bullets (Smart Board Display) */}
      {bullets && bullets.length > 0 && (
        <div className="bg-white border-l-4 border-indigo-500 pl-6 py-4">
          <ul className="space-y-2">
            {bullets.map((bullet, idx) => (
              <li key={idx} className="text-base text-gray-700 flex items-start">
                <span className="text-indigo-500 font-bold mr-3">•</span>
                <span>{bullet}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Example */}
      {example && (
        <div className="bg-green-50 border-l-4 border-green-500 pl-6 py-4">
          <p className="text-sm font-semibold text-green-700 mb-2">
            Example:
          </p>
          <p className="text-base text-green-900">{example}</p>
        </div>
      )}

      {/* Recap */}
      {recap && (
        <div className="bg-purple-50 border-l-4 border-purple-500 pl-6 py-4">
          <p className="text-sm font-semibold text-purple-700 mb-2">
            Recap:
          </p>
          <p className="text-base text-purple-900">{recap}</p>
        </div>
      )}
    </div>
  );
}
