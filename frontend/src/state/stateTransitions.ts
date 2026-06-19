import { AppStateName } from './appState';

type Event = 
  | { type: 'COMMAND_SUBMITTED' }
  | { type: 'RESPONSE_RECEIVED'; mode: 'explain' | 'quiz' | 'other' }
  | { type: 'LISTENING_STARTED' }
  | { type: 'PROCESSING_STARTED' }
  | { type: 'HANDS_FREE_TOGGLED'; enabled: boolean }
  | { type: 'SOURCE_MODE_TOGGLED'; enabled: boolean }
  | { type: 'ERROR_OCCURRED' }
  | { type: 'CLEAR_SESSION' };

export const transition = (currentState: AppStateName, event: Event): AppStateName => {
  switch (currentState) {
    case 'idle':
      if (event.type === 'COMMAND_SUBMITTED') return 'processing';
      if (event.type === 'LISTENING_STARTED') return 'listening';
      if (event.type === 'HANDS_FREE_TOGGLED' && event.enabled) return 'hands_free_active';
      if (event.type === 'SOURCE_MODE_TOGGLED' && event.enabled) return 'source_mode';
      break;
    
    case 'listening':
      if (event.type === 'COMMAND_SUBMITTED') return 'processing';
      break;
      
    case 'processing':
      if (event.type === 'RESPONSE_RECEIVED') {
        if (event.mode === 'explain') return 'explaining';
        if (event.mode === 'quiz') return 'quiz_active';
        return 'idle';
      }
      if (event.type === 'ERROR_OCCURRED') return 'error';
      break;

    case 'explaining':
    case 'quiz_active':
    case 'error':
      if (event.type === 'COMMAND_SUBMITTED') return 'processing';
      if (event.type === 'CLEAR_SESSION') return 'idle';
      if (event.type === 'LISTENING_STARTED') return 'listening';
      break;
      
    case 'hands_free_active':
      if (event.type === 'HANDS_FREE_TOGGLED' && !event.enabled) return 'idle';
      // Other transitions will be handled within the hands-free loop
      break;
      
    case 'source_mode':
        if (event.type === 'SOURCE_MODE_TOGGLED' && !event.enabled) return 'idle';
        if (event.type === 'COMMAND_SUBMITTED') return 'processing';
        break;
  }
  return currentState;
};
