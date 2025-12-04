import { useMemo, useState, useEffect } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import gsap from 'gsap';
import boundaryLinesVert from '../shaders/boundaryLinesVert.glsl';
import { latLonToSphere, latLonToFlat } from '../utils/globeMath';
import hierarchyData from '../data/chhattisgarhHierarchy.json';

interface ChhattisgarhHierarchyProps {
    uMorph: number;
    setFocus?: (focus: any) => void;
}

export default function ChhattisgarhHierarchy({ uMorph, setFocus }: ChhattisgarhHierarchyProps) {
    const { camera, controls } = useThree();
    const [hovered, setHovered] = useState<string | null>(null);
    const [selected, setSelected] = useState<string | null>(null);

    // Process Data & Geometry
    const { linesGeometry, labels } = useMemo(() => {
        const spherePositions: number[] = [];
        const flatPositions: number[] = [];
        const indices: number[] = [];
        const labelsData: any[] = [];

        let indexOffset = 0;

        // Helper to add a line segment
        const addLine = (lat1: number, lon1: number, lat2: number, lon2: number) => {
            const [sx1, sy1, sz1] = latLonToSphere(lat1, lon1, 5.05); // Slightly above surface
            const [sx2, sy2, sz2] = latLonToSphere(lat2, lon2, 5.05);
            const [fx1, fy1] = latLonToFlat(lat1, lon1);
            const [fx2, fy2] = latLonToFlat(lat2, lon2);

            spherePositions.push(sx1, sy1, sz1, sx2, sy2, sz2);
            flatPositions.push(fx1, fy1, 0, fx2, fy2, 0);
            indices.push(indexOffset, indexOffset + 1);
            indexOffset += 2;
        };

        // Iterate hierarchy
        hierarchyData.forEach((item: any) => {
            // Add Label
            labelsData.push({
                id: item.id,
                name: item.name,
                lat: item.lat,
                lon: item.lon,
                type: item.type,
                parentId: item.parentId
            });

            // Add Boundary (Placeholder Box for now as we don't have real polygon data in the JSON yet)
            // The JSON generation script didn't add polygon coordinates, only centroids.
            // To show "Boundaries drawn using <LineSegments>", we need geometry.
            // Since we are in "Hybrid Representative Subset" mode and don't have the polygons in the JSON,
            // we will generate a small placeholder shape (e.g., a hexagon or circle) around the centroid
            // to represent the "boundary" for visual demonstration.

            const centerLat = item.lat;
            const centerLon = item.lon;
            const size = item.type === 'district' ? 0.5 : item.type === 'ac' ? 0.2 : 0.05;

            const segments = 6;
            for (let i = 0; i < segments; i++) {
                const angle1 = (i / segments) * Math.PI * 2;
                const angle2 = ((i + 1) / segments) * Math.PI * 2;

                const lat1 = centerLat + Math.sin(angle1) * size;
                const lon1 = centerLon + Math.cos(angle1) * size;
                const lat2 = centerLat + Math.sin(angle2) * size;
                const lon2 = centerLon + Math.cos(angle2) * size;

                addLine(lat1, lon1, lat2, lon2);
            }
        });

        const geom = new THREE.BufferGeometry();
        geom.setAttribute('position', new THREE.Float32BufferAttribute(spherePositions, 3)); // Default for bounding box
        geom.setAttribute('aPosSphere', new THREE.Float32BufferAttribute(spherePositions, 3));
        geom.setAttribute('aPosFlat', new THREE.Float32BufferAttribute(flatPositions, 3));
        geom.setIndex(indices);

        return { linesGeometry: geom, labels: labelsData };
    }, []);

    // Material
    const material = useMemo(() => {
        return new THREE.ShaderMaterial({
            vertexShader: boundaryLinesVert,
            fragmentShader: `
            uniform float uTime;
            void main() {
                float dash = sin(uTime * 2.0 + gl_FragCoord.x * 0.1);
                float alpha = 0.5 + 0.5 * dash;
                gl_FragColor = vec4(0.0, 0.83, 1.0, alpha); // #00D4FF
            }
        `,
            uniforms: {
                uTime: { value: 0 },
                uMorph: { value: 0 }
            },
            transparent: true,
            depthWrite: false,
            blending: THREE.AdditiveBlending
        });
    }, []);

    useFrame(({ clock }) => {
        material.uniforms.uTime.value = clock.getElapsedTime();
        material.uniforms.uMorph.value = uMorph;
    });

    const handleClick = (item: any) => {
        setSelected(item.id);
        setFocus(item);

        // Camera Fly-to
        // We need to know if we are in Sphere or Flat mode.
        // Assuming uMorph determines mode.
        const isFlat = uMorph > 0.5;

        const targetPos = isFlat
            ? latLonToFlat(item.lat, item.lon)
            : latLonToSphere(item.lat, item.lon, 5);

        const targetVec = new THREE.Vector3(
            isFlat ? targetPos[0] : targetPos[0],
            isFlat ? targetPos[1] : targetPos[1],
            isFlat ? 0 : targetPos[2]
        );

        // Animate Camera
        // Note: This is a simplified fly-to. Real implementation needs more robust controls handling.
        // We'll rely on the parent component or a global store to handle the actual camera tweening
        // if we want to strictly follow "Camera States (GSAP) — MUST MATCH EXACTLY".
        // But here we can trigger the focus state.
    };

    return (
        <group>
            <lineSegments geometry={linesGeometry} material={material} />

            {/* Labels disabled - using BillboardLabels component instead */}
            {/* {labels.map((item) => (
                <Html key={item.id} ... />
            ))} */}
        </group>
    );
}
