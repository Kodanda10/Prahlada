import { useState } from 'react';
import LocationFeed from './LocationFeed';

// Mock data for now - will come from props later
const MOCK_LOCATIONS = [
    { id: 'raipur', name: 'Raipur', type: 'district', lat: 21.2514, lon: 81.6296 },
    { id: 'bilaspur', name: 'Bilaspur', type: 'district', lat: 22.0797, lon: 82.1409 },
    { id: 'durg', name: 'Durg', type: 'district', lat: 21.1904, lon: 81.2849 },
    { id: 'korba', name: 'Korba', type: 'district', lat: 22.3595, lon: 82.7501 },
    { id: 'jagdalpur', name: 'Jagdalpur', type: 'district', lat: 19.0743, lon: 82.0098 },
];

export default function UI({ breadcrumbs, onBreadcrumbClick }: any) {
    const [selectedLoc, setSelectedLoc] = useState<string | null>(null);

    return (
        <div className="absolute inset-0 pointer-events-none flex flex-col justify-between">
            {/* Header */}
            <header className="p-4 pointer-events-auto flex justify-between items-start">
                <div className="container mx-auto flex justify-between items-center text-white">
                    <button className="material-symbols-outlined text-3xl hover:text-indigo-400 transition-colors">
                        arrow_back_ios
                    </button>
                    <div className="flex flex-col items-center">
                        <span className="text-lg font-bold tracking-wider text-indigo-400 drop-shadow-[0_0_10px_rgba(99,102,241,0.5)]">
                            PROJECT DHRUV
                        </span>
                        {breadcrumbs.length > 0 && (
                            <div className="flex items-center text-xs text-indigo-300 mt-1">
                                {breadcrumbs.map((crumb: string, index: number) => (
                                    <span key={index} className="flex items-center">
                                        <button onClick={() => onBreadcrumbClick(index)} className="hover:underline">
                                            {crumb}
                                        </button>
                                        {index < breadcrumbs.length - 1 && <span className="mx-1">›</span>}
                                    </span>
                                ))}
                            </div>
                        )}
                    </div>
                    <button className="material-symbols-outlined text-3xl hover:text-indigo-400 transition-colors">
                        more_horiz
                    </button>
                </div>
            </header>

            {/* Main Content Area */}
            <div className="flex-1 flex relative">
                {/* Left Sidebar: Location Feed */}
                <div className="absolute left-0 top-0 bottom-0 z-10">
                    <LocationFeed
                        locations={MOCK_LOCATIONS}
                        onSelect={(loc) => setSelectedLoc(loc.id)}
                        selectedId={selectedLoc || undefined}
                    />
                </div>
            </div>

            {/* Footer */}
            <footer className="p-6 pointer-events-auto">
                <div className="container mx-auto flex justify-around items-center bg-zinc-900/80 backdrop-blur-md rounded-full py-3 px-4 text-zinc-400 border border-zinc-800 shadow-[0_0_20px_rgba(0,0,0,0.5)]">
                    <a href="#" className="flex flex-col items-center text-indigo-400 drop-shadow-[0_0_5px_rgba(99,102,241,0.5)]">
                        <span className="material-symbols-outlined text-2xl">public</span>
                        <span className="text-[10px] font-medium mt-1">Globe</span>
                    </a>
                    <a href="#" className="flex flex-col items-center hover:text-white transition-colors">
                        <span className="material-symbols-outlined text-2xl">explore</span>
                        <span className="text-[10px] mt-1">Explore</span>
                    </a>
                    <a href="#" className="flex flex-col items-center hover:text-white transition-colors">
                        <span className="material-symbols-outlined text-2xl">bookmarks</span>
                        <span className="text-[10px] mt-1">Saved</span>
                    </a>
                    <a href="#" className="flex flex-col items-center hover:text-white transition-colors">
                        <span className="material-symbols-outlined text-2xl">person</span>
                        <span className="text-[10px] mt-1">Profile</span>
                    </a>
                </div>
            </footer>
        </div>
    );
}
