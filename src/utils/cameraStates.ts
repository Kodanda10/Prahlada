import { latLonToFlat } from './globeMath';

export type HierarchyLevel = 'global' | 'state' | 'district' | 'assembly' | 'village';

export interface CameraState {
    position: [number, number, number];
    target: [number, number, number];
    zoom: number;
}

export interface Bounds {
    minLat: number;
    maxLat: number;
    minLon: number;
    maxLon: number;
    centerLat: number;
    centerLon: number;
}

interface HierarchyNode {
    id: string;
    lat: number;
    lon: number;
    type: string;
    parentId: string | null;
}

const CHHATTISGARH_CENTER = { lat: 21.25, lon: 81.63 };

/**
 * Calculate camera position and target based on hierarchy level and focus target
 */
export function getCameraPosition(
    level: HierarchyLevel,
    target: { lat: number; lon: number } | null
): CameraState {
    const effectiveTarget = target || CHHATTISGARH_CENTER;

    // Calculate flat map coordinates
    const [fx, fy] = latLonToFlat(effectiveTarget.lat, effectiveTarget.lon);

    // Define zoom levels for each hierarchy
    const zoomLevels: Record<HierarchyLevel, number> = {
        global: 22,
        state: 8,
        district: 4,
        assembly: 2.5,
        village: 1.5
    };

    const zoom = zoomLevels[level];

    if (level === 'global') {
        return {
            position: [0, 0, 22],
            target: [0, 0, 0],
            zoom: 22
        };
    }

    // For all other levels, position camera above the target in flat map view
    return {
        position: [fx, fy, zoom],
        target: [fx, fy, 0],
        zoom
    };
}

/**
 * Calculate geographic bounds for a set of hierarchy nodes
 */
export function calculateBounds(
    hierarchyData: HierarchyNode[],
    parentId: string | null
): Bounds {
    // Filter nodes that belong to this parent
    const nodes = parentId === null
        ? hierarchyData
        : hierarchyData.filter(node => node.parentId === parentId);

    if (nodes.length === 0) {
        return {
            minLat: 0,
            maxLat: 0,
            minLon: 0,
            maxLon: 0,
            centerLat: 0,
            centerLon: 0
        };
    }

    const lats = nodes.map(n => n.lat);
    const lons = nodes.map(n => n.lon);

    const minLat = Math.min(...lats);
    const maxLat = Math.max(...lats);
    const minLon = Math.min(...lons);
    const maxLon = Math.max(...lons);

    return {
        minLat,
        maxLat,
        minLon,
        maxLon,
        centerLat: (minLat + maxLat) / 2,
        centerLon: (minLon + maxLon) / 2
    };
}
