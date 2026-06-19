/**
 * Motion Tokens for Shiksha Sahayak
 * "Motion only when it adds meaning."
 */

export const motionTokens = {
  duration: {
    fast: 0.15,
    normal: 0.25,
    slow: 0.4,
  },
  easing: {
    standard: [0.4, 0, 0.2, 1],
    decelerate: [0, 0, 0.2, 1],
    accelerate: [0.4, 0, 1, 1],
  },
  transition: {
    default: {
      duration: 0.25,
      ease: [0.4, 0, 0.2, 1],
    },
    fast: {
        duration: 0.15,
        ease: [0.4, 0, 0.2, 1],
    }
  },
  variants: {
    page: {
        initial: { opacity: 0, y: 10 },
        animate: { opacity: 1, y: 0 },
        exit: { opacity: 0, y: -10 },
    },
    item: {
        initial: { opacity: 0, scale: 0.95, y: 10 },
        animate: { opacity: 1, scale: 1, y: 0 },
        exit: { opacity: 0, scale: 0.95, y: -10 },
    }
  }
};
