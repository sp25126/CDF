import { tokens } from "./tokens";

/**
 * Theme configuration for Shiksha Sahayak.
 * Provides easy access to tokens and theme-specific logic.
 */

export const theme = {
  ...tokens,
  
  // High-level intent-based themes
  teaching: {
    background: tokens.colors.canvas.bg,
    surface: tokens.colors.canvas.surface,
    text: tokens.colors.canvas.ink,
    textMuted: tokens.colors.canvas.muted,
    border: tokens.colors.canvas.border,
  },
  
  console: {
    background: tokens.colors.console.bg,
    surface: tokens.colors.console.surface,
    text: tokens.colors.console.ink,
    textMuted: tokens.colors.console.muted,
    border: tokens.colors.console.border,
  },
  
  // CSS Variable mapping (for integration with global.css or tailwind)
  cssVariables: {
    "--color-primary": tokens.colors.primary,
    "--color-canvas-bg": tokens.colors.canvas.bg,
    "--color-canvas-ink": tokens.colors.canvas.ink,
    "--color-console-bg": tokens.colors.console.bg,
    "--color-console-ink": tokens.colors.console.ink,
    "--font-base": tokens.typography.fontSize.base,
    "--radius-card": tokens.radius.md,
  },
};
