import { describe, it, expect } from 'vitest';
import { getVisibleNodes, getBreadcrumbs, getChildren, type HierarchyNode } from './hierarchyFilter';

const mockHierarchy: HierarchyNode[] = [
    { id: 'cg', name: 'Chhattisgarh', lat: 21.25, lon: 81.63, type: 'state', parentId: null },
    { id: 'd_raipur', name: 'Raipur', lat: 21.23, lon: 81.63, type: 'district', parentId: 'cg' },
    { id: 'd_balod', name: 'बालोद', lat: 20.73, lon: 81.20, type: 'district', parentId: 'cg' },
    { id: 'ac_raipur_city', name: 'Raipur City', lat: 21.25, lon: 81.63, type: 'ac', parentId: 'd_raipur' },
    { id: 'ac_arang', name: 'Arang', lat: 21.20, lon: 81.97, type: 'ac', parentId: 'd_raipur' },
    { id: 'gp_sonakhan', name: 'Sonakhan GP', lat: 20.75, lon: 81.25, type: 'gp', parentId: 'ac_arang' },
    { id: 'v_sonakhan', name: 'Sonakhan Village', lat: 20.76, lon: 81.26, type: 'village', parentId: 'gp_sonakhan' },
];

describe('Hierarchy Filtering', () => {
    describe('getVisibleNodes', () => {
        it('should return all nodes when no focus (global view)', () => {
            const result = getVisibleNodes(mockHierarchy, null);
            expect(result.length).toBe(mockHierarchy.length);
        });

        it('should return state and its direct children (districts) when focused on state', () => {
            const cgNode = mockHierarchy.find(n => n.id === 'cg')!;
            const result = getVisibleNodes(mockHierarchy, cgNode);

            const resultIds = result.map(n => n.id);
            expect(resultIds).toContain('cg');
            expect(resultIds).toContain('d_raipur');
            expect(resultIds).toContain('d_balod');
            expect(resultIds).not.toContain('ac_raipur_city'); // Grandchildren not visible
        });

        it('should return district and its assemblies when focused on district', () => {
            const raipurNode = mockHierarchy.find(n => n.id === 'd_raipur')!;
            const result = getVisibleNodes(mockHierarchy, raipurNode);

            const resultIds = result.map(n => n.id);
            expect(resultIds).toContain('d_raipur');
            expect(resultIds).toContain('ac_raipur_city');
            expect(resultIds).toContain('ac_arang');
            expect(resultIds).not.toContain('d_balod'); // Sibling not visible
            expect(resultIds).not.toContain('gp_sonakhan'); // Grandchildren not visible
        });

        it('should return assembly and its GPs when focused on assembly', () => {
            const arangNode = mockHierarchy.find(n => n.id === 'ac_arang')!;
            const result = getVisibleNodes(mockHierarchy, arangNode);

            const resultIds = result.map(n => n.id);
            expect(resultIds).toContain('ac_arang');
            expect(resultIds).toContain('gp_sonakhan');
            expect(resultIds).not.toContain('ac_raipur_city'); // Sibling not visible
        });

        it('should return GP and its villages when focused on GP', () => {
            const gpNode = mockHierarchy.find(n => n.id === 'gp_sonakhan')!;
            const result = getVisibleNodes(mockHierarchy, gpNode);

            const resultIds = result.map(n => n.id);
            expect(resultIds).toContain('gp_sonakhan');
            expect(resultIds).toContain('v_sonakhan');
        });
    });

    describe('getBreadcrumbs', () => {
        it('should return single breadcrumb for root', () => {
            const breadcrumbs = getBreadcrumbs(mockHierarchy, 'cg');
            expect(breadcrumbs).toEqual(['Chhattisgarh']);
        });

        it('should return path from state to district', () => {
            const breadcrumbs = getBreadcrumbs(mockHierarchy, 'd_raipur');
            expect(breadcrumbs).toEqual(['Chhattisgarh', 'Raipur']);
        });

        it('should return full path to village', () => {
            const breadcrumbs = getBreadcrumbs(mockHierarchy, 'v_sonakhan');
            expect(breadcrumbs).toEqual([
                'Chhattisgarh',
                'Raipur',
                'Arang',
                'Sonakhan GP',
                'Sonakhan Village'
            ]);
        });

        it('should handle non-existent ID gracefully', () => {
            const breadcrumbs = getBreadcrumbs(mockHierarchy, 'invalid_id');
            expect(breadcrumbs).toEqual([]);
        });
    });

    describe('getChildren', () => {
        it('should return all root nodes when parentId is null', () => {
            const children = getChildren(mockHierarchy, null);
            expect(children.length).toBe(1);
            expect(children[0].id).toBe('cg');
        });

        it('should return direct children of a node', () => {
            const children = getChildren(mockHierarchy, 'cg');
            expect(children.length).toBe(2);
            expect(children.map(c => c.id)).toContain('d_raipur');
            expect(children.map(c => c.id)).toContain('d_balod');
        });

        it('should return empty array if node has no children', () => {
            const children = getChildren(mockHierarchy, 'v_sonakhan');
            expect(children.length).toBe(0);
        });
    });
});
