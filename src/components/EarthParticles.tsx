import { useRef, useMemo, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import particlesVert from '../shaders/particlesVert.glsl.ts';
import particlesFrag from '../shaders/particlesFrag.glsl.ts';
import { latLonToSphere, latLonToFlat } from '../utils/globeMath';

interface EarthParticlesProps {
    uMorph: number;
}

export default function EarthParticles({ uMorph }: EarthParticlesProps) {
    const pointsRef = useRef<THREE.Points>(null);

    // Shader Material
    const shaderMaterial = useMemo(() => {
        return new THREE.ShaderMaterial({
            vertexShader: particlesVert,
            fragmentShader: particlesFrag,
            uniforms: {
                uTime: { value: 0 },
                uMorph: { value: 0 },
                uSize: { value: 1.8 } // Smaller, sharper dots
            },
            transparent: true,
            depthWrite: false,
            blending: THREE.AdditiveBlending
        });
    }, []);

    // Geometry Generation
    const geometry = useMemo(() => {
        const geom = new THREE.BufferGeometry();
        // ... (rest of init code)
        return geom;
    }, []);

    // Load Image and Update Geometry
    useEffect(() => {
        const img = new Image();
        img.crossOrigin = "Anonymous";
        // Try a different reliable source or fallback to procedural
        img.src = "https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_specular_2048.jpg";

        const updateGeometry = (data: Uint8ClampedArray | null, width: number, height: number) => {
            const spherePositions: number[] = [];
            const flatPositions: number[] = [];

            // Density settings
            const step = 3; // Balance between density and performance
            const maxParticles = 60000;
            let particleCount = 0;

            for (let y = 0; y < height; y += step) {
                for (let x = 0; x < width; x += step) {
                    if (particleCount >= maxParticles) break;

                    let isLand = false;

                    if (data) {
                        // Use texture data
                        const i = (y * width + x) * 4;
                        if (data[i] > 50) isLand = true;
                    } else {
                        // Procedural fallback (simple bands/noise if image fails)
                        // This ensures we ALWAYS see something
                        const lat = 90 - (y / height) * 180;
                        const lon = (x / width) * 360 - 180;
                        // Simple procedural continents approximation
                        if (Math.abs(lat) < 60 && Math.sin(lon * 0.1) * Math.cos(lat * 0.1) > -0.2) {
                            isLand = true;
                        }
                    }

                    if (isLand) {
                        const lon = (x / width) * 360 - 180;
                        const lat = 90 - (y / height) * 180;

                        const [sx, sy, sz] = latLonToSphere(lat, lon, 5);
                        spherePositions.push(sx, sy, sz);

                        const [fx, fy] = latLonToFlat(lat, lon);
                        flatPositions.push(fx, fy, 0);

                        particleCount++;
                    }
                }
            }

            if (pointsRef.current) {
                const geom = pointsRef.current.geometry;
                geom.setAttribute('position', new THREE.Float32BufferAttribute(spherePositions, 3));
                geom.setAttribute('aPosSphere', new THREE.Float32BufferAttribute(spherePositions, 3));
                geom.setAttribute('aPosFlat', new THREE.Float32BufferAttribute(flatPositions, 3));
                geom.attributes.position.needsUpdate = true;
                geom.attributes.aPosSphere.needsUpdate = true;
                geom.attributes.aPosFlat.needsUpdate = true;
            }
        };

        img.onload = () => {
            const canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            const ctx = canvas.getContext('2d');
            if (ctx) {
                ctx.drawImage(img, 0, 0);
                const imageData = ctx.getImageData(0, 0, img.width, img.height);
                updateGeometry(imageData.data, img.width, img.height);
            }
        };

        img.onerror = () => {
            console.warn("Failed to load earth texture, using procedural fallback");
            // Generate procedural data
            updateGeometry(null, 2000, 1000);
        };

    }, []);

    useFrame(({ clock }) => {
        if (pointsRef.current) {
            const material = pointsRef.current.material as THREE.ShaderMaterial;
            material.uniforms.uTime.value = clock.getElapsedTime();
            material.uniforms.uMorph.value = uMorph;
        }
    });

    return (
        <group>
            {/* Dark Glossy Base Sphere */}
            <mesh>
                <sphereGeometry args={[5, 64, 64]} />
                <meshPhysicalMaterial
                    color="#0f0c29" // Very dark indigo/black
                    roughness={0.2}
                    metalness={0.8}
                    clearcoat={1.0}
                    clearcoatRoughness={0.1}
                    transparent={true}
                    opacity={0.95}
                />
            </mesh>

            {/* Particles on top */}
            <points ref={pointsRef} geometry={geometry}>
                <primitive object={shaderMaterial} attach="material" />
            </points>
        </group>
    );
}
