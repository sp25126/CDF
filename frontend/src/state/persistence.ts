const SESSION_KEY = 'classroom-assistant-session';

const isBrowser = typeof window !== 'undefined';

export const saveSession = (state: any) => {
  if (!isBrowser) return;
  try {
    const stateToSave = {
      canvasMode: state.canvasMode,
      topBar: state.topBar,
      payload: state.payload,
    };
    localStorage.setItem(SESSION_KEY, JSON.stringify(stateToSave));
  } catch (e) {
    console.error("Could not save session", e);
  }
};

export const loadSession = () => {
  if (!isBrowser) return undefined;
  try {
    const savedState = localStorage.getItem(SESSION_KEY);
    if (savedState === null) {
      return undefined;
    }
    return JSON.parse(savedState);
  } catch (e) {
    console.error("Could not load session", e);
    return undefined;
  }
};

export const clearSession = () => {
  if (!isBrowser) return;
  try {
    localStorage.removeItem(SESSION_KEY);
  } catch(e) {
    console.error("Could not clear session", e);
  }
}
