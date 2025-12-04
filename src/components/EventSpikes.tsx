import { useRef, useMemo, useLayoutEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { latLonToSphere, latLonToFlat } from '../utils/globeMath';
import type { HierarchyNode } from '../utils/hierarchyFilter';

interface EventSpikesProps {
    nodes: HierarchyNode[];
    uMorph: number;
}

// Color coding for different event types
const EVENT_COLORS = {
    district: new THREE.Color('#00FF9D'), // Green - Normal
    ac: new THREE.Color('#FFaa00'),       // Orange - Warning
    gp: new THREE.Color('#FF0055'),       // Red - Event
    village: new THREE.Color('#00D4FF'),  // Cyan - Info
};

export default function EventSpikes({ nodes, uMorph }: EventSpikesProps) {
    const meshRef = useRef<THREE.InstancedMesh>(null);
    const count = nodes.length;

    const shaderMaterial = useMemo(() => {
        return new THREE.ShaderMaterial({
            vertexShader: `
                attribute vec3 instanceColor;
                attribute mat4 aMatrixSphere;
                attribute mat4 aMatrixFlat;
                varying vec3 vColor;
                uniform float uTime;
                uniform float uMorph;
                
                mat4 mixMat4(mat4 a, mat4 b, float t) {
                    return a * (1.0 - t) + b * t;
                }
                
                void main() {
                    vColor = instanceColor;
                    
                    // Pulse effect based on instance color
                    float pulse = 1.0 + 0.4 * sin(uTime * 2.0 + instanceColor.r * 10.0);
                    
                    vec3 transformed = position;
                    transformed.y *= pulse; // Animate height
                    
                    mat4 finalInstanceMatrix = mixMat4(aMatrixSphere, aMatrixFlat, uMorph);
                    
                    vec4 mvPosition = modelViewMatrix * finalInstanceMatrix * vec4(transformed, 1.0);
                    gl_Position = projectionMatrix * mvPosition;
                }
            `,
            fragmentShader: `
                varying vec3 vColor;
                
                void main() {
                    // Gradient from bright at base to dim at top
                    float alpha = 1.0 - gl_FragCoord.y * 0.0005;
                    gl_FragColor = vec4(vColor, alpha * 0.9);
                }
            `,
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

    const { sphereMatrices, flatMatrices, colors } = useMemo(() => {
        if (count === 0) {
            return {
                sphereMatrices: new Float32Array(0),
                flatMatrices: new Float32Array(0),
                colors: new Float32Array(0)
            };
        }

        const sphereMats = new Float32Array(count * 16);
        const flatMats = new Float32Array(count * 16);
        const cols = new Float32Array(count * 3);

        const dummy = new THREE.Object3D();

        nodes.forEach((node, i) => {
            // Determine color based on type
            const color = EVENT_COLORS[node.type as keyof typeof EVENT_COLORS] || EVENT_COLORS.district;
            color.toArray(cols, i * 3);

            // Sphere Transform
            const [sx, sy, sz] = latLonToSphere(node.lat, node.lon, 5);
            dummy.position.set(sx, sy, sz);
            dummy.lookAt(0, 0, 0);
            dummy.rotateX(-Math.PI / 2); // Point outward from sphere
            dummy.updateMatrix();
            sphereMats.set(dummy.matrix.elements, i * 16);

            // Flat Transform
            const [fx, fy] = latLonToFlat(node.lat, node.lon);
            dummy.position.set(fx, fy, 0);
            dummy.rotation.set(0, 0, 0);
            dummy.rotateX(Math.PI / 2); // Point upward in flat view
            dummy.updateMatrix();
            flatMats.set(dummy.matrix.elements, i * 16);
        });

        return { sphereMatrices: sphereMats, flatMatrices: flatMats, colors: cols };
    }, [nodes, count]);

    useLayoutEffect(() => {
        if (meshRef.current && count > 0) {
            meshRef.current.geometry.setAttribute('aMatrixSphere', new THREE.InstancedBufferAttribute(sphereMatrices, 16));
            meshRef.current.geometry.setAttribute('aMatrixFlat', new THREE.InstancedBufferAttribute(flatMatrices, 16));
            meshRef.current.geometry.setAttribute('instanceColor', new THREE.InstancedBufferAttribute(colors, 3));
        }
    }, [sphereMatrices, flatMatrices, colors, count]);

    useFrame(({ clock }) => {
        if (meshRef.current) {
            const material = meshRef.current.material as THREE.ShaderMaterial;
            material.uniforms.uTime.value = clock.getElapsedTime();
            material.uniforms.uMorph.value = uMorph;
        }
    });

    if (count === 0) {
        return null;
    }

    return (
        <instancedMesh ref={meshRef} args={[undefined, undefined, count]}>
            {/* Tall cylinder geometry instead of cone */}
            <cylinderGeometry args={[0.04, 0.04, 3.0, 8]} />
            <primitive object={shaderMaterial} attach="material" />
        </instancedMesh>
    );
}
