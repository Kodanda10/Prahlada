// import '@testing-library/jest-dom';
import { vi } from 'vitest';
import * as THREE from 'three';

// Mock TextureLoader to avoid Suspense
// Mock WebGL context
// Mock WebGL context with Proxy to handle all methods
HTMLCanvasElement.prototype.getContext = function (type: string) {
    if (type === 'webgl' || type === 'webgl2') {
        const noop = () => { };
        const context = {
            getExtension: () => ({}),
            getParameter: (p: number) => {
                if (p === 37445) return 'Unmasked Vendor';
                if (p === 37446) return 'Unmasked Renderer';
                if (p === 7938) return 'WebGL 2.0 (OpenGL ES 3.0 Chromium)';
                if (p === 35724) return 'WebGL GLSL ES 3.00 (OpenGL ES GLSL ES 3.0 Chromium)';
                if (p === 7936) return 'WebKit';
                if (p === 7937) return 'WebKit WebGL';
                return 0;
            },
            createTexture: () => ({}),
            createFramebuffer: () => ({}),
            createRenderbuffer: () => ({}),
            createShader: () => ({}),
            createProgram: () => ({}),
            createBuffer: () => ({}),
            checkFramebufferStatus: () => 36053,
            getShaderPrecisionFormat: () => ({
                rangeMin: 1,
                rangeMax: 1,
                precision: 1
            }),
            getShaderSource: () => '',
            getActiveUniform: () => ({ name: 'uTest', type: 35676, size: 1 }),
            getActiveAttrib: () => ({ name: 'aTest', type: 35676, size: 1 }),
            getUniformLocation: () => ({}),
            getAttribLocation: () => 0,
            getProgramParameter: (p: number) => {
                console.log('getProgramParameter', p);
                if (p === 35714) return 1; // LINK_STATUS
                return 0;
            },
            getShaderParameter: (p: number) => {
                if (p === 35713) return 1; // COMPILE_STATUS
                return 0;
            },
            canvas: this,
            VERSION: 7938,
            SHADING_LANGUAGE_VERSION: 35724,
            VENDOR: 7936,
            RENDERER: 7937,
        };

        return new Proxy(context, {
            get(target, prop) {
                if (prop in target) return (target as any)[prop];
                // Return no-op function for any other method
                return noop;
            }
        }) as any;
    }
    return null;
} as any;

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: (query: any) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: () => { }, // Deprecated
        removeListener: () => { }, // Deprecated
        addEventListener: () => { },
        removeEventListener: () => { },
        dispatchEvent: () => { },
    }),
});

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
    callback: any;
    constructor(callback: any) {
        this.callback = callback;
    }
    observe(target: any) {
        this.callback([{ target, contentRect: { width: 100, height: 100 } }]);
    }
    unobserve() { }
    disconnect() { }
};

// Mock layout
Object.defineProperties(HTMLElement.prototype, {
    offsetHeight: {
        get() { return 100 },
    },
    offsetWidth: {
        get() { return 100 },
    },
});

Element.prototype.getBoundingClientRect = () => ({
    width: 100,
    height: 100,
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
    x: 0,
    y: 0,
    toJSON: () => { }
}) as DOMRect;
