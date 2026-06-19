/**
 * Interaction Rules for Shiksha Sahayak
 * "Buttons must look tappable."
 */

export const interactionRules = {
  touch: {
    minSize: "44px",
    gap: "1rem",
  },
  
  feedback: {
    hover: "scale(1.02)",
    active: "scale(0.98)",
    focus: "0 0 0 4px var(--color-primary-alpha-20)",
  },
  
  states: {
    disabled: {
      opacity: 0.4,
      cursor: "not-allowed",
      grayscale: "100%",
    },
    loading: {
      animation: "pulse 2s infinite ease-in-out",
    },
  },
  
  // Rule: Modals are lazy. Exhaust inline alternatives first.
  preferredPatterns: {
    confirmation: "inline-popover",
    selection: "segmented-control",
    settings: "side-panel",
  }
};
