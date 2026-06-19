import { useEffect } from 'react';
import { create } from 'zustand';
import { AppState, AppStateName } from './appState';
import { uiModes } from './uiModes';
import { saveSession, loadSession } from './persistence';

interface AppStateStore {
  state: AppState;
  transitionTo: (newStateName: AppStateName, updates?: Partial<Omit<AppState, 'name'>>) => void;
  setPayload: (payload: any) => void;
  initialize: () => void;
}

let initialized = false;

export const useAppStateStore = create<AppStateStore>((set, get) => ({
  state: uiModes.idle,
  
  transitionTo: (newStateName, updates = {}) => {
    const newMode = uiModes[newStateName];
    set((store) => {
      const prevState = store.state;
      const nextState = {
        ...newMode,
        ...updates,
        payload: updates.payload || prevState.payload, 
        topBar: { ...newMode.topBar, ...prevState.topBar, ...updates.topBar },
        consoleBehavior: { ...newMode.consoleBehavior, ...prevState.consoleBehavior, ...updates.consoleBehavior },
      };
      saveSession(nextState);
      return { state: nextState };
    });
  },

  setPayload: (payload) => {
    set((store) => {
      const nextState = { ...store.state, payload };
      saveSession(nextState);
      return { state: nextState };
    });
  },

  initialize: () => {
    if (initialized) return;
    initialized = true;
    try {
      const saved = loadSession();
      if(saved) {
        const matchingModeName = Object.keys(uiModes).find(key => uiModes[key as AppStateName].canvasMode === saved.canvasMode);
        const mode = uiModes[matchingModeName as AppStateName || 'idle'];
        set((store) => {
          // If state has already diverged from idle, don't overwrite it entirely,
          // but we shouldn't really hit this due to `initialized` flag
          return {
            state: {
              ...store.state,
              ...mode,
              ...saved,
            }
          };
        });
      }
    } catch (e) {
      console.warn('Could not restore session:', e);
    }
  }
}));

export const useAppState = () => {
  const store = useAppStateStore();
  
  useEffect(() => {
    store.initialize();
  }, [store]);

  return {
    state: store.state,
    transitionTo: store.transitionTo,
    setPayload: store.setPayload,
  };
};
