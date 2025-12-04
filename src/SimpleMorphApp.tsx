import { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import SimpleMorphDemo from './components/SimpleMorphDemo';
import '../index.css';

export default function App() {
    const [viewMode, setViewMode] = useState<'globe' | 'flat'>('globe');

    return (
        <div className="w-screen h-screen bg-black">
            <Canvas camera={{ position: [0, 0, 22], fov: 45 }}>
                <SimpleMorphDemo viewMode={viewMode} />
            </Canvas>

            {/* Simple control button */}
            <div className="absolute bottom-6 left-1/2 -translate-x-1/2 pointer-events-auto">
                <button
                    onClick={() => setViewMode(viewMode === 'globe' ? 'flat' : 'globe')}
                    className="px-6 py-3 bg-cyan-500/20 border border-cyan-400 text-white rounded-lg
                             hover:bg-cyan-500/40 transition-all"
                >
                    {viewMode === 'globe' ? 'Morph to Flat Map' : 'Morph to Globe'}
                </button>
            </div>
        </div>
    );
}
