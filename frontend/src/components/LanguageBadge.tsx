/**
 * LanguageBadge component.
 * Displays the language mode in a compact badge.
 */

import { LanguageMode } from "@/types/api";

interface LanguageBadgeProps {
  language_mode: LanguageMode;
}

const languageLabels: Record<LanguageMode, string> = {
  hinglish: "हिंग्लिश",
  english: "English",
  hindi: "हिंदी",
};

const languageColors: Record<LanguageMode, string> = {
  hinglish: "bg-blue-100 text-blue-800 border-blue-300",
  english: "bg-green-100 text-green-800 border-green-300",
  hindi: "bg-orange-100 text-orange-800 border-orange-300",
};

export function LanguageBadge({ language_mode }: LanguageBadgeProps) {
  return (
    <div
      className={`inline-block px-3 py-1 rounded-full text-sm font-medium border ${languageColors[language_mode]}`}
    >
      {languageLabels[language_mode]}
    </div>
  );
}
