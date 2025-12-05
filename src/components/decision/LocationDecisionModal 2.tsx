import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ChevronRight, MapPin, Search, CheckCircle2 } from 'lucide-react';
import { BoundaryService } from '../../services/BoundaryService';

interface LocationDecisionModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSelect: (locationData: any) => void;
    initialLocation?: any;
}

type Step = 'DISTRICT' | 'ASSEMBLY' | 'BLOCK' | 'VILLAGE';

interface LocationState {
    district: string | null;
    assembly: string | null;
    block: string | null;
    village: string | null;
}

export default function LocationDecisionModal({ isOpen, onClose, onSelect, initialLocation }: LocationDecisionModalProps) {
    const [step, setStep] = useState<Step>('DISTRICT');
    const [selections, setSelections] = useState<LocationState>({
        district: null,
        assembly: null,
        block: null,
        village: null
    });
    const [loading, setLoading] = useState(false);
    const [items, setItems] = useState<string[]>([]); // Current list of items to show (Districts, ACs, etc.)
    const [searchQuery, setSearchQuery] = useState('');

    // Load initial data (Districts)
    useEffect(() => {
        if (isOpen) {
            loadDistricts();
        }
    }, [isOpen]);

    const loadDistricts = async () => {
        setLoading(true);
        try {
            const hierarchy = await BoundaryService.loadHierarchyData();
            if (hierarchy) {
                setItems(Object.keys(hierarchy).sort());
            }
        } catch (error) {
            console.error("Failed to load districts", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSelection = async (item: string) => {
        if (step === 'DISTRICT') {
            setSelections(prev => ({ ...prev, district: item }));
            // Load Assemblies for this district
            setLoading(true);
            try {
                const hierarchy = await BoundaryService.loadHierarchyData();
                if (hierarchy && hierarchy[item]) {
                    setItems(Object.keys(hierarchy[item]).sort());
                    setStep('ASSEMBLY');
                    setSearchQuery('');
                }
            } catch (e) { console.error(e); } finally { setLoading(false); }

        } else if (step === 'ASSEMBLY') {
            setSelections(prev => ({ ...prev, assembly: item }));
            // Load Blocks for this AC
            setLoading(true);
            try {
                const hierarchy = await BoundaryService.loadHierarchyData();
                const dist = selections.district;
                if (hierarchy && dist && hierarchy[dist][item]) {
                    setItems(Object.keys(hierarchy[dist][item]).sort());
                    setStep('BLOCK');
                    setSearchQuery('');
                }
            } catch (e) { console.error(e); } finally { setLoading(false); }

        } else if (step === 'BLOCK') {
            setSelections(prev => ({ ...prev, block: item }));
            // Load Villages for this Block
            setLoading(true);
            try {
                const hierarchy = await BoundaryService.loadHierarchyData();
                const dist = selections.district;
                const ac = selections.assembly;
                if (hierarchy && dist && ac && hierarchy[dist][ac][item]) {
                    setItems(hierarchy[dist][ac][item].sort());
                    setStep('VILLAGE');
                    setSearchQuery('');
                }
            } catch (e) { console.error(e); } finally { setLoading(false); }

        } else if (step === 'VILLAGE') {
            const finalSelections = { ...selections, village: item };
            setSelections(finalSelections);
            onSelect(finalSelections);
            onClose();
        }
    };

    const filteredItems = items.filter(item =>
        item.toLowerCase().includes(searchQuery.toLowerCase())
    );

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-[200] flex items-center justify-center p-4">
                {/* Backdrop */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                    className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                />

                {/* Modal Container */}
                <motion.div
                    initial={{ scale: 0.9, opacity: 0, y: 20 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    exit={{ scale: 0.9, opacity: 0, y: 20 }}
                    className="relative w-full max-w-4xl bg-[#0f172a] border border-indigo-500/30 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]"
                >
                    {/* Header: Progressive Hierarchy Bar */}
                    <div className="p-6 border-b border-white/10 bg-black/20">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-xl font-bold text-white font-hindi flex items-center gap-2">
                                <MapPin className="text-indigo-400" />
                                स्थान चयन (Location Selection)
                            </h2>
                            <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors">
                                <X className="w-5 h-5 text-slate-400" />
                            </button>
                        </div>

                        {/* Progress Bar */}
                        <div className="flex items-center gap-2 text-sm">
                            {['DISTRICT', 'ASSEMBLY', 'BLOCK', 'VILLAGE'].map((s, i) => {
                                const isActive = step === s;
                                const isCompleted = ['DISTRICT', 'ASSEMBLY', 'BLOCK', 'VILLAGE'].indexOf(step) > i;
                                const label = s === 'DISTRICT' ? 'ज़िला' : s === 'ASSEMBLY' ? 'विधानसभा' : s === 'BLOCK' ? 'विकासखंड' : 'गाँव';
                                const value = s === 'DISTRICT' ? selections.district : s === 'ASSEMBLY' ? selections.assembly : s === 'BLOCK' ? selections.block : selections.village;

                                return (
                                    <div key={s} className="flex items-center">
                                        <div className={`
                                            flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all duration-300
                                            ${isActive ? 'bg-indigo-500/20 border-indigo-500 text-indigo-300 shadow-[0_0_10px_rgba(99,102,241,0.3)]' :
                                                isCompleted ? 'bg-green-500/10 border-green-500/30 text-green-400' :
                                                    'bg-white/5 border-white/10 text-slate-500'}
                                        `}>
                                            {isCompleted ? <CheckCircle2 size={14} /> : <span className="w-3.5 h-3.5 rounded-full border border-current opacity-50" />}
                                            <span className="font-hindi font-medium">{value || label}</span>
                                        </div>
                                        {i < 3 && <div className="w-8 h-[1px] bg-white/10 mx-1" />}
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Search Bar */}
                    <div className="p-4 border-b border-white/5 bg-black/10">
                        <div className="relative">
                            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                            <input
                                type="text"
                                placeholder="खोजें..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full bg-black/20 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white placeholder:text-slate-600 focus:outline-none focus:border-indigo-500/50 transition-all font-hindi"
                            />
                        </div>
                    </div>

                    {/* Content Area: Chips Grid */}
                    <div className="flex-1 overflow-y-auto p-6 custom-scrollbar bg-gradient-to-b from-[#0f172a] to-[#020617]">
                        {loading ? (
                            <div className="flex justify-center items-center h-40">
                                <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                            </div>
                        ) : (
                            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                                {filteredItems.map((item, idx) => (
                                    <motion.button
                                        key={item}
                                        initial={{ opacity: 0, scale: 0.9 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        transition={{ delay: idx * 0.02 }}
                                        onClick={() => handleSelection(item)}
                                        className="
                                            group relative px-4 py-3 rounded-xl text-left transition-all duration-200
                                            bg-white/5 hover:bg-indigo-500/20 border border-white/10 hover:border-indigo-500/50
                                            flex flex-col gap-1
                                        "
                                    >
                                        <span className="text-slate-200 group-hover:text-white font-medium font-hindi">{item}</span>
                                        <span className="text-[10px] text-slate-500 group-hover:text-indigo-300 uppercase tracking-wider">
                                            {step}
                                        </span>
                                    </motion.button>
                                ))}
                            </div>
                        )}
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
}
