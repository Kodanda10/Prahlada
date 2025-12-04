import { describe, it, expect } from 'vitest';
import { getCameraPosition, calculateBounds, type HierarchyLevel } from './cameraStates';

describe('Camera State Management', () => {
    describe('getCameraPosition', () => {
        it('should return global view camera position', () => {
            const result = getCameraPosition('global', null);

            expect(result.position).toEqual([0, 0, 22]);
            expect(result.target).toEqual([0, 0, 0]);
            expect(result.zoom).toBe(22);
        });

        it('should return Chhattisgarh state view camera position', () => {
            const cgCenter = { lat: 21.25, lon: 81.63 };
            const result = getCameraPosition('state', cgCenter);

            // Should be centered on Chhattisgarh in flat view
            expect(result.position[2]).toBe(8); // Closer zoom
            expect(result.target).not.toEqual([0, 0, 0]);
        });

        it('should return district view camera position', () => {
            const districtCenter = { lat: 21.23, lon: 81.63 };
            const result = getCameraPosition('district', districtCenter);

            expect(result.position[2]).toBe(4); // Even closer
            expect(result.target[2]).toBe(0); // Flat map (z=0)
            expect(result.zoom).toBe(4);
        });

        it('should return assembly view camera position', () => {
            const acCenter = { lat: 21.5, lon: 81.8 };
            const result = getCameraPosition('assembly', acCenter);

            expect(result.position[2]).toBe(2.5); // Very close zoom
        });

        it('should return village view camera position', () => {
            const villageCenter = { lat: 21.6, lon: 81.9 };
            const result = getCameraPosition('village', villageCenter);

            expect(result.position[2]).toBe(1.5); // Maximum zoom
        });

        it('should handle null target gracefully', () => {
            const result = getCameraPosition('district', null);

            // Should fall back to state center
            expect(result.position[2]).toBeGreaterThan(0);
        });
    });

    describe('calculateBounds', () => {
        const mockHierarchy = [
            { id: 'cg', lat: 21.25, lon: 81.63, type: 'state', parentId: null },
            { id: 'd1', lat: 21.23, lon: 81.5, type: 'district', parentId: 'cg' },
            { id: 'd2', lat: 21.5, lon: 82.0, type: 'district', parentId: 'cg' },
            { id: 'ac1', lat: 21.24, lon: 81.52, type: 'ac', parentId: 'd1' },
            { id: 'ac2', lat: 21.25, lon: 81.55, type: 'ac', parentId: 'd1' },
        ];

        it('should calculate bounds for state (null parent)', () => {
            const bounds = calculateBounds(mockHierarchy, null);

            expect(bounds.minLat).toBeLessThan(21.25);
            expect(bounds.maxLat).toBeGreaterThan(21.25);
            expect(bounds.minLon).toBeLessThan(81.63);
            expect(bounds.maxLon).toBeGreaterThan(81.63);
        });

        it('should calculate bounds for district children', () => {
            const bounds = calculateBounds(mockHierarchy, 'd1');

            // Should only include ac1 and ac2
            expect(bounds.minLat).toBeGreaterThanOrEqual(21.24);
            expect(bounds.maxLat).toBeLessThanOrEqual(21.25);
        });

        it('should return center point when no children', () => {
            const singleNode = [
                { id: 'v1', lat: 21.5, lon: 81.5, type: 'village', parentId: 'gp1' }
            ];
            const bounds = calculateBounds(singleNode, 'gp1');

            expect(bounds.minLat).toBe(21.5);
            expect(bounds.maxLat).toBe(21.5);
        });

        it('should handle empty hierarchy', () => {
            const bounds = calculateBounds([], null);

            expect(bounds.minLat).toBe(0);
            expect(bounds.maxLat).toBe(0);
        });
    });
});
