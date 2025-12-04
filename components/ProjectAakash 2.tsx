import React, { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, MapPin, ChevronRight, Navigation, Globe, X, LocateFixed } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import * as d3 from 'd3-geo';
import { BoundaryService } from '../services/BoundaryService';

/** --- UTILS --- */
function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

// REMOVED: generateMapData and MAP_DATA
// We now fetch real data in the component

export type GeoFeature = {
    id: string;
    name: string;
    type: 'STATE' | 'DISTRICT' | 'ASSEMBLY' | 'BLOCK' | 'VILLAGE';
    path: string; // SVG Path
    bounds: { x: number; y: number; w: number; h: number };
    color: string;
    children?: GeoFeature[];
};

/** --- COMPONENT: PROJECT AAKASH --- */

interface ProjectAakashProps {
    onSelect: (location: any) => void;
    onClose: () => void;
}

export default function ProjectAakash({ onSelect, onClose }: ProjectAakashProps) {
    // Navigation State
    const [history, setHistory] = useState<GeoFeature[]>([]);
    const [currentLevelFeatures, setCurrentLevelFeatures] = useState<GeoFeature[]>([]); // Start empty
    const [viewBox, setViewBox] = useState("0 0 1000 1000"); // Standard SVG coordinate system
    const [isHovering, setIsHovering] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Store the initial set of districts for resetting
    const [initialDistricts, setInitialDistricts] = useState<GeoFeature[]>([]);

    // Derived State
    const activeFeature = history[history.length - 1];
    const breadcrumbs = ['छत्तीसगढ़', ...history.map(h => h.name)];

    // Load Real Map Data
    useEffect(() => {
        async function loadRealMap() {
            try {
                const response = await fetch('/chhattisgarh_districts.json');
                if (!response.ok) throw new Error('Failed to load map data');
                const data = await response.json();

                // Setup Projection
                // Center on Chhattisgarh (approx 82.0, 21.5)
                // Scale and Translate to fit 1000x1000 box
                const projection = d3.geoMercator()
                    .center([82.4, 21.2])
                    .scale(6000)
                    .translate([500, 500]);

                const pathGenerator = d3.geoPath().projection(projection);

                const realShapes: GeoFeature[] = data.features.map((f: any, i: number) => {
                    const bounds = pathGenerator.bounds(f);
                    // FIX: Use DHSREGEN for the district name based on the file inspection
                    const name = f.properties.DHSREGEN || f.properties.district || `District ${i}`;

                    return {
                        id: f.properties.district_code || `dist_${i}`,
                        name: name,
                        type: 'DISTRICT',
                        path: pathGenerator(f) || "",
                        bounds: {
                            x: bounds[0][0],
                            y: bounds[0][1],
                            w: bounds[1][0] - bounds[0][0],
                            h: bounds[1][1] - bounds[0][1]
                        },
                        color: '#06b6d4'
                    };
                });

                setCurrentLevelFeatures(realShapes);
                setInitialDistricts(realShapes); // Store initial districts
                setIsLoading(false);
            } catch (e) {
                console.error("Map Load Error:", e);
                setIsLoading(false);
            }
        }

        loadRealMap();
    }, []);

    // Fetch children from API
    // Fetch children from API (or Local Hierarchy Fallback)
    const fetchChildrenFromApi = async (parentId: string, level: 'district' | 'assembly' | 'block'): Promise<{ id: string, name: string, type: string }[]> => {
        // 1. Try Local Hierarchy First (Faster & Reliable)
        try {
            const hierarchy = await BoundaryService.loadHierarchyData();
            if (hierarchy) {
                if (level === 'assembly') {
                    // parentId is District Name
                    // Handle case mismatch just in case
                    const distName = Object.keys(hierarchy).find(d => d.toLowerCase() === parentId.toLowerCase());
                    if (distName && hierarchy[distName]) {
                        return Object.keys(hierarchy[distName]).map((name, i) => ({
                            id: `ac_${distName}_${i}`,
                            name: name,
                            type: 'ASSEMBLY'
                        }));
                    }
                } else if (level === 'block') {
                    // parentId is Assembly Name
                    // Find the AC in the hierarchy
                    for (const dist in hierarchy) {
                        const acName = Object.keys(hierarchy[dist]).find(a => a.toLowerCase() === parentId.toLowerCase());
                        if (acName) {
                            return Object.keys(hierarchy[dist][acName]).map((name, i) => ({
                                id: `blk_${acName}_${i}`,
                                name: name,
                                type: 'BLOCK'
                            }));
                        }
                    }
                }
            }
        } catch (e) {
            console.warn("Local hierarchy lookup failed", e);
        }

        // 2. Fallback to Backend API
        try {
            const token = localStorage.getItem('token');
            const headers: HeadersInit = token ? { 'Authorization': `Bearer ${token}` } : {};

            const response = await fetch(`/api/geo/children?parentId=${encodeURIComponent(parentId)}&level=${level}`, {
                headers
            });
            if (!response.ok) {
                console.warn("API fetch failed, returning empty");
                return [];
            }
            return await response.json();
        } catch (e) {
            console.error("Failed to fetch children", e);
            return [];
        }
    };

    // Fetch Real Geographic Boundaries from BoundaryService
    const generateChildrenShapes = async (
        parent: GeoFeature,
        childType: 'ASSEMBLY' | 'BLOCK' | 'VILLAGE',
        realData: { id: string, name: string }[]
    ): Promise<GeoFeature[]> => {
        try {
            console.log(`🔍 Fetching ${childType} boundaries for ${parent.name} (type: ${parent.type})`);

            // Attempt to fetch real boundary data
            let boundaryData = null;

            if (childType === 'ASSEMBLY') {
                // Fetch Assembly Constituencies (Vidhan Sabha) for this district
                boundaryData = await BoundaryService.fetchDistrictAssemblies(parent.name);
            } else if (childType === 'BLOCK') {
                // For blocks, we need the DISTRICT name, not the Assembly name
                // Walk back through history to find the district
                const districtName = history.find(h => h.type === 'DISTRICT')?.name || parent.name;
                console.log(`🔍 Fetching blocks for district: ${districtName}`);
                boundaryData = await BoundaryService.fetchDistrictBlocks(districtName);
            } else if (childType === 'VILLAGE') {
                // Fetch villages as POINTS (not polygons)
                boundaryData = await BoundaryService.fetchBlockVillages(parent.name);
            }

            // If we got real GeoJSON boundaries, convert them to our GeoFeature format
            if (boundaryData && boundaryData.features.length > 0) {
                // Filter blocks to only show those within the selected Assembly
                let filteredBoundaries = boundaryData;

                if (childType === 'BLOCK' && parent.type === 'ASSEMBLY') {
                    // Load hierarchy data to determine which blocks are in this AC
                    const hierarchy = await BoundaryService.loadHierarchyData();
                    const districtName = history.find(h => h.type === 'DISTRICT')?.name || parent.name; // This might be tricky if parent is AC.
                    // Actually, if parent is AC, we need to know which District it belongs to.
                    // In handleSelect, we push to history. So if we are at AC level, history has District.
                    // But wait, 'parent' passed to generateChildrenShapes IS the AC feature.
                    // And 'history' contains the path.

                    // Let's find district name safely
                    const districtFeature = history.find(h => h.type === 'DISTRICT');
                    const distName = districtFeature ? districtFeature.name : null;

                    if (hierarchy && distName && hierarchy[distName] && hierarchy[distName][parent.name]) {
                        // The hierarchy directly lists blocks under the AC
                        const blocksInAC = Object.keys(hierarchy[distName][parent.name]);
                        const blocksSet = new Set(blocksInAC.map(b => b.toLowerCase()));

                        filteredBoundaries = {
                            type: 'FeatureCollection',
                            features: boundaryData.features.filter(f =>
                                blocksSet.has(f.properties.name.toLowerCase()) ||
                                blocksInAC.some(b => f.properties.name.toLowerCase().includes(b.toLowerCase()))
                            )
                        };
                        console.log(`🔍 Filtered to ${filteredBoundaries.features.length} blocks in ${parent.name} using LGD Hierarchy`);
                    }
                }

                // Use the same projection as the parent map
                const projection = d3.geoMercator()
                    .center([82.4, 21.2])
                    .scale(6000)
                    .translate([500, 500]);

                const pathGenerator = d3.geoPath().projection(projection);

                const children: GeoFeature[] = filteredBoundaries.features.map((feature, i) => {
                    // Handle Point geometries differently (villages)
                    if (feature.geometry.type === 'Point') {
                        const coords = projection(feature.geometry.coordinates as [number, number]);
                        if (!coords) {
                            return null;
                        }

                        return {
                            id: feature.properties.id,
                            name: feature.properties.name,
                            type: childType,
                            path: `M ${coords[0] - 2},${coords[1] - 2} L ${coords[0] + 2},${coords[1] - 2} L ${coords[0] + 2},${coords[1] + 2} L ${coords[0] - 2},${coords[1] + 2} Z`, // Small square for point
                            bounds: {
                                x: coords[0] - 2,
                                y: coords[1] - 2,
                                w: 4,
                                h: 4
                            },
                            color: '#10b981' // Green for villages
                        };
                    }

                    // Handle Polygon/MultiPolygon (AC, blocks)
                    const bounds = pathGenerator.bounds(feature);
                    const svgPath = pathGenerator(feature) || "";

                    return {
                        id: feature.properties.id,
                        name: feature.properties.name,
                        type: childType,
                        path: svgPath,
                        bounds: {
                            x: bounds[0][0],
                            y: bounds[0][1],
                            w: bounds[1][0] - bounds[0][0],
                            h: bounds[1][1] - bounds[0][1]
                        },
                        color: childType === 'ASSEMBLY' ? '#f59e0b' : childType === 'BLOCK' ? '#8b5cf6' : '#10b981'
                    };
                }).filter((f): f is GeoFeature => f !== null);

                console.log(`✅ Loaded ${children.length} real ${childType} boundaries for ${parent.name}`);
                return children;
            }

            // FALLBACK: If API fails or no data, use procedural generation
            console.warn(`⚠️ No real boundary data found for ${parent.name}, using procedural generation`);
            return generateProceduralChildren(parent, childType, realData);

        } catch (error) {
            console.error('Error fetching boundaries:', error);
            return generateProceduralChildren(parent, childType, realData);
        }
    };

    // Procedural Fallback (kept for areas without boundary data)
    const generateProceduralChildren = (
        parent: GeoFeature,
        childType: 'ASSEMBLY' | 'BLOCK' | 'VILLAGE',
        realData: { id: string, name: string }[]
    ): GeoFeature[] => {
        const { x, y, w, h } = parent.bounds;

        // If no real data, fallback to procedural count
        const count = realData.length > 0 ? realData.length : (
            childType === 'ASSEMBLY' ? 8 : childType === 'BLOCK' ? 12 : 20
        );

        const cols = Math.ceil(Math.sqrt(count));
        const rows = Math.ceil(count / cols);
        const cellW = w / cols;
        const cellH = h / rows;

        const children: GeoFeature[] = [];

        for (let i = 0; i < count; i++) {
            const r = Math.floor(i / cols);
            const c = i % cols;

            // Add randomness to grid to make it look organic
            const jitter = (val: number) => val + (Math.random() - 0.5) * (
                childType === 'ASSEMBLY' ? cellW * 0.4 : childType === 'BLOCK' ? cellW * 0.5 : cellW * 0.3
            );

            const cx = x + c * cellW + cellW / 2;
            const cy = y + r * cellH + cellH / 2;

            // Create a rough polygon (quadrilateral with jittered corners)
            const p1 = [jitter(x + c * cellW), jitter(y + r * cellH)];
            const p2 = [jitter(x + (c + 1) * cellW), jitter(y + r * cellH)];
            const p3 = [jitter(x + (c + 1) * cellW), jitter(y + (r + 1) * cellH)];
            const p4 = [jitter(x + c * cellW), jitter(y + (r + 1) * cellH)];

            const path = `M ${p1[0]} ${p1[1]} L ${p2[0]} ${p2[1]} L ${p3[0]} ${p3[1]} L ${p4[0]} ${p4[1]} Z`;

            // Use real data if available, otherwise procedural
            const data = realData[i] || {
                id: `${parent.id}_${childType}_${r}_${c}`,
                name: `${childType === 'ASSEMBLY' ? 'AC' : childType === 'BLOCK' ? 'Block' : 'Village'} ${i + 1}`
            };

            children.push({
                id: data.id,
                name: data.name,
                type: childType,
                path: path,
                bounds: {
                    x: x + c * cellW,
                    y: y + r * cellH,
                    w: cellW,
                    h: cellH
                },
                color: childType === 'ASSEMBLY' ? '#f59e0b' : childType === 'BLOCK' ? '#8b5cf6' : '#10b981'
            });
        }
        return children;
    };

    // Handlers
    const handleSelect = async (feature: GeoFeature) => {
        // 1. Determine Next Level (Updated Hierarchy: DISTRICT → ASSEMBLY → BLOCK → VILLAGE)
        let nextLevelType: 'ASSEMBLY' | 'BLOCK' | 'VILLAGE' | null = null;
        let apiLevel: 'district' | 'assembly' | 'block' | null = null;

        if (feature.type === 'DISTRICT') {
            nextLevelType = 'ASSEMBLY'; // Show Vidhan Sabha first
            apiLevel = 'district';
        } else if (feature.type === 'ASSEMBLY') {
            nextLevelType = 'BLOCK'; // Then show blocks
            apiLevel = 'assembly';
        } else if (feature.type === 'BLOCK') {
            nextLevelType = 'VILLAGE'; // Finally show villages as points
            apiLevel = 'block';
        }

        // 2. If Leaf Node (Village), Select and Close
        if (!nextLevelType) {
            onSelect({
                name: feature.name,
                type: feature.type,
                parent: history.length > 0 ? history[history.length - 1].name : null
            });
            onClose();
            return;
        }

        // 3. Generate or Retrieve Children
        let children = feature.children;
        if (!children) {
            setIsLoading(true);
            // Fetch real children from API
            const realChildren = apiLevel ? await fetchChildrenFromApi(feature.name, apiLevel) : [];

            // Generate shapes mapped to real children (await since it's async now)
            children = await generateChildrenShapes(feature, nextLevelType, realChildren);
            feature.children = children; // Cache them
            setIsLoading(false);
        }

        // 4. Zoom Logic
        const padX = feature.bounds.w * 0.4;
        const padY = feature.bounds.h * 0.4;
        const newVB = `
        ${feature.bounds.x - padX / 2}
        ${feature.bounds.y - padY / 2}
        ${feature.bounds.w + padX}
        ${feature.bounds.h + padY}
    `;

        // 5. Update State
        setViewBox(newVB.replace(/\s+/g, ' ').trim());
        setHistory([...history, feature]);
        setCurrentLevelFeatures(children);
    };

    const handleBack = (index: number) => {
        if (index === 0) {
            // Reset to State Level (Chhattisgarh)
            setHistory([]);
            setCurrentLevelFeatures(initialDistricts);
            setViewBox("0 0 1000 1000");
        } else {
            // Go back to a specific level (e.g., District View)
            // index 1 = District Name. We want to keep that district selected and show its children (Blocks).
            const targetFeature = history[index - 1];
            const newHistory = history.slice(0, index);

            setHistory(newHistory);

            // Restore the children of the target feature
            if (targetFeature.children) {
                setCurrentLevelFeatures(targetFeature.children);
            }

            // Zoom to the target feature
            const padX = targetFeature.bounds.w * 0.4;
            const padY = targetFeature.bounds.h * 0.4;
            const newVB = `
                ${targetFeature.bounds.x - padX / 2} 
                ${targetFeature.bounds.y - padY / 2} 
                ${targetFeature.bounds.w + padX} 
                ${targetFeature.bounds.h + padY}
            `;
            setViewBox(newVB.replace(/\s+/g, ' ').trim());
        }
    };

    const [searchQuery, setSearchQuery] = useState("");

    // Filter features based on search
    const filteredFeatures = useMemo(() => {
        if (!searchQuery) return currentLevelFeatures;
        return currentLevelFeatures.filter(f =>
            f.name.toLowerCase().includes(searchQuery.toLowerCase())
        );
    }, [currentLevelFeatures, searchQuery]);

    return (
        <div className="fixed inset-0 z-[100] bg-slate-950 text-slate-100 font-sans selection:bg-cyan-500/30 flex flex-col">

            {/* 1. BACKGROUND GRID (The "Holodeck" Vibe) */}
            <div className="absolute inset-0 pointer-events-none opacity-40"
                style={{
                    backgroundImage: 'radial-gradient(circle, #1e293b 1px, transparent 1px)',
                    backgroundSize: '40px 40px'
                }}
            />

            {/* Close Button */}
            <button
                onClick={onClose}
                className="absolute top-6 right-6 z-50 p-2 bg-slate-900/50 hover:bg-slate-800 rounded-full text-slate-400 hover:text-white transition-colors border border-white/10"
            >
                <X size={24} />
            </button>

            {/* 2. THE COSMIC MAP (Rendering Engine) */}
            <motion.svg
                className="w-full h-full filter drop-shadow-[0_0_20px_rgba(6,182,212,0.3)]" // Added Map Glow
                viewBox="0 0 1000 1000"
                animate={{ viewBox: viewBox }}
                transition={{
                    type: "spring",
                    stiffness: 120, // Tension of the spring
                    damping: 14,    // Friction (prevents wobbling)
                    mass: 1         // Weight of the camera
                }}
            >
                <defs>
                    <filter id="neon-glow" x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur stdDeviation="5" result="coloredBlur" />
                        <feMerge>
                            <feMergeNode in="coloredBlur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>

                {/* LAYER 1: The Parent (Ghost Map) */}
                <AnimatePresence>
                    {activeFeature && (
                        <motion.path
                            key="parent-ghost"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 0.15 }}
                            exit={{ opacity: 0 }}
                            d={activeFeature.path}
                            style={{ vectorEffect: 'non-scaling-stroke' }}
                            className="fill-none stroke-cyan-500 stroke-[1px]"
                        />
                    )}
                </AnimatePresence>

                {/* LAYER 2: The Active Children */}
                <AnimatePresence mode='wait'>
                    {filteredFeatures.map((feature, i) => (
                        <motion.g
                            key={feature.id}
                            initial={{ opacity: 0, scale: 0.8, translateY: 20 }}
                            animate={{ opacity: 1, scale: 1, translateY: 0 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            transition={{ duration: 0.5, delay: i * 0.02 }} // Faster stagger
                            onMouseEnter={() => setIsHovering(feature.id)}
                            onMouseLeave={() => setIsHovering(null)}
                            onClick={() => handleSelect(feature)}
                            className="cursor-pointer"
                        >
                            <motion.path
                                d={feature.path}
                                style={{ vectorEffect: 'non-scaling-stroke' }}
                                className={clsx(
                                    "transition-all duration-300",
                                    isHovering === feature.id
                                        ? "fill-cyan-500/20 stroke-cyan-400 stroke-[2px]"
                                        : "fill-slate-800/50 stroke-slate-600 stroke-[1px]"
                                )}
                                filter={isHovering === feature.id ? "url(#neon-glow)" : undefined}
                            />
                        </motion.g>
                    ))}
                </AnimatePresence>
            </motion.svg>

            {/* 3. HEADS UP DISPLAY (HUD) */}

            {/* Top: Search & Coordinates */}
            <div className="absolute top-6 left-1/2 -translate-x-1/2 w-full max-w-lg px-4 pointer-events-none">
                <div className="relative group pointer-events-auto">
                    <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
                        <Search className="w-5 h-5 text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
                    </div>
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="ज़िला, विकासखंड या गाँव खोजें..."
                        className="w-full bg-slate-900/80 backdrop-blur-md border border-slate-700 rounded-full py-3 pl-12 pr-4 text-slate-200 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all shadow-lg shadow-black/50 font-hindi"
                    />
                    <div className="absolute inset-y-0 right-3 flex items-center gap-2">
                        <LocateFixed className="w-4 h-4 text-cyan-500 animate-pulse" />
                        <span className="text-xs text-slate-400 font-mono">21.25° N</span>
                    </div>
                </div>
            </div>

            {/* Bottom: Pilot Controls & Breadcrumbs */}
            <div className="absolute bottom-8 left-0 right-0 flex justify-center px-4 pointer-events-none">
                <motion.div
                    className="bg-slate-900/90 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-4 shadow-2xl shadow-cyan-900/10 max-w-3xl w-full flex flex-col gap-3 pointer-events-auto"
                    initial={{ y: 100, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                >
                    {/* Status Line / Target Info */}
                    <div className="flex justify-between items-center border-b border-slate-800 pb-2 min-h-[32px]">
                        {isHovering ? (
                            <div className="flex items-center gap-2 animate-in fade-in slide-in-from-bottom-2 duration-200">
                                <span className="text-cyan-400 font-mono text-xs uppercase tracking-widest">TARGET:</span>
                                <span className="text-lg font-bold text-white font-hindi tracking-wide drop-shadow-[0_0_10px_rgba(6,182,212,0.5)]">
                                    {currentLevelFeatures.find(f => f.id === isHovering)?.name}
                                </span>
                            </div>
                        ) : (
                            <div className="flex items-center gap-2 text-xs font-mono text-cyan-500">
                                <Globe className="w-3 h-3 animate-pulse" />
                                <span className="font-hindi">उपग्रह संपर्क स्थापित</span>
                            </div>
                        )}

                        <div className="text-xs text-slate-500 font-hindi">
                            ऊंचाई: {
                                history.length === 0 ? '१२० किमी' :
                                    history.length === 1 ? '६० किमी' :  // District
                                        history.length === 2 ? '३० किमी' :  // Assembly
                                            history.length === 3 ? '१० किमी' :  // Block
                                                '२ किमी'  // Village
                            }
                        </div>
                    </div>

                    {/* Breadcrumb Time-Travel Bar */}
                    <div className="flex items-center gap-2 overflow-x-auto no-scrollbar py-1">
                        {breadcrumbs.map((crumb, index) => (
                            <React.Fragment key={index}>
                                <button
                                    onClick={() => handleBack(index)}
                                    className={cn(
                                        "px-3 py-1.5 rounded-md text-sm font-medium transition-all flex-shrink-0 font-hindi",
                                        index === breadcrumbs.length - 1
                                            ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-[0_0_10px_rgba(6,182,212,0.2)]"
                                            : "text-slate-500 hover:text-slate-300 hover:bg-slate-800"
                                    )}
                                >
                                    {crumb}
                                </button>
                                {index < breadcrumbs.length - 1 && (
                                    <ChevronRight className="w-4 h-4 text-slate-700 flex-shrink-0" />
                                )}
                            </React.Fragment>
                        ))}
                    </div>

                    {/* Context Actions */}
                    <div className="flex justify-between items-center pt-1">
                        <button
                            onClick={() => onSelect(null)}
                            className="text-xs text-red-400 hover:text-red-300 flex items-center gap-1 transition-colors font-hindi group"
                        >
                            <X className="w-3 h-3 group-hover:animate-pulse" />
                            कोई संकेत नहीं (लागू नहीं)
                        </button>

                        {activeFeature && (
                            <button
                                onClick={() => handleBack(0)}
                                className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-md flex items-center gap-2 transition-all font-hindi"
                            >
                                <Navigation className="w-3 h-3" />
                                केंद्र पर जाएं
                            </button>
                        )}
                    </div>

                </motion.div>
            </div>

            {/* Loading Overlay - Show when fetching boundary data */}
            {isLoading && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center z-50"
                >
                    <div className="flex flex-col items-center gap-4">
                        <div className="w-16 h-16 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin" />
                        <p className="text-cyan-400 font-hindi text-lg animate-pulse">
                            मानचित्र डेटा लोड हो रहा है...
                        </p>
                    </div>
                </motion.div>
            )}

        </div>
    );
}
