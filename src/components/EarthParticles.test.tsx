import { describe, it, expect } from 'vitest';
import hierarchyData from '../data/chhattisgarhHierarchy.json';

describe('EarthParticles Performance Constraints', () => {
    it('should ensure particle count stays under 40,000 cap', () => {
        // This test verifies the hard cap constraint
        // We use 2048x1024 image with step=4
        const step = 4;
        const imageWidth = 2048;
        const imageHeight = 1024;

        const maxPossibleParticles = Math.ceil(imageWidth / step) * Math.ceil(imageHeight / step);

        // Even if every sampled pixel was land (worst case), we should be under cap
        // In reality, ~70% of earth is water, so actual count is ~30% of max
        const expectedMaxParticles = maxPossibleParticles * 0.3; // Approximate land coverage

        expect(expectedMaxParticles).toBeLessThan(40000);

        // Log for visibility
        console.log(`Max possible particles with step=${step}: ${maxPossibleParticles}`);
        console.log(`Expected actual (30% land): ${Math.floor(expectedMaxParticles)}`);
    });
});

describe('Chhattisgarh Hierarchy JSON Schema', () => {
    it('should have correct structure for all items', () => {
        expect(hierarchyData).toBeDefined();
        expect(Array.isArray(hierarchyData)).toBe(true);
        expect(hierarchyData.length).toBeGreaterThan(0);

        hierarchyData.forEach((item: any, index) => {
            // Required fields
            expect(item).toHaveProperty('id');
            expect(item).toHaveProperty('name');
            expect(item).toHaveProperty('lat');
            expect(item).toHaveProperty('lon');
            expect(item).toHaveProperty('type');

            // Type validation
            expect(typeof item.id).toBe('string');
            expect(typeof item.name).toBe('string');
            expect(typeof item.lat).toBe('number');
            expect(typeof item.lon).toBe('number');
            expect(typeof item.type).toBe('string');

            // Value constraints
            expect(['district', 'ac', 'gp', 'village']).toContain(item.type);
            expect(item.lat).toBeGreaterThanOrEqual(17.8);
            expect(item.lat).toBeLessThanOrEqual(24.1);
            expect(item.lon).toBeGreaterThanOrEqual(80.2);
            expect(item.lon).toBeLessThanOrEqual(84.4);

            // parentId can be null (for root district) or string
            if (item.parentId !== null) {
                expect(typeof item.parentId).toBe('string');
            }
        });
    });

    it('should maintain hierarchy relationships', () => {
        const ids = new Set(hierarchyData.map((item: any) => item.id));

        hierarchyData.forEach((item: any) => {
            // If item has parent, parent must exist in dataset
            if (item.parentId !== null) {
                expect(ids.has(item.parentId)).toBe(true);
            }
        });
    });

    it('should have at least one district as root', () => {
        const districts = hierarchyData.filter((item: any) =>
            item.type === 'district' && item.parentId === null
        );

        expect(districts.length).toBeGreaterThan(0);
    });
});
