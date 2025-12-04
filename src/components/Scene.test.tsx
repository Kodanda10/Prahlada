import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import React from 'react';
import Scene from './Scene';

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
    observe() { }
    unobserve() { }
    disconnect() { }
};

describe('Scene', () => {
    it('renders without crashing and mounts a canvas', () => {
        // Scene needs to be inside a Canvas because it uses useThree/useFrame
        // So we should render App, or wrap Scene in Canvas.
        // The prompt says "If Scene is only used inside App, you can instead mount <App />".
        // But Scene.tsx exports a component that *uses* R3F hooks.
        // So `render(<Scene />)` will fail if not inside Canvas.
        // I will wrap it in Canvas for the test.

        const { Canvas } = require('@react-three/fiber');
        const { container } = render(
            <Canvas>
                <Scene viewMode="globe" focusTarget={null} setFocusTarget={() => { }} />
            </Canvas>
        );
        const canvas = container.querySelector('canvas');
        expect(canvas).not.toBeNull();
    });
});
