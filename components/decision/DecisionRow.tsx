import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, CheckCircle2, HelpCircle, Plus, Sparkles, BrainCircuit, X, Edit2 } from 'lucide-react';
import Chip from '../Chip';
import { translateToHindi } from '../../utils/textUtils';
import GeoNeuroResolver from '../../src/components/decision/GeoNeuroResolver';
import { chipVariants, cardVariants, GEONEURO_THEMES } from '../../src/hooks/useGeoNeuroAnimations';

interface DecisionRowProps {
    label: string;
    subLabel?: string;
    fieldKey: string;
    parserValues: any[];
    aiValues: any[];
    finalValues: any[];
    onUpdateFinal: (values: any[]) => void;
    type?: 'text' | 'person' | 'location' | 'word_bucket';
    isConflict?: boolean;
}

const DecisionRow: React.FC<DecisionRowProps> = ({
    label,
    subLabel,
    fieldKey,
    parserValues,
    aiValues,
    finalValues,
    onUpdateFinal,
    type = 'text',
    isConflict = false
}) => {
    const [isEditing, setIsEditing] = useState(false);
    const [newItemValue, setNewItemValue] = useState('');

    // Normalize values to array of strings (or objects for location)
    const normalize = (val: any): any[] => {
        if (!val) return [];
        if (Array.isArray(val)) return val;
        return [val];
    };

    // Helper to get display label
    const getLabel = (val: any) => {
        if (typeof val === 'string') return translateToHindi(val);
        if (!val) return '';

        // Handle empty object
        if (typeof val === 'object' && Object.keys(val).length === 0) {
            return 'कोई स्थान उल्लेखित नहीं';
        }

        // Handle Location Object
        if (val.district || val.ulb || val.block) {
            const parts = [val.ulb, val.block, val.district, val.state].filter(Boolean);
            return translateToHindi(parts.join(', '));
        }
        // Handle other objects with name or label
        return translateToHindi(val.name || val.label || JSON.stringify(val));
    };

    const pValues = normalize(parserValues);
    const aValues = normalize(aiValues);

    // Determine Status
    let status: 'ok' | 'missing' | 'conflict' | 'edited' = 'ok';
    if (finalValues.length === 0 && pValues.length === 0 && aValues.length === 0) status = 'missing';
    else if (isConflict && finalValues.length === 0) status = 'conflict';
    else if (finalValues.length > 0) status = 'edited'; // Simplified logic, ideally check if matches parser/ai

    const handleAddFromSuggestion = (val: any) => {
        // Avoid duplicates
        if (finalValues.some(v => JSON.stringify(v) === JSON.stringify(val))) return;
        onUpdateFinal([...finalValues, val]);
    };

    const handleRemoveFinal = (index: number) => {
        const newValues = [...finalValues];
        newValues.splice(index, 1);
        onUpdateFinal(newValues);
    };

    const handleEditFinal = (index: number, newVal: string) => {
        const newValues = [...finalValues];
        newValues[index] = newVal; // This assumes string values for now
        onUpdateFinal(newValues);
    };

    const handleAddNew = () => {
        if (newItemValue.trim()) {
            onUpdateFinal([...finalValues, newItemValue.trim()]);
            setNewItemValue('');
            setIsEditing(false);
        }
    };

    const [isLocationModalOpen, setIsLocationModalOpen] = useState(false);

    const handleAdd = () => {
        if (fieldKey === 'location') {
            setIsLocationModalOpen(true);
        } else {
            setIsEditing(true);
        }
    };

    // Handle location selection from GeoNeuroResolver
    const handleLocationSelect = (locationData: any) => {
        if (!locationData) {
            // Handle "Not Applicable"
            onUpdateFinal([]);
        } else {
            // Convert GeoNeuroResolver format to our location format
            const isUrban = locationData.areaType === 'URBAN';
            const locationObj = {
                district: locationData.district,
                assembly: locationData.vidhansabha,
                block: locationData.block,
                village: isUrban ? null : locationData.village,
                gp: isUrban ? null : locationData.gp,
                ulb: isUrban ? locationData.ulb : null,
                ward: locationData.ward,
            };
            onUpdateFinal([locationObj]);
        }
        setIsLocationModalOpen(false);
    };

    return (
        <>
            <div className="grid grid-cols-1 md:grid-cols-[140px_1fr_1fr] gap-4 mb-6 items-stretch group">
                {/* 1. Field Label */}
                <div className="pt-3">
                    <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-bold text-slate-200 font-hindi">{label}</span>
                        {status === 'ok' && <CheckCircle2 size={14} className="text-emerald-500" />}
                        {status === 'missing' && <HelpCircle size={14} className="text-amber-500" />}
                        {status === 'conflict' && <AlertTriangle size={14} className="text-purple-500 animate-pulse" />}
                        {status === 'edited' && <div className="w-2 h-2 rounded-full bg-blue-500" />}
                    </div>
                    {subLabel && <div className="text-[10px] text-slate-500 uppercase tracking-wider font-mono">{subLabel}</div>}
                </div>

                {/* 2. Suggestions Rail */}
                <motion.div
                    className="geoneuro-glass rounded-xl p-3 relative overflow-hidden min-h-[120px] flex flex-col"
                    whileHover={{ scale: 1.01, boxShadow: '0 0 30px rgba(99, 102, 241, 0.15)' }}
                    transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                >
                    <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-cyan-500/50 to-violet-500/50" />

                    {/* Parser Suggestions */}
                    <div className="mb-3 last:mb-0">
                        <div className="flex items-center gap-1.5 mb-2 text-[10px] text-cyan-400 font-bold uppercase tracking-wider opacity-70 font-hindi">
                            <BrainCircuit size={10} /> पार्सर
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {pValues.length > 0 ? pValues.map((val, idx) => (
                                <motion.button
                                    key={`p-${idx}`}
                                    variants={chipVariants}
                                    whileHover="hover"
                                    whileTap="tap"
                                    onClick={() => handleAddFromSuggestion(val)}
                                    className="text-left"
                                >
                                    <Chip
                                        label={getLabel(val)}
                                        color="cyan"
                                        readOnly={true}
                                        className="cursor-pointer hover:ring-1 hover:ring-cyan-400/50"
                                    />
                                </motion.button>
                            )) : <span className="text-slate-600 text-xs italic font-hindi">कोई सुझाव नहीं</span>}
                        </div>
                    </div>

                    {/* AI Suggestions */}
                    <div>
                        <div className="flex items-center gap-1.5 mb-2 text-[10px] text-violet-400 font-bold uppercase tracking-wider opacity-70 font-hindi">
                            <Sparkles size={10} /> एआई
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {aValues.length > 0 ? aValues.map((val, idx) => (
                                <motion.button
                                    key={`a-${idx}`}
                                    variants={chipVariants}
                                    whileHover="hover"
                                    whileTap="tap"
                                    onClick={() => handleAddFromSuggestion(val)}
                                    className="text-left"
                                >
                                    <Chip
                                        label={getLabel(val)}
                                        color="violet"
                                        readOnly={true}
                                        className="cursor-pointer hover:ring-1 hover:ring-violet-400/50"
                                    />
                                </motion.button>
                            )) : <span className="text-slate-600 text-xs italic font-hindi">कोई सुझाव नहीं</span>}
                        </div>
                    </div>
                </motion.div>

                {/* 3. Final Decision Strip - Same GeoNeuro glass theme as Suggestions Rail */}
                <motion.div
                    className={`
                        geoneuro-glass rounded-xl p-4 relative overflow-hidden min-h-[120px] flex flex-col
                        ${finalValues.length > 0
                            ? 'border border-emerald-500/30 shadow-[0_0_20px_rgba(16,185,129,0.1)]'
                            : 'border border-white/10 border-dashed'
                        }
                    `}
                    whileHover={{
                        scale: 1.01,
                        boxShadow: finalValues.length > 0
                            ? '0 0 30px rgba(16, 185, 129, 0.2)'
                            : '0 0 30px rgba(99, 102, 241, 0.15)'
                    }}
                    transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                >
                    {/* Accent bar matching suggestions rail */}
                    <div className={`absolute top-0 right-0 w-1 h-full bg-gradient-to-b ${finalValues.length > 0 ? 'from-emerald-500/50 to-teal-500/50' : 'from-indigo-500/30 to-purple-500/30'}`} />
                    <div className="absolute top-3 right-3 text-[10px] font-bold uppercase tracking-wider text-slate-500 font-hindi">
                        अंतिम निर्णय
                    </div>

                    <div className="flex flex-wrap gap-2 mt-4">
                        <AnimatePresence>
                            {finalValues.map((val, idx) => (
                                <motion.div
                                    key={`f-${idx}`}
                                    initial={{ opacity: 0, scale: 0.8, y: 10 }}
                                    animate={{ opacity: 1, scale: 1, y: 0 }}
                                    exit={{ opacity: 0, scale: 0.8 }}
                                    layout
                                >
                                    <Chip
                                        label={getLabel(val)}
                                        color="emerald"
                                        onRemove={() => handleRemoveFinal(idx)}
                                        onEdit={(newVal) => handleEditFinal(idx, newVal)}
                                    />
                                </motion.div>
                            ))}
                        </AnimatePresence>

                        {/* Add/Edit Button */}
                        {isEditing ? (
                            <div className="flex items-center gap-2 animate-in fade-in slide-in-from-left-2">
                                <input
                                    type="text"
                                    autoFocus
                                    value={newItemValue}
                                    onChange={(e) => setNewItemValue(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleAddNew()}
                                    onBlur={() => { if (!newItemValue) setIsEditing(false); }}
                                    className="bg-black/40 border border-emerald-500/30 rounded-full px-3 py-1.5 text-sm text-white focus:outline-none focus:border-emerald-500 w-32 font-hindi"
                                    placeholder="Add new..."
                                />
                                <button onClick={handleAddNew} className="p-1 rounded-full bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30">
                                    <CheckCircle2 size={14} />
                                </button>
                            </div>
                        ) : (
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={handleAdd}
                                    className={`
                                        px-3 py-1.5 rounded-full border border-dashed border-slate-600 
                                        text-xs text-slate-400 hover:text-white hover:border-slate-400 
                                        hover:bg-white/5 transition-all flex items-center gap-1.5
                                    `}
                                >
                                    {fieldKey === 'location' ? (
                                        <>
                                            <Edit2 size={12} />
                                            <span className="font-hindi">स्थान बदलें</span>
                                        </>
                                    ) : (
                                        <>
                                            <Plus size={12} />
                                            <span className="font-hindi">नया जोड़ें</span>
                                        </>
                                    )}
                                </button>

                                {/* Not Applicable Button for Location */}
                                {fieldKey === 'location' && (
                                    <button
                                        onClick={() => onUpdateFinal([])}
                                        className="px-3 py-1.5 rounded-full border border-dashed border-red-900/50 text-xs text-red-400 hover:text-red-300 hover:bg-red-900/20 transition-all flex items-center gap-1.5"
                                    >
                                        <X size={12} />
                                        <span className="font-hindi">लागू नहीं</span>
                                    </button>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Helper text at bottom - no longer overlapping */}
                    {finalValues.length === 0 && !isEditing && (
                        <div className="text-center pt-3 mt-auto border-t border-white/5">
                            <span className="text-[10px] text-slate-500 font-hindi">
                                ऊपर सुझावों पर क्लिक करें या नया जोड़ें
                            </span>
                        </div>
                    )}
                </motion.div>
            </div >

            {/* GeoNeuroResolver Modal */}
            < GeoNeuroResolver
                isOpen={isLocationModalOpen}
                onClose={() => setIsLocationModalOpen(false)}
                onSelect={handleLocationSelect}
                initialLocation={{
                    district: finalValues[0]?.district || null,
                    vidhansabha: finalValues[0]?.assembly || null,
                    block: finalValues[0]?.block || null,
                    village: finalValues[0]?.village || null,
                    gp: finalValues[0]?.gp || null,
                    ulb: finalValues[0]?.ulb || null,
                    ward: finalValues[0]?.ward || null,
                    areaType: finalValues[0]?.ulb ? 'URBAN' : 'RURAL',
                }}
            />
        </>
    );
};

export default DecisionRow;
