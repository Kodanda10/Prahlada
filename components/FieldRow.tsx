import React, { useState } from 'react';
import { Pencil, Check, X, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import Chip from './Chip';
import { translateToHindi } from '../utils/textUtils';

interface FieldComparison {
    parser: { value: any; confidence: number; source?: string };
    llm: { value: any; confidence: number; source?: string };
    conflict: boolean;
}

interface FieldRowProps {
    fieldKey: string;
    label: string;
    comparison: FieldComparison;
    selected?: 'parser' | 'llm';
    onSelect: (source: 'parser' | 'llm') => void;
    onManualEdit: (value: any) => void;
    isMobile: boolean;
    activeTab: 'parser' | 'llm';
}

const FieldRow: React.FC<FieldRowProps> = ({
    fieldKey,
    label,
    comparison,
    selected,
    onSelect,
    onManualEdit,
    isMobile,
    activeTab
}) => {
    const [editingSource, setEditingSource] = useState<'parser' | 'llm' | null>(null);
    const [editValue, setEditValue] = useState('');

    // Helper to normalize value into an array of strings/objects for Chip rendering
    const normalizeToChips = (value: any): string[] => {
        let rawChips: string[] = [];

        if (Array.isArray(value)) {
            rawChips = value.map(item => {
                if (typeof item === 'object' && item !== null) {
                    if (item.name) return item.name;
                    if (item.label) return item.label;
                    if (item.canonical) return item.canonical;
                    return JSON.stringify(item);
                }
                return String(item);
            });
        } else if (typeof value === 'object' && value !== null) {
            // Handle specific AI Location structure
            if (value.resolved && typeof value.resolved === 'object') {
                const res = value.resolved;
                const locName = res.canonical || res.name || res.ulb || res.village || res.district || res.state;
                if (locName) rawChips = [locName];
            } else if (value.inferred && Array.isArray(value.inferred) && value.inferred.length > 0) {
                rawChips = value.inferred;
            } else if ('district' in value || 'hierarchy_path' in value) {
                const parts = [
                    value.district, value.assembly, value.ulb,
                    value.block, value.gp, value.village, value.ward
                ].filter(Boolean);
                if (parts.length > 0) rawChips = parts;
                else if (value.hierarchy_path && Array.isArray(value.hierarchy_path)) rawChips = value.hierarchy_path;
            } else if (value.canonical) rawChips = [value.canonical];
            else if (value.name) rawChips = [value.name];
            else {
                const possibleName = value.name || value.label || value.text || value.value;
                if (possibleName) rawChips = [possibleName];
                else rawChips = [JSON.stringify(value)];
            }
        } else if (!value) {
            rawChips = [];
        } else {
            rawChips = [String(value)];
        }

        // Translate all chips to Hindi
        return rawChips.map(chip => translateToHindi(chip));
    };

    const handleChipRemove = (e: React.MouseEvent, source: 'parser' | 'llm', chipIndex: number, currentValue: any) => {
        e.stopPropagation();
        const chips = normalizeToChips(currentValue);
        const newChips = chips.filter((_, i) => i !== chipIndex);
        onManualEdit(newChips);
    };

    const handleChipEdit = (source: 'parser' | 'llm', chipIndex: number, currentValue: any, newValue: string) => {
        const chips = normalizeToChips(currentValue);
        const newChips = [...chips];
        newChips[chipIndex] = newValue;
        onManualEdit(newChips);
    };

    const handleStartEdit = (e: React.MouseEvent, source: 'parser' | 'llm', value: any) => {
        e.stopPropagation();
        setEditingSource(source);
        setEditingSource(source);
        // Use normalized chips for editing to ensure Hindi text is shown
        const chips = normalizeToChips(value);
        const strVal = chips.join(', ');
        setEditValue(strVal);
        onSelect(source);
    };

    const handleSaveEdit = (e: React.MouseEvent) => {
        e.stopPropagation();
        const finalVal = editValue.includes(',')
            ? editValue.split(',').map(s => s.trim()).filter(Boolean)
            : editValue;

        onManualEdit(finalVal);
        setEditingSource(null);
    };

    const handleCancelEdit = (e: React.MouseEvent) => {
        e.stopPropagation();
        setEditingSource(null);
    };

    const renderField = (source: 'parser' | 'llm', data: any) => {
        const isSelected = selected === source;
        const isEditing = editingSource === source;
        const colorClass = source === 'parser' ? 'cyan' : 'violet';
        const chips = normalizeToChips(data.value);

        return (
            <motion.div
                layout
                data-field={fieldKey}
                data-source={source}
                className={`
                  relative p-3 rounded-xl border transition-all cursor-pointer group
                  ${isSelected
                        ? `bg-${colorClass}-500/10 border-${colorClass}-500/40 shadow-[0_0_20px_rgba(var(--${colorClass}-500),0.15)]`
                        : 'bg-white/5 border-white/5 hover:bg-white/10 hover:border-white/10'
                    }
                `}
                onClick={() => !isEditing && onSelect(source)}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
            >
                {/* Header Indicator */}
                <div className={`absolute top-0 left-0 w-1 h-full rounded-l-xl transition-colors ${isSelected ? `bg-${colorClass}-500` : 'bg-transparent'}`} />

                <div className="flex items-center justify-between mb-2 pl-2">
                    <span className={`text-[10px] font-bold uppercase tracking-wider ${source === 'parser' ? 'text-cyan-400' : 'text-violet-400'} opacity-60`}>
                        {source === 'parser' ? 'PARSER' : 'AI'}
                    </span>

                    <div className="flex items-center gap-2">
                        {!isEditing && isSelected && (
                            <button
                                onClick={(e) => handleStartEdit(e, source, data.value)}
                                className="p-1.5 hover:bg-white/10 rounded-full text-slate-400 hover:text-white transition-colors opacity-0 group-hover:opacity-100"
                                title="Edit manually"
                            >
                                <Pencil size={12} />
                            </button>
                        )}
                        <div className={`
                            w-4 h-4 rounded-full border-2 flex items-center justify-center transition-all
                            ${isSelected
                                ? `border-${colorClass}-400 bg-${colorClass}-400 shadow-[0_0_10px_rgba(var(--${colorClass}-400),0.6)]`
                                : 'border-slate-600 bg-transparent group-hover:border-slate-400'
                            }
                        `}>
                            {isSelected && <Check size={10} className="text-black font-bold" />}
                        </div>
                    </div>
                </div>

                {isEditing ? (
                    <div className="relative pl-2">
                        <textarea
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            className="w-full bg-black/50 border border-white/20 rounded-lg p-3 text-sm text-slate-200 font-hindi focus:outline-none focus:border-blue-500 min-h-[80px] font-mono shadow-inner"
                            onClick={(e) => e.stopPropagation()}
                            autoFocus
                        />
                        <div className="flex justify-end gap-2 mt-2">
                            <button onClick={handleCancelEdit} className="p-2 hover:bg-white/10 rounded-lg text-red-400 transition-colors">
                                <X size={16} />
                            </button>
                            <button onClick={handleSaveEdit} className="p-2 hover:bg-white/10 rounded-lg text-green-400 transition-colors">
                                <Check size={16} />
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="pl-2 flex flex-wrap gap-2">
                        {chips.length > 0 ? (
                            chips.map((chip, idx) => (
                                <Chip
                                    key={idx}
                                    label={chip}
                                    color={source === 'parser' ? 'cyan' : 'violet'}
                                    onRemove={(e) => handleChipRemove(e as any, source, idx, data.value)}
                                    onEdit={(newVal) => handleChipEdit(source, idx, data.value, newVal)}
                                    readOnly={!isSelected}
                                />
                            ))
                        ) : (
                            <span className="text-slate-500 text-sm italic">—</span>
                        )}
                    </div>
                )}
            </motion.div>
        );
    };

    if (isMobile) {
        return (
            <div className="mb-6">
                <div className="flex items-center gap-2 mb-3">
                    <span className="text-xs font-bold text-slate-400 font-hindi uppercase tracking-wide">
                        {label}
                    </span>
                    {comparison.conflict && (
                        <AlertTriangle size={14} className="text-amber-500 animate-pulse" />
                    )}
                </div>
                {activeTab === 'parser' && renderField('parser', comparison.parser)}
                {activeTab === 'llm' && renderField('llm', comparison.llm)}
            </div>
        );
    }

    return (
        <div className="mb-6">
            <div className="flex items-center gap-2 mb-3">
                <span className="text-xs font-bold text-slate-400 font-hindi uppercase tracking-wide">
                    {label}
                </span>
                {comparison.conflict && (
                    <AlertTriangle size={14} className="text-amber-500 animate-pulse" />
                )}
            </div>

            <div className="grid grid-cols-2 gap-4">
                {renderField('parser', comparison.parser)}
                {renderField('llm', comparison.llm)}
            </div>
        </div>
    );
};

export default FieldRow;
