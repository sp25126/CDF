"use client";

import React from "react";
import dynamic from "next/dynamic";
import JuliEStateRing from "./JuliEStateRing";
import { theme } from "../design/theme";
import { useAvatarState } from "../3d/avatar/useAvatarState";

// AvatarCanvas uses WebGL / @react-three/fiber which must NOT run during SSR.
// Dynamic import with ssr:false guards against the server-side crash.
const AvatarCanvas = dynamic(
  () => import("./AvatarCanvas").then((mod) => mod.AvatarCanvas),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full flex items-center justify-center bg-slate-900">
        <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    ),
  }
);

/**
 * JuliEPanel — fixed avatar panel in the sidebar.
 * Listens to the app event bus via useAvatarState and drives JULI-E animations.
 * AvatarCanvas is dynamically imported (SSR-safe).
 */
export const JuliEPanel: React.FC<{ className?: string }> = ({ className = "" }) => {
  const avatarState = useAvatarState();

  // Map extended states to the ring's limited set
  const ringState = (
    ["listening", "speaking", "quiz", "idle"] as const
  ).includes(avatarState as any)
    ? (avatarState as "listening" | "speaking" | "quiz" | "idle")
    : "idle";

  return (
    <div
      className={`relative flex flex-col items-center justify-center ${className}`}
    >
      <div className="relative w-48 h-48">
        {/* Coloured ring indicating current state */}
        <JuliEStateRing state={ringState} />

        {/* 3D WebGL avatar — SSR-safe */}
        <div className="w-full h-full rounded-full bg-slate-900 overflow-hidden">
          <AvatarCanvas state={avatarState} />
        </div>
      </div>

      {/* State label */}
      <p
        className="mt-4 text-xs font-bold uppercase tracking-widest"
        style={{ color: theme.colors.canvas.muted }}
      >
        {avatarState.replace(/_/g, " ")}
      </p>
    </div>
  );
};

export default JuliEPanel;
