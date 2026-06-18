// src/components/LoadingScreen.tsx
import React from "react";

/**
 * Full‑screen loading overlay shown while avatar assets are being preloaded.
 */
export function LoadingScreen() {
  return (
    <div className="fixed inset-0 flex flex-col items-center justify-center bg-black bg-opacity-80 z-50">
      <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-4" />
      <span className="text-white text-lg font-semibold">Loading avatar...</span>
    </div>
  );
}
