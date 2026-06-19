import { useEffect } from 'react';
import { appEventBus } from './appEventBus';

type AppEvent = Parameters<typeof appEventBus.dispatch>[0];
type EventCallback = (event: AppEvent) => void;

export const useAppEvents = () => {
  const dispatch = (event: AppEvent) => {
    appEventBus.dispatch(event);
  };

  const subscribe = (callback: EventCallback) => {
    return appEventBus.subscribe(callback);
  };

  return { dispatch, subscribe };
};
