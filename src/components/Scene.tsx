import { useRef, useEffect } from 'react';
import { useThree } from '@react-three/fiber';
import * as THREE from 'three';
import gsap from 'gsap';
import EarthParticles from './EarthParticles';
import ChhattisgarhHierarchy from './ChhattisgarhHierarchy';
import BillboardLabels from './BillboardLabels';
import EventSpikes from './EventSpikes';
import type { HierarchyNode } from '../utils/hierarchyFilter';
import type { HierarchyLevel } from '../hooks/useHierarchyState';
import { getCameraPosition } from '../utils/cameraStates';

interface SceneProps {
    viewMode: 'globe' | 'flat';
    focusTarget: HierarchyNode | null;
    visibleNodes: HierarchyNode[];
    currentLevel: HierarchyLevel;
    onNodeClick: (node: HierarchyNode) => void;
}

export default function Scene({ viewMode, focusTarget, visibleNodes, currentLevel, onNodeClick }: SceneProps) {
    const { camera } = useThree();
    const uMorph = viewMode === 'flat' ? 1.0 : 0.0;
    const lightsRef = useRef<THREE.Group>(null);

    // Camera animation based on hierarchy level
    useEffect(() => {
        const targetCoords = focusTarget ? { lat: focusTarget.lat, lon: focusTarget.lon } : null;
        const cameraState = getCameraPosition(currentLevel, targetCoords);

        gsap.to(camera.position, {
            x: cameraState.position[0],
            y: cameraState.position[1],
            z: cameraState.position[2],
            duration: 1.5,
            ease: 'power2.inOut',
            onUpdate: () => {
                camera.lookAt(cameraState.target[0], cameraState.target[1], cameraState.target[2]);
            }
        });
    }, [camera, currentLevel, focusTarget]);

    return (
        <>
            <group ref={lightsRef}>
                <ambientLight intensity={0.9} />
                <directionalLight position={[10, 10, 5]} intensity={2.0} />
                <pointLight position={[-10, -10, -5]} intensity={1.5} color="#00D4FF" />
                <pointLight position={[5, 5, 10]} intensity={1.2} color="#00FFFF" />
            </group>

            {/* Don't show entire Earth - just Chhattisgarh boundaries */}
            {/* <EarthParticles uMorph={uMorph} /> */}

            {/* Chhattisgarh boundary lines - THIS is the main visualization */}
            <ChhattisgarhHierarchy uMorph={uMorph} />

            {/* Billboard labels - showing district names in Hindi */}
            <BillboardLabels
                nodes={visibleNodes}
                uMorph={uMorph}
                onNodeClick={onNodeClick}
            />

            {/* Event spikes at district locations */}
            <EventSpikes
                nodes={visibleNodes}
                uMorph={uMorph}
            />
        </>
    );
}
