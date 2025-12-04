import { describe, it, expect, vi } from 'vitest';
import BillboardLabels from './BillboardLabels';
import type { HierarchyNode } from '../utils/hierarchyFilter';

const mockNodes: HierarchyNode[] = [
    { id: 'd1', name: 'Raipur District', lat: 21.23, lon: 81.63, type: 'district', parentId: 'cg' },
    { id: 'd2', name: 'बालोद', lat: 20.73, lon: 81.20, type: 'district', parentId: 'cg' },
    { id: 'ac1', name: 'Raipur City', lat: 21.25, lon: 81.65, type: 'ac', parentId: 'd1' },
];

describe('BillboardLabels', () => {
    it('should render component without errors', () => {
        const handleClick = vi.fn();

        // Just verify the component can be instantiated
        expect(() => BillboardLabels({
            nodes: mockNodes,
            uMorph: 0,
            onNodeClick: handleClick
        })).not.toThrow();
    });

    it('should handle empty nodes array', () => {
        const handleClick = vi.fn();

        expect(() => BillboardLabels({
            nodes: [],
            uMorph: 1.0,
            onNodeClick: handleClick
        })).not.toThrow();
    });

    it('should accept uMorph parameter', () => {
        const handleClick = vi.fn();

        expect(() => BillboardLabels({
            nodes: mockNodes,
            uMorph: 0.5, // Mid-morph
            onNodeClick: handleClick
        })).not.toThrow();
    });

    it('should accept onNodeClick callback', () => {
        const handleClick = vi.fn();

        const result = BillboardLabels({
            nodes: mockNodes,
            uMorph: 1.0,
            onNodeClick: handleClick
        });

        expect(result).toBeTruthy();
    });
});
