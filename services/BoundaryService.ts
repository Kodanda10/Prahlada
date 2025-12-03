

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
     * 2. Fetch AC boundaries from Overpass API.
     * 3. Match Overpass results with LGD list.
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

            // 2. Fetch from Overpass (Admin Level 7 = Assembly?)
            console.log('⏳ Fetching AC boundaries from Overpass...');
            const overpassData = await this.fetchFromOverpass(districtName, 7);

            if (overpassData && overpassData.features.length > 0) {
                // 3. Match Overpass results with LGD list
                // We filter the Overpass results to only include those that roughly match our LGD list
                // This helps avoid showing irrelevant boundaries
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

                // If filtering removed everything, maybe just return original?
                // For now, let's return original but log warning
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
     * Fetch blocks for a district
     */
    async fetchDistrictBlocks(districtName: string): Promise<BoundaryCollection | null> {
        const cacheKey = `blocks_${districtName}`;
        if (this.boundaryCache[cacheKey]) return this.boundaryCache[cacheKey];

        try {
            // 1. Get Block List from Hierarchy (This is a bit harder as blocks are nested under ACs in our hierarchy structure)
            // We need to flatten the hierarchy to get all blocks in the district
            const hierarchy = await this.loadHierarchyData();
            if (!hierarchy || !hierarchy[districtName]) return null;

            const blockNames = new Set<string>();
            Object.values(hierarchy[districtName]).forEach(acBlocks => {
                Object.keys(acBlocks).forEach(blockName => blockNames.add(blockName));
            });

            console.log(`📍 Found ${blockNames.size} Blocks in ${districtName} (LGD)`);

            // 2. Fetch from Overpass (Admin Level 6 = Tehsil/Taluk)
            const overpassData = await this.fetchFromOverpass(districtName, 6);

            if (overpassData && overpassData.features.length > 0) {
                // 3. Match Overpass results with LGD list
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
