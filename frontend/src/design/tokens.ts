/**
 * Design Tokens for Shiksha Sahayak
 * Optimized for classroom smartboards and teacher consoles.
 * Uses OKLCH for perceptually uniform colors.
 */

export const tokens = {
  colors: {
    // Brand - Indigo based, calm and professional
    primary: "oklch(0.55 0.18 260)", // Indigo-600 equivalent
    primaryHover: "oklch(0.45 0.18 260)",
    primaryActive: "oklch(0.35 0.18 260)",
    
    // Teaching Canvas (Student-facing)
    canvas: {
      bg: "oklch(0.98 0.005 260)", // Very light tinted neutral
      surface: "oklch(1 0 0)", // White
      ink: "oklch(0.2 0.02 260)", // Deep slate/ink
      muted: "oklch(0.6 0.02 260)",
      border: "oklch(0.9 0.01 260)",
    },
    
    // Teacher Console (Control area)
    console: {
      bg: "oklch(0.25 0.03 260)", // Dark navy/slate
      surface: "oklch(0.3 0.03 260)",
      ink: "oklch(0.95 0.01 260)", // Near white text
      muted: "oklch(0.7 0.02 260)",
      border: "oklch(0.35 0.03 260)",
    },
    
    // Semantic
    success: "oklch(0.65 0.15 150)",
    error: "oklch(0.6 0.18 25)",
    warning: "oklch(0.8 0.15 85)",
    info: "oklch(0.7 0.1 220)",
  },
  
  // Typography - Large scales for smartboard readability
  typography: {
    fontFamily: {
      display: '"Inter", system-ui, sans-serif',
      body: '"Inter", system-ui, sans-serif',
    },
    fontSize: {
      xs: "0.875rem",  // 14px
      sm: "1rem",      // 16px
      base: "1.25rem", // 20px - Base for classroom viewing
      lg: "1.5rem",    // 24px
      xl: "2rem",      // 32px
      "2xl": "2.5rem", // 40px
      "3xl": "3.5rem", // 56px
      "4xl": "4.5rem", // 72px
    },
    fontWeight: {
      normal: "400",
      medium: "500",
      semibold: "600",
      bold: "700",
    },
    lineHeight: {
      tight: "1.1",
      snug: "1.3",
      normal: "1.5",
      relaxed: "1.75",
    },
  },
  
  // Spacing - Generous for touch and distance
  spacing: {
    0: "0",
    1: "0.25rem",
    2: "0.5rem",
    3: "0.75rem",
    4: "1rem",
    6: "1.5rem",
    8: "2rem",
    12: "3rem",
    16: "4rem",
    24: "6rem",
  },
  
  // Shapes
  radius: {
    none: "0",
    sm: "0.375rem",
    md: "0.75rem",   // Default for classroom-grade cards
    lg: "1.25rem",
    full: "9999px",
  },
  
  // Elevation
  shadows: {
    none: "none",
    sm: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
    md: "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
    lg: "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
  },
  
  // Layers
  zIndex: {
    base: 0,
    dropdown: 10,
    sticky: 20,
    overlay: 30,
    modal: 40,
    popover: 50,
    toast: 60,
  },
};
