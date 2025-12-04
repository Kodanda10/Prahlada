import { useRef, useEffect } from 'react';
import { useThree } from '@react-three/fiber';
import gsap from 'gsap';
import EarthParticles from './EarthParticles';

interface SimpleMorphDemoProps {
    viewMode: 'globe' | 'flat';
}

export default function SimpleMorphDemo({ viewMode }: SimpleMorphDemoProps) {
    const { camera } = useThree();
    const uMorph = viewMode === 'flat' ? 1.0 : 0.0;

    // Camera animation when switching modes
    useEffect(() => {
        if (viewMode === 'globe') {
            // Globe view - pull back
            gsap.to(camera.position, {
                x: 0,
                y: 0,
                z: 22,
                duration: 2,
                ease: 'power2.inOut',
            });
        } else {
            // Flat map view - zoom in closer
            gsap.to(camera.position, {
                x: 0,
                y: 0,
                z: 12,
                duration: 2,
                ease: 'power2.inOut',
            });
        }
        camera.lookAt(0, 0, 0);
    }, [camera, viewMode]);

    return (
        <>
            {/* Lighting */}
            {/* Lighting for Indigo Cyberpunk Theme */}
            <ambientLight intensity={0.4} />
            <directionalLight position={[5, 5, 5]} intensity={2.0} color="#a5b4fc" /> {/* Light indigo tint */}
            <pointLight position={[-10, -10, -5]} intensity={1.5} color="#6366f1" /> {/* Primary Indigo */}
            <pointLight position={[10, 10, 5]} intensity={1.0} color="#c084fc" /> {/* Purple Accent */}

            {/* Particle visualization with morphing */}
            <EarthParticles uMorph={uMorph} />
        </>
    );
}
