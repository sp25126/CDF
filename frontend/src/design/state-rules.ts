/**
 * State Rules for Shiksha Sahayak
 * Defines behavior and visibility transitions between modes.
 */

export type AppMode = "normal" | "explain" | "quiz" | "source" | "hands-free";

interface ModeState {
  showTranscript: boolean;
  showMediaRail: boolean;
  showConsole: boolean;
  primaryZone: "avatar" | "canvas" | "quiz";
  avatarPosition: "center" | "side";
}

export const modeRules: Record<AppMode, ModeState> = {
  normal: {
    showTranscript: true,
    showMediaRail: false,
    showConsole: true,
    primaryZone: "avatar",
    avatarPosition: "center",
  },
  explain: {
    showTranscript: true,
    showMediaRail: true,
    showConsole: true,
    primaryZone: "canvas",
    avatarPosition: "side",
  },
  quiz: {
    showTranscript: false,
    showMediaRail: false,
    showConsole: true,
    primaryZone: "quiz",
    avatarPosition: "side",
  },
  source: {
    showTranscript: true,
    showMediaRail: true,
    showConsole: true,
    primaryZone: "canvas",
    avatarPosition: "side",
  },
  "hands-free": {
    showTranscript: true,
    showMediaRail: true,
    showConsole: false, // Console is secondary in hands-free
    primaryZone: "canvas",
    avatarPosition: "side",
  },
};
