

const OVERPASS_API = 'https://overpass-api.de/api/interpreter';

interface BoundaryFeature {
    type: 'Feature';
    geometry: {
        type: 'Polygon' | 'MultiPolygon' | 'Point';
        coordinates: number[] | number[][][] | number[][][][];
    };
    properties: {
        name: string;
        id: string;
        type: 'STATE' | 'DISTRICT' | 'ASSEMBLY' | 'BLOCK' | 'VILLAGE';
        adminLevel?: number;
        population?: number;
        isPoint?: boolean;
    };
}

interface BoundaryCollection {
    type: 'FeatureCollection';
    features: BoundaryFeature[];
}

// New Hierarchy Interface based on LGD Data
interface HierarchyData {
    [districtName: string]: {
        [acName: string]: {
            [blockName: string]: Array<{
                code: string;
                name: string;
                lat?: number;
                lng?: number;
            }>;
        };
    };
}



export const BoundaryService = {
    boundaryCache: {} as Record<string, BoundaryCollection>,
    hierarchyData: null as HierarchyData | null,

    /**
     * Load the hierarchical geography data (LGD Source)
     */
    async loadHierarchyData(): Promise<HierarchyData | null> {
        if (this.hierarchyData) return this.hierarchyData;

        try {
            const response = await fetch('/chhattisgarh_hierarchy_enriched.json');
            if (!response.ok) {
                console.warn('Failed to load hierarchy data');
                return null;
            }
            this.hierarchyData = await response.json();
            console.log('📚 Loaded LGD hierarchy data');
            return this.hierarchyData;
        } catch (error) {
            console.error('Error loading hierarchy data:', error);
            return null;
        }
    },

    /**
     * Fetch Assembly Constituencies (Vidhan Sabha) for a district
     * 
     * Strategy:
     * 1. Get AC list from LGD Hierarchy.
     * 2. Try to generate boundaries from Village Points (Convex Hull).
     * 3. Fallback to Overpass API if generation fails.
     */
    async fetchDistrictAssemblies(districtName: string): Promise<BoundaryCollection | null> {
        const cacheKey = `assemblies_${districtName}`;

        if (this.boundaryCache[cacheKey]) {
            console.log(`📦 Using cached assemblies for ${districtName}`);
            return this.boundaryCache[cacheKey];
        }

        try {
            // 1. Get AC List from Hierarchy
            const hierarchy = await this.loadHierarchyData();
            if (!hierarchy || !hierarchy[districtName]) {
                console.warn(`District ${districtName} not found in hierarchy`);
                return null;
            }

            const acNames = Object.keys(hierarchy[districtName]);
            console.log(`📍 Found ${acNames.length} ACs in ${districtName} (LGD):`, acNames);

            // 2. Try Local Generation (Convex Hull from Villages)
            const generatedBoundaries = await this.createACBoundariesFromVillages(districtName, hierarchy[districtName]);
            if (generatedBoundaries && generatedBoundaries.features.length > 0) {
                console.log(`✅ Generated ${generatedBoundaries.features.length} AC boundaries from village points`);
                this.boundaryCache[cacheKey] = generatedBoundaries;
                return generatedBoundaries;
            }

            // 3. Fallback to Overpass (Admin Level 7 = Assembly?)
            console.log('⏳ Fetching AC boundaries from Overpass...');
            const overpassData = await this.fetchFromOverpass(districtName, 7);

            if (overpassData && overpassData.features.length > 0) {
                // Match Overpass results with LGD list
                const filteredFeatures = overpassData.features.filter(feature => {
                    const featureName = feature.properties.name.toLowerCase();
                    return acNames.some(acName => featureName.includes(acName.toLowerCase()) || acName.toLowerCase().includes(featureName));
                });

                if (filteredFeatures.length > 0) {
                    const filteredData: BoundaryCollection = {
                        ...overpassData,
                        features: filteredFeatures
                    };
                    this.boundaryCache[cacheKey] = filteredData;
                    return filteredData;
                }

                console.warn(`⚠️ Overpass found boundaries but none matched LGD names for ${districtName}. Returning all found.`);
                this.boundaryCache[cacheKey] = overpassData;
                return overpassData;
            }

            console.warn(`⚠️ Overpass failed to find ACs for ${districtName}.`);
            return null;

        } catch (error) {
            console.error(`Error fetching assemblies for ${districtName}:`, error);
            return null;
        }
    },

    /**
     * Generate AC boundaries using Convex Hull of villages
     */
    async createACBoundariesFromVillages(districtName: string, acData: any): Promise<BoundaryCollection | null> {
        try {
            // We need d3-polygon for convex hull. 
            // Since we can't easily import d3 here without ensuring it's in package.json and installed,
            // we will implement a simple Monotone Chain algorithm for Convex Hull.

            const features: BoundaryFeature[] = [];

            for (const acName in acData) {
                const blocks = acData[acName];
                let allPoints: [number, number][] = [];

                // Collect all village coordinates in this AC
                for (const blockName in blocks) {
                    const villages = blocks[blockName];
                    villages.forEach((v: any) => {
                        if (v.lat && v.lng) {
                            allPoints.push([v.lng, v.lat]);
                        }
                    });
                }

                if (allPoints.length < 3) continue;

                // Compute Convex Hull
                const hull = this.calculateConvexHull(allPoints);

                if (hull.length > 2) {
                    // Close the polygon
                    hull.push(hull[0]);

                    features.push({
                        type: 'Feature',
                        geometry: {
                            type: 'Polygon',
                            coordinates: [hull]
                        },
                        properties: {
                            name: acName,
                            id: `ac_gen_${acName.replace(/\s+/g, '_')}`,
                            type: 'ASSEMBLY',
                            adminLevel: 7
                        }
                    });
                }
            }

            if (features.length === 0) return null;

            return {
                type: 'FeatureCollection',
                features
            };

        } catch (e) {
            console.error("Error generating AC boundaries:", e);
            return null;
        }
    },

    /**
     * Monotone Chain Convex Hull Algorithm
     */
    calculateConvexHull(points: [number, number][]): [number, number][] {
        points.sort((a, b) => a[0] === b[0] ? a[1] - b[1] : a[0] - b[0]);

        const cross = (o: [number, number], a: [number, number], b: [number, number]) => {
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
        };

        const lower: [number, number][] = [];
        for (const p of points) {
            while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) {
                lower.pop();
            }
            lower.push(p);
        }

        const upper: [number, number][] = [];
        for (let i = points.length - 1; i >= 0; i--) {
            const p = points[i];
            while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) {
                upper.pop();
            }
            upper.push(p);
        }

        upper.pop();
        lower.pop();
        return lower.concat(upper);
    },

    /**
     * Fetch blocks for a district
     */
    async fetchDistrictBlocks(districtName: string): Promise<BoundaryCollection | null> {
        const cacheKey = `blocks_${districtName}`;
        if (this.boundaryCache[cacheKey]) return this.boundaryCache[cacheKey];

        try {
            // 1. Get Block List from Hierarchy
            const hierarchy = await this.loadHierarchyData();
            if (!hierarchy || !hierarchy[districtName]) return null;

            const blockNames = new Set<string>();
            Object.values(hierarchy[districtName]).forEach(acBlocks => {
                Object.keys(acBlocks).forEach(blockName => blockNames.add(blockName));
            });

            console.log(`📍 Found ${blockNames.size} Blocks in ${districtName} (LGD)`);

            // 2. Try Local Generation (Convex Hull from Villages)
            const generatedBoundaries = await this.createBlockBoundariesFromVillages(districtName, hierarchy[districtName]);
            if (generatedBoundaries && generatedBoundaries.features.length > 0) {
                console.log(`✅ Generated ${generatedBoundaries.features.length} Block boundaries from village points`);
                this.boundaryCache[cacheKey] = generatedBoundaries;
                return generatedBoundaries;
            }

            // 3. Fallback to Overpass (Admin Level 6 = Tehsil/Taluk)
            const overpassData = await this.fetchFromOverpass(districtName, 6);

            if (overpassData && overpassData.features.length > 0) {
                // Match Overpass results with LGD list
                const filteredFeatures = overpassData.features.filter(feature => {
                    const featureName = feature.properties.name.toLowerCase();
                    return Array.from(blockNames).some(blockName => featureName.includes(blockName.toLowerCase()) || blockName.toLowerCase().includes(featureName));
                });

                if (filteredFeatures.length > 0) {
                    const filteredData: BoundaryCollection = {
                        ...overpassData,
                        features: filteredFeatures
                    };
                    this.boundaryCache[cacheKey] = filteredData;
                    return filteredData;
                }

                this.boundaryCache[cacheKey] = overpassData;
                return overpassData;
            }
            return null;
        } catch (error) {
            console.error(`Error fetching blocks for ${districtName}:`, error);
            return null;
        }
    },

    /**
     * Generate Block boundaries using Convex Hull of villages
     */
    async createBlockBoundariesFromVillages(districtName: string, acData: any): Promise<BoundaryCollection | null> {
        try {
            const features: BoundaryFeature[] = [];
            const blockPoints: Record<string, [number, number][]> = {};

            // Group points by Block
            for (const acName in acData) {
                const blocks = acData[acName];
                for (const blockName in blocks) {
                    if (!blockPoints[blockName]) blockPoints[blockName] = [];

                    const villages = blocks[blockName];
                    villages.forEach((v: any) => {
                        if (v.lat && v.lng) {
                            blockPoints[blockName].push([v.lng, v.lat]);
                        }
                    });
                }
            }

            // Generate Hull for each Block
            for (const blockName in blockPoints) {
                const points = blockPoints[blockName];
                if (points.length < 3) continue;

                const hull = this.calculateConvexHull(points);

                if (hull.length > 2) {
                    hull.push(hull[0]); // Close polygon

                    features.push({
                        type: 'Feature',
                        geometry: {
                            type: 'Polygon',
                            coordinates: [hull]
                        },
                        properties: {
                            name: blockName,
                            id: `block_gen_${blockName.replace(/\s+/g, '_')}`,
                            type: 'BLOCK',
                            adminLevel: 6
                        }
                    });
                }
            }

            if (features.length === 0) return null;

            return {
                type: 'FeatureCollection',
                features
            };

        } catch (e) {
            console.error("Error generating Block boundaries:", e);
            return null;
        }
    },

    /**
     * Fetch villages for a block - RENDERED AS POINTS
     * 
     * Strategy:
     * 1. Get Village list from LGD Hierarchy.
     * 2. Fetch Village nodes from Overpass (place=village/hamlet) in the Block.
     * 3. Match/Enrich.
     */
    async fetchBlockVillages(blockName: string): Promise<BoundaryCollection | null> {
        const cacheKey = `villages_${blockName}`;
        if (this.boundaryCache[cacheKey]) return this.boundaryCache[cacheKey];

        try {
            // 1. Get Village List from Hierarchy
            const hierarchy = await this.loadHierarchyData();
            if (!hierarchy) return null;

            // Find the block in the hierarchy
            // Since block names are unique within a district but maybe not globally, we should ideally know the district.
            // However, the current signature only takes blockName.
            // We'll search for the block across the hierarchy.

            let villages: Array<{ code: string; name: string; lat?: number; lng?: number }> = [];
            let found = false;

            for (const district in hierarchy) {
                for (const ac in hierarchy[district]) {
                    if (hierarchy[district][ac][blockName]) {
                        villages = hierarchy[district][ac][blockName];
                        found = true;
                        break;
                    }
                }
                if (found) break;
            }

            if (!found || villages.length === 0) {
                console.warn(`Block ${blockName} not found in hierarchy or has no villages`);
                return null;
            }

            console.log(`📍 Found ${villages.length} villages in ${blockName} (LGD)`);

            // 2. Convert to GeoJSON Points
            const features: BoundaryFeature[] = villages
                .filter(v => v.lat && v.lng) // Only those with coordinates
                .map(v => ({
                    type: 'Feature',
                    geometry: {
                        type: 'Point',
                        coordinates: [v.lng!, v.lat!]
                    },
                    properties: {
                        name: v.name,
                        id: v.code,
                        type: 'VILLAGE',
                        adminLevel: 8,
                        isPoint: true
                    }
                }));

            if (features.length === 0) {
                console.warn(`No villages with coordinates found for ${blockName}`);
                return null;
            }

            const collection: BoundaryCollection = {
                type: 'FeatureCollection',
                features
            };

            this.boundaryCache[cacheKey] = collection;
            console.log(`✅ Loaded ${features.length} village points for ${blockName} from Local Data`);
            return collection;

        } catch (error) {
            console.error(`Error fetching villages for ${blockName}:`, error);
            return null;
        }
    },

    /**
     * Load village data (Deprecated/Unused now, kept for interface compatibility if needed)
     */
    async loadVillageData(): Promise<any | null> {
        return null;
    },

    /**
     * Fetch from Overpass API (Generic)
     */
    async fetchFromOverpass(
        searchArea: string,
        adminLevel: number
    ): Promise<BoundaryCollection | null> {
        try {
            const query = `
                [out:json][timeout:60];
                area["name"="${searchArea}"]->.searchArea;
                (
                    relation["boundary"="administrative"]["admin_level"="${adminLevel}"](area.searchArea);
                );
                out geom;
            `;

            console.log(`🌍 Fetching from Overpass (level ${adminLevel} in ${searchArea})`);

            const response = await fetch(OVERPASS_API, {
                method: 'POST',
                body: query,
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });

            if (!response.ok) return null;

            const data = await response.json();

            if (!data.elements || data.elements.length === 0) {
                return null;
            }

            console.log(`✅ Found ${data.elements.length} boundaries from Overpass`);
            return this.convertOverpassToGeoJSON(data, adminLevel);
        } catch (error) {
            console.error(`❌ Overpass API error:`, error);
            return null;
        }
    },

    /**
     * Convert Overpass JSON to GeoJSON
     */
    convertOverpassToGeoJSON(overpassData: any, adminLevel: number): BoundaryCollection | null {
        try {
            const features: BoundaryFeature[] = [];

            for (const element of overpassData.elements) {
                if (element.type !== 'relation') continue;

                const geometry = this.extractGeometry(element);
                if (!geometry) continue;

                const typeMap: Record<number, BoundaryFeature['properties']['type']> = {
                    4: 'STATE',
                    5: 'DISTRICT',
                    6: 'BLOCK',
                    7: 'ASSEMBLY',
                    8: 'VILLAGE'
                };

                features.push({
                    type: 'Feature',
                    geometry,
                    properties: {
                        name: element.tags?.name || element.tags?.['name:hi'] || `Unnamed`,
                        id: `osm_${element.id}`,
                        type: typeMap[adminLevel] || 'BLOCK',
                        adminLevel
                    }
                });
            }

            if (features.length === 0) return null;

            return {
                type: 'FeatureCollection',
                features
            };
        } catch (error) {
            console.error('Error converting Overpass to GeoJSON:', error);
            return null;
        }
    },

    /**
     * Extract geometry from Overpass relation
     */
    extractGeometry(element: any): BoundaryFeature['geometry'] | null {
        try {
            if (!element.members) return null;

            const outerWays: number[][][] = [];

            for (const member of element.members) {
                if (member.type !== 'way' || !member.geometry) continue;

                const coordinates: number[][] = member.geometry.map((node: any) => [node.lon, node.lat]);

                if (member.role === 'outer' || !member.role) {
                    outerWays.push(coordinates);
                }
            }

            if (outerWays.length === 0) return null;

            if (outerWays.length === 1) {
                return {
                    type: 'Polygon',
                    coordinates: outerWays
                };
            }

            return {
                type: 'MultiPolygon',
                coordinates: outerWays.map(outer => [outer])
            };
        } catch (error) {
            return null;
        }
    },

    /**
     * Clear the cache
     */
    clearCache() {
        this.boundaryCache = {};
    },
};
