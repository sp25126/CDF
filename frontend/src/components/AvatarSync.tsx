"use client";

import React from "react";
import dynamic from "next/dynamic";

type AvatarState = "idle" | "listening" | "speaking" | "thinking" | "waving";

interface AvatarSyncProps {
  state: AvatarState;
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

export function AvatarSync({ state }: AvatarSyncProps) {
  return (
    <div className="flex flex-col items-center justify-center p-4">
      {/* 3D Model Outer Glow Ring */}
      <div className="relative w-56 h-56 rounded-full bg-slate-950 border-4 border-white shadow-2xl flex items-center justify-center overflow-hidden mb-4">
        {/* Futuristic glowing backdrop */}
        <div className="absolute inset-0 bg-gradient-to-tr from-indigo-950 via-slate-900 to-slate-950 opacity-95"></div>
        
        {/* Pulsing indicator ring */}
        <div
          className={`absolute inset-0 border-2 rounded-full transition-all duration-1000 ${
            state === "listening"
              ? "border-amber-400 animate-ping opacity-60"
              : state === "speaking"
              ? "border-blue-500 animate-pulse opacity-60"
              : state === "thinking"
              ? "border-purple-500 animate-pulse opacity-40"
              : "border-slate-800 opacity-20"
          }`}
          style={{ animationDuration: state === "listening" ? "2s" : "3.5s" }}
        ></div>

        {/* 3D WebGL Canvas */}
        <div className="absolute inset-0 z-10 w-full h-full">
          <AvatarCanvas state={state} />
        </div>
      </div>
      
      {/* Visual State Indicators */}
      <div className="text-center z-20">
        <h3 className="font-bold text-lg text-slate-800">JULI-E</h3>
        <span
          className={`text-xs font-bold uppercase tracking-widest px-3 py-1 rounded-full inline-block shadow-sm ${
            state === "listening"
              ? "bg-amber-100 text-amber-800 border border-amber-200 animate-pulse"
              : state === "speaking"
              ? "bg-blue-100 text-blue-800 border border-blue-200"
              : state === "thinking"
              ? "bg-purple-100 text-purple-800 border border-purple-200"
              : "bg-slate-100 text-slate-600 border border-slate-200"
          }`}
        >
          {state}
        </span>
      </div>
    </div>
  );
}
