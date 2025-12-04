import { Html } from '@react-three/drei';
import { latLonToSphere, latLonToFlat } from '../utils/globeMath';
import type { HierarchyNode } from '../utils/hierarchyFilter';

interface BillboardLabelsProps {
    nodes: HierarchyNode[];
    uMorph: number;
    onNodeClick: (node: HierarchyNode) => void;
}

export default function BillboardLabels({ nodes, uMorph, onNodeClick }: BillboardLabelsProps) {
    return (
        <group>
            {nodes.map((node) => {
                // Calculate position based on morph state
                const spherePos = latLonToSphere(node.lat, node.lon, 5.2); // Slightly above surface
                const flatPos = latLonToFlat(node.lat, node.lon);

                // Interpolate between sphere and flat
                const x = spherePos[0] * (1 - uMorph) + flatPos[0] * uMorph;
                const y = spherePos[1] * (1 - uMorph) + flatPos[1] * uMorph;
                const z = spherePos[2] * (1 - uMorph) + 0.1 * uMorph; // Slightly above flat map

                return (
                    <Html
                        key={node.id}
                        position={[x, y, z]}
                        center
                        distanceFactor={10}
                        style={{ pointerEvents: 'auto' }}
                    >
                        <div
                            data-node-id={node.id}
                            onClick={(e) => {
                                e.stopPropagation();
                                onNodeClick(node);
                            }}
                            className="px-3 py-1.5 rounded-md bg-slate-900/90 backdrop-blur-sm border border-cyan-500/30 
                                     text-white text-xs font-medium cursor-pointer
                                     hover:bg-cyan-900/40 hover:border-cyan-400/60 hover:scale-105
                                     transition-all duration-200 whitespace-nowrap shadow-lg"
                        >
                            {node.name}
                        </div>
                    </Html>
                );
            })}
        </group>
    );
}
