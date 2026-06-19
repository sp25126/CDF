export type AvatarState = 'idle' | 'listening' | 'processing' | 'speaking' | 'quiz_active' | 'source_mode' | 'waving' | 'error';

export const avatarStateMap: Record<string, AvatarState> = {
  // App states
  MIC_OPEN: 'listening',
  MIC_CLOSE: 'idle',
  COMMAND_SUBMITTED: 'processing',
  RESPONSE_RECEIVED: 'speaking',
  TTS_START: 'speaking',
  TTS_END: 'idle',
  QUIZ_ACTIVATED: 'quiz_active',
  SOURCE_MODE_ACTIVATED: 'source_mode',
  ERROR: 'error',
  CLEAR_SESSION: 'waving',

  // Default
  idle: 'idle',
};
