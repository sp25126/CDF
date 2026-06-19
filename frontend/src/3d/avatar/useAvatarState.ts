import { useState, useEffect } from 'react';
import { useAppEvents } from '../../state/useAppEvents';
import { AvatarState, avatarStateMap } from './avatarStateMap';

export const useAvatarState = () => {
  const [avatarState, setAvatarState] = useState<AvatarState>('idle');
  const { subscribe } = useAppEvents();

  useEffect(() => {
    const unsubscribe = subscribe(event => {
      const nextState = avatarStateMap[event.type];
      if (nextState) {
        setAvatarState(nextState);
      }
    });

    return unsubscribe;
  }, [subscribe]);

  return avatarState;
};
