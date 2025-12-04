import { motion } from 'framer-motion';

interface Location {
    id: string;
    name: string;
    type: string;
    lat: number;
    lon: number;
}

interface LocationFeedProps {
    locations: Location[];
    onSelect: (location: Location) => void;
    selectedId?: string;
}

export default function LocationFeed({ locations, onSelect, selectedId }: LocationFeedProps) {
    return (
        <div className="w-80 bg-black/80 backdrop-blur-md border-r border-indigo-500/30 h-full flex flex-col pointer-events-auto">
            <div className="p-4 border-b border-indigo-500/30">
                <h2 className="text-indigo-400 font-bold tracking-wider text-sm uppercase flex items-center gap-2">
                    <span className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse" />
                    Location Identifier
                </h2>
            </div>

            <div className="flex-1 overflow-y-auto p-2 space-y-2">
                {locations.map((loc) => (
                    <button
                        key={loc.id}
                        onClick={() => onSelect(loc)}
                        className={`w-full text-left p-3 rounded-lg border transition-all duration-300 group
                            ${selectedId === loc.id
                                ? 'bg-indigo-500/20 border-indigo-400 text-white shadow-[0_0_15px_rgba(99,102,241,0.3)]'
                                : 'bg-zinc-900/50 border-zinc-800 text-zinc-400 hover:border-indigo-500/50 hover:text-indigo-300'
                            }`}
                    >
                        <div className="flex justify-between items-center">
                            <span className="font-medium">{loc.name}</span>
                            <span className="text-[10px] uppercase tracking-widest opacity-60">{loc.type}</span>
                        </div>
                        <div className="mt-1 flex items-center gap-2 text-[10px] font-mono opacity-50">
                            <span>LAT: {loc.lat.toFixed(4)}</span>
                            <span>LON: {loc.lon.toFixed(4)}</span>
                        </div>
                    </button>
                ))}
            </div>
        </div>
    );
}
