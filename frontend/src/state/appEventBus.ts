type AppEvent = 
  | { type: 'COMMAND_SUBMITTED' }
  | { type: 'RESPONSE_RECEIVED', payload: any }
  | { type: 'MIC_OPEN' }
  | { type: 'MIC_CLOSE' }
  | { type: 'TTS_START' }
  | { type: 'TTS_END' }
  | { type: 'QUIZ_ACTIVATED' }
  | { type: 'SOURCE_MODE_ACTIVATED' }
  | { type: 'ERROR' }
  | { type: 'CLEAR_SESSION' };

type EventCallback = (event: AppEvent) => void;

class EventBus {
  private subscribers: EventCallback[] = [];

  subscribe(callback: EventCallback) {
    this.subscribers.push(callback);
    return () => {
      this.subscribers = this.subscribers.filter(cb => cb !== callback);
    };
  }

  dispatch(event: AppEvent) {
    this.subscribers.forEach(callback => callback(event));
  }
}

export const appEventBus = new EventBus();
