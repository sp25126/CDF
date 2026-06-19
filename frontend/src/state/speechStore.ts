import { create } from "zustand";

interface SpeechState {
  currentWordIndex: number;
  isPlaying: boolean;
  spokenText: string;
  setWordIndex: (index: number) => void;
  setPlaying: (playing: boolean) => void;
  setSpokenText: (text: string) => void;
  reset: () => void;
}

export const useSpeechStore = create<SpeechState>((set) => ({
  currentWordIndex: -1,
  isPlaying: false,
  spokenText: "",

  setWordIndex: (index) => set({ currentWordIndex: index }),
  setPlaying: (playing) => set({ isPlaying: playing }),
  setSpokenText: (text) => set({ spokenText: text }),
  reset: () => set({ currentWordIndex: -1, isPlaying: false, spokenText: "" }),
}));
