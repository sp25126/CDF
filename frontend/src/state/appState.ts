export type AppStateName = 
  | 'idle'
  | 'listening'
  | 'processing'
  | 'explaining'
  | 'quiz_active'
  | 'source_mode'
  | 'hands_free_active'
  | 'error'
  | 'loading';

export type CanvasMode = 'idle' | 'explain' | 'quiz' | 'materials';
export type JuliAvatarState = 'idle' | 'listening' | 'speaking' | 'thinking' | 'quiz' | 'waving';

export interface AppState {
  name: AppStateName;
  canvasMode: CanvasMode;
  juliState: JuliAvatarState;
  consoleBehavior: {
    micActive: boolean;
    macros: string[];
  };
  topBar: {
    language: string;
    handsFree: boolean;
    sourceMode: boolean;
  };
  // New fields for real data
  payload?: any; // This will hold the response data
  error?: any;   // This will hold error information
}
