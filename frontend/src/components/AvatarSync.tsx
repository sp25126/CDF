"use client";

import React from "react";
import dynamic from "next/dynamic";
import { voiceStateLabel } from "../voice/voiceSessionState";
import type { VoiceSessionState } from "../voice/voiceSessionState";

// Extended avatar state type — covers all 6 voice states mapped to visual styles
type AvatarState = "idle" | "listening" | "speaking" | "thinking" | "waving";

interface AvatarSyncProps {
  state: AvatarState;
  /** Optional voice session state for richer status label */
  voiceState?: VoiceSessionState;
}

// Dynamically import the 3D Canvas component to bypass SSR errors
const AvatarCanvas = dynamic(
  () => import("./AvatarCanvas").then((mod) => mod.AvatarCanvas),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full flex flex-col items-center justify-center bg-slate-900 text-slate-400">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-2"></div>
        <span className="text-xs font-semibold animate-pulse">Loading 3D Avatar...</span>
      </div>
    ),
  }
);

// ─── Ring style per avatar state ──────────────────────────────────────────────

function ringClass(state: AvatarState): string {
  switch (state) {
    case "listening":
      return "border-amber-400 animate-ping opacity-60";
    case "speaking":
      return "border-blue-500 animate-pulse opacity-60";
    case "thinking":
      return "border-purple-500 animate-pulse opacity-40";
    default:
      return "border-slate-800 opacity-20";
  }
}

function ringDuration(state: AvatarState): string {
  return state === "listening" ? "2s" : "3.5s";
}

// ─── Badge style per avatar state ─────────────────────────────────────────────

function badgeClass(state: AvatarState): string {
  switch (state) {
    case "listening":
      return "bg-amber-100 text-amber-800 border border-amber-200 animate-pulse";
    case "speaking":
      return "bg-blue-100 text-blue-800 border border-blue-200";
    case "thinking":
      return "bg-purple-100 text-purple-800 border border-purple-200";
    default:
      return "bg-slate-100 text-slate-600 border border-slate-200";
  }
}

// ─── Label logic ──────────────────────────────────────────────────────────────

function statusLabel(state: AvatarState, voiceState?: VoiceSessionState): string {
  if (voiceState) return voiceStateLabel(voiceState);
  // Fallback if voiceState isn't provided
  switch (state) {
    case "listening": return "Listening…";
    case "speaking":  return "Speaking";
    case "thinking":  return "Thinking…";
    case "waving":    return "Hello!";
    default:          return "Idle";
  }
}

// ─── Component ────────────────────────────────────────────────────────────────

export function AvatarSync({ state, voiceState }: AvatarSyncProps) {
  return (
    <div className="flex flex-col items-center justify-center p-4">
      {/* 3D Model Outer Glow Ring */}
      <div className="relative w-56 h-56 rounded-full bg-slate-950 border-4 border-white shadow-2xl flex items-center justify-center overflow-hidden mb-4">
        {/* Futuristic glowing backdrop */}
        <div className="absolute inset-0 bg-gradient-to-tr from-indigo-950 via-slate-900 to-slate-950 opacity-95"></div>

        {/* Pulsing indicator ring */}
        <div
          className={`absolute inset-0 border-2 rounded-full transition-all duration-1000 ${ringClass(state)}`}
          style={{ animationDuration: ringDuration(state) }}
        ></div>

        {/* 3D WebGL Canvas */}
        <div className="absolute inset-0 z-10 w-full h-full">
          <AvatarCanvas state={state} />
        </div>
      </div>

      {/* Visual State Indicators */}
      <div className="text-center z-20">
        <h3 className="font-bold text-lg text-slate-800">JULI-E</h3>
        <span className={`text-xs font-bold uppercase tracking-widest px-3 py-1 rounded-full inline-block shadow-sm ${badgeClass(state)}`}>
          {statusLabel(state, voiceState)}
        </span>
      </div>
    </div>
  );
}
