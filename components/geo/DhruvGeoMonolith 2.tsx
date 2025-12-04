import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, ChevronLeft, MapPin, Layers } from 'lucide-react';
import '../../styles/monolith.css';

interface BreadcrumbItem {
    level: 'state' | 'district' | 'assembly' | 'block' | 'village';
    name: string;
    id: string;
}

interface DhruvGeoMonolithProps {
    onLocationSelect?: (location: any) => void;
    initialState?: string;
}

/**
 * Dhruv Geo-Monolith
 * A vertical, cinematic location selector with Obsidian Glass aesthetic
 * Designed to feel like a premium mobile app interface
 */
export const DhruvGeoMonolith: React.FC<DhruvGeoMonolithProps> = ({
    onLocationSelect,
    initialState = 'Chhattisgarh'
}) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [breadcrumbs, setBreadcrumbs] = useState<BreadcrumbItem[]>([
        { level: 'state', name: 'छत्तीसगढ़', id: 'chhattisgarh' }
    ]);
    const [zoomLevel, setZoomLevel] = useState(1); // 1=State, 2=District, 3=Assembly, 4=Block, 5=Village
    const [selectedLocation, setSelectedLocation] = useState<any>(null);
    const [isOnline, setIsOnline] = useState(true);

    // System status check
    useEffect(() => {
        const checkStatus = setInterval(() => {
            setIsOnline(navigator.onLine);
        }, 3000);
        return () => clearInterval(checkStatus);
    }, []);

    const handleBreadcrumbClick = (index: number) => {
        const newBreadcrumbs = breadcrumbs.slice(0, index + 1);
        setBreadcrumbs(newBreadcrumbs);
        setZoomLevel(index + 1);
    };

    const handleLocationClick = (location: any) => {
        // Add to breadcrumbs and zoom in
        const newItem: BreadcrumbItem = {
            level: location.type,
            name: location.name,
            id: location.id,
        };
        setBreadcrumbs([...breadcrumbs, newItem]);
        setZoomLevel(zoomLevel + 1);
        setSelectedLocation(location);

        if (onLocationSelect) {
            onLocationSelect(location);
        }
    };

    const handleBack = () => {
        if (breadcrumbs.length > 1) {
            const newBreadcrumbs = breadcrumbs.slice(0, -1);
            setBreadcrumbs(newBreadcrumbs);
            setZoomLevel(zoomLevel - 1);
        }
    };

    return (
        // 1. CONTAINER: Dark Void with Scanner Grid
        <div className="fixed inset-0 bg-[#020408] flex items-center justify-center p-4 overflow-hidden scanner-grid">

            {/* 2. THE MONOLITH: Vertical Aspect Ratio */}
            <motion.div
                initial={{ y: 20, opacity: 0, scale: 0.98 }}
                animate={{ y: 0, opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                className="relative w-full max-w-[420px] h-[85vh] glass-panel rounded-[32px] overflow-hidden flex flex-col shadow-2xl"
            >

                {/* HEADER: System Status */}
                <div className="absolute top-0 left-0 right-0 z-20 p-6 gradient-overlay-top">
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="flex justify-between items-center mb-1"
                    >
                        <span className="text-[10px] tracking-[0.2em] text-cyan-500/60 uppercase font-mono">
                            Dhruv System v4.0
                        </span>
                        <div className="flex gap-2 items-center">
                            <div className={`w-1.5 h-1.5 rounded-full ${isOnline ? 'bg-emerald-500 status-online' : 'bg-red-500'}`} />
                            <span className={`text-[10px] font-bold font-mono ${isOnline ? 'text-emerald-500' : 'text-red-500'}`}>
                                {isOnline ? 'ONLINE' : 'OFFLINE'}
                            </span>
                        </div>
                    </motion.div>

                    <motion.h1
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 }}
                        className="text-2xl font-bold text-white font-hindi text-neon-strong"
                    >
                        स्थान चयन
                    </motion.h1>

                    {/* Zoom Level Indicator */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.4 }}
                        className="flex items-center gap-2 mt-2"
                    >
                        <Layers className="w-3 h-3 text-cyan-500/60" />
                        <span className="text-[10px] text-cyan-500/60 font-mono">
                            ZOOM: {zoomLevel}/5
                        </span>
                    </motion.div>
                </div>

                {/* MAP VIEWPORT: Takes full height behind UI */}
                <div className="map-viewport">
                    {/* Placeholder for actual map component */}
                    <div className="w-full h-full flex items-center justify-center">
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            transition={{ delay: 0.5 }}
                            className="text-center"
                        >
                            <MapPin className="w-16 h-16 text-cyan-500/30 mx-auto mb-4" />
                            <p className="text-cyan-500/50 text-sm font-mono">
                                Map Component Here
                            </p>
                            <p className="text-cyan-500/30 text-xs font-mono mt-2">
                                {breadcrumbs[breadcrumbs.length - 1]?.name}
                            </p>
                        </motion.div>
                    </div>
                </div>

                {/* FOOTER CONTROLS: Floating at bottom */}
                <div className="absolute bottom-0 left-0 right-0 z-20 p-6 gradient-overlay-bottom">

                    {/* Search Input - Glass Pill */}
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.6 }}
                        className="relative group mb-4"
                    >
                        <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                            <Search className="w-4 h-4 text-cyan-500/70" />
                        </div>
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="खोजें (Search)..."
                            className="w-full glass-input rounded-2xl py-4 pl-12 pr-4 text-white placeholder:text-slate-500 font-hindi text-sm"
                        />
                        {searchQuery && (
                            <button
                                onClick={() => setSearchQuery('')}
                                className="absolute inset-y-0 right-4 flex items-center text-cyan-500/50 hover:text-cyan-500"
                            >
                                ×
                            </button>
                        )}
                    </motion.div>

                    {/* Breadcrumbs / Navigation */}
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.7 }}
                        className="flex gap-2 overflow-x-auto no-scrollbar pb-2"
                    >
                        {breadcrumbs.length > 1 && (
                            <button
                                onClick={handleBack}
                                className="chip-glass rounded-full px-3 py-2 flex items-center gap-2 flex-shrink-0"
                            >
                                <ChevronLeft className="w-4 h-4 text-cyan-400" />
                                <span className="text-xs text-cyan-400 font-medium">Back</span>
                            </button>
                        )}

                        <AnimatePresence>
                            {breadcrumbs.map((item, index) => (
                                <motion.button
                                    key={item.id}
                                    initial={{ scale: 0, opacity: 0 }}
                                    animate={{ scale: 1, opacity: 1 }}
                                    exit={{ scale: 0, opacity: 0 }}
                                    transition={{ delay: index * 0.05 }}
                                    onClick={() => handleBreadcrumbClick(index)}
                                    className={`chip-glass rounded-full px-4 py-2 flex-shrink-0 ${index === breadcrumbs.length - 1
                                        ? 'border-cyan-500 bg-cyan-500/20'
                                        : 'opacity-60 hover:opacity-100'
                                        }`}
                                >
                                    <span className="text-xs text-white font-hindi font-medium">
                                        {item.name}
                                    </span>
                                </motion.button>
                            ))}
                        </AnimatePresence>
                    </motion.div>

                    {/* Level Label */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.8 }}
                        className="mt-3 text-center"
                    >
                        <span className="text-[10px] text-cyan-500/40 uppercase tracking-wider font-mono">
                            {breadcrumbs[breadcrumbs.length - 1]?.level || 'state'}
                        </span>
                    </motion.div>
                </div>

                {/* Corner Accent Lines (Cyberpunk Touch) */}
                <div className="absolute top-0 left-0 w-16 h-16 border-t-2 border-l-2 border-cyan-500/20 rounded-tl-[32px] pointer-events-none" />
                <div className="absolute top-0 right-0 w-16 h-16 border-t-2 border-r-2 border-cyan-500/20 rounded-tr-[32px] pointer-events-none" />
                <div className="absolute bottom-0 left-0 w-16 h-16 border-b-2 border-l-2 border-cyan-500/20 rounded-bl-[32px] pointer-events-none" />
                <div className="absolute bottom-0 right-0 w-16 h-16 border-b-2 border-r-2 border-cyan-500/20 rounded-br-[32px] pointer-events-none" />
            </motion.div>

            {/* Ambient Glow Effect */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-500/5 rounded-full blur-3xl" />
            </div>
        </div>
    );
};

export default DhruvGeoMonolith;
