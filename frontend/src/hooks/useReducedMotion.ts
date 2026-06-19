import { useState, useEffect } from 'react';

const QUERY = '(prefers-reduced-motion: no-preference)';

export const useReducedMotion = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(true);

  useEffect(() => {
    const mediaQuery = window.matchMedia(QUERY);
    const listener = () => {
      setPrefersReducedMotion(!mediaQuery.matches);
    };
    listener();
    mediaQuery.addEventListener('change', listener);
    return () => {
      mediaQuery.removeEventListener('change', listener);
    };
  }, []);

  return prefersReducedMotion;
};
