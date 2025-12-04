import { useRef, useMemo, useLayoutEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import spikesVert from '../shaders/spikesVert.glsl.ts';
import spikesFrag from '../shaders/spikesFrag.glsl.ts';
import { latLonToSphere, latLonToFlat } from '../utils/globeMath';

interface DhruvSignalsProps {
    uMorph: number;
}

export default function DhruvSignals({ uMorph }: DhruvSignalsProps) {
    const meshRef = useRef<THREE.InstancedMesh>(null);
    const count = 60; // Reduced count for cleaner look like reference

    const shaderMaterial = useMemo(() => {
        return new THREE.ShaderMaterial({
            vertexShader: spikesVert,
            fragmentShader: spikesFrag,
            uniforms: {
                uTime: { value: 0 },
                uMorph: { value: 0 }
            },
            transparent: true,
            side: THREE.DoubleSide,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });
    }, []);

    const { signals, sphereMatrices, flatMatrices, colors } = useMemo(() => {
        const tempSignals = [];
        const sphereMats = new Float32Array(count * 16);
        const flatMats = new Float32Array(count * 16);
        const cols = new Float32Array(count * 3);

        const dummy = new THREE.Object3D();

        for (let i = 0; i < count; i++) {
            // Random lat/lon in Chhattisgarh bounds
            const lat = 17.8 + Math.random() * (24.1 - 17.8);
            const lon = 80.2 + Math.random() * (84.4 - 80.2);

            // Type: 0=Sentiment(Green), 1=Event(Red), 2=Anomaly(Orange)
            const type = Math.random() > 0.8 ? 1 : (Math.random() > 0.5 ? 2 : 0);
            let color = new THREE.Color('#00FF9D'); // Sentiment (Green)
            if (type === 1) color = new THREE.Color('#FF0055'); // Event (Red)
            if (type === 2) color = new THREE.Color('#FFaa00'); // Anomaly (Orange)

            color.toArray(cols, i * 3);

            // Sphere Transform
            const [sx, sy, sz] = latLonToSphere(lat, lon, 5);
            dummy.position.set(sx, sy, sz);
            dummy.lookAt(0, 0, 0); // Point to center
            dummy.rotateX(-Math.PI / 2); // Rotate so cone points OUT (Y-axis aligns with normal)
            dummy.updateMatrix();
            sphereMats.set(dummy.matrix.elements, i * 16);

            // Flat Transform
            const [fx, fy] = latLonToFlat(lat, lon);
            dummy.position.set(fx, fy, 0);
            dummy.rotation.set(0, 0, 0); // Reset rotation
            dummy.rotateX(Math.PI / 2); // Point UP (Z-axis is up in 2D view? No, Y is up in 3D flat view usually)
            // Wait, flat view is X-Y plane. Z is up.
            // Cone points Y+. So we need to rotate X by 90 deg to point Z+.
            dummy.updateMatrix();
            flatMats.set(dummy.matrix.elements, i * 16);

            tempSignals.push({ lat, lon, color });
        }
        return { signals: tempSignals, sphereMatrices: sphereMats, flatMatrices: flatMats, colors: cols };
    }, []);

    useLayoutEffect(() => {
        if (meshRef.current) {
            meshRef.current.geometry.setAttribute('aMatrixSphere', new THREE.InstancedBufferAttribute(sphereMatrices, 16));
            meshRef.current.geometry.setAttribute('aMatrixFlat', new THREE.InstancedBufferAttribute(flatMatrices, 16));
            meshRef.current.geometry.setAttribute('instanceColor', new THREE.InstancedBufferAttribute(colors, 3));
        }
    }, [sphereMatrices, flatMatrices, colors]);

    useFrame(({ clock }) => {
        if (meshRef.current) {
            const material = meshRef.current.material as THREE.ShaderMaterial;
            material.uniforms.uTime.value = clock.getElapsedTime();
            material.uniforms.uMorph.value = uMorph;
        }
    });

    return (
        <instancedMesh ref={meshRef} args={[undefined, undefined, count]}>
            <coneGeometry args={[0.05, 1.5, 8]} />
            <primitive object={shaderMaterial} attach="material" />
        </instancedMesh>
    );
}
