import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AvatarSync } from '../src/components/AvatarSync';

jest.mock('../src/3d/avatar/JuliEAvatar', () => {
    return {
        JuliEAvatar: () => <div data-testid="julie-avatar-mock">Avatar</div>
    };
});

describe('Avatar Visibility Tests', () => {
    test('JULI-E avatar renders unconditionally on mount', () => {
        render(<AvatarSync avatarState="idle" isVisible={true} />);
        
        // Ensure the Avatar container is in the DOM
        const avatarContainer = screen.getByTestId('julie-avatar-mock');
        expect(avatarContainer).toBeInTheDocument();
    });

    test('Avatar state changes correctly without unmounting', () => {
        const { rerender } = render(<AvatarSync avatarState="idle" isVisible={true} />);
        expect(screen.getByTestId('julie-avatar-mock')).toBeInTheDocument();

        // Simulate switching to explain mode
        rerender(<AvatarSync avatarState="speaking" isVisible={true} />);
        expect(screen.getByTestId('julie-avatar-mock')).toBeInTheDocument();

        // Simulate hands-free mode changing listening behavior
        rerender(<AvatarSync avatarState="listening" isVisible={true} />);
        expect(screen.getByTestId('julie-avatar-mock')).toBeInTheDocument();
    });
});
