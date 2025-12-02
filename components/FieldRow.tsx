import React, { useState } from 'react';
import { Pencil, Check, X } from 'lucide-react';

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

    const renderValue = (value: any) => {
        if (Array.isArray(value)) {
            return value.join(', ') || '—';
        }
        if (typeof value === 'object' && value !== null) {
            if ('district' in value || 'hierarchy_path' in value) {
                const parts = [
                    value.district, value.assembly, value.ulb,
                    value.block, value.gp, value.village, value.ward
                ].filter(Boolean);

                if (parts.length > 0) return parts.join(' › ');
                if (value.hierarchy_path && Array.isArray(value.hierarchy_path)) {
                    return value.hierarchy_path.join(' › ');
                }
            }
            return JSON.stringify(value);
        }
        return value || '—';
    };

    const handleStartEdit = (e: React.MouseEvent, source: 'parser' | 'llm', value: any) => {
        e.stopPropagation();
        setEditingSource(source);
        // Convert value to string for editing
        let strVal = '';
        if (Array.isArray(value)) strVal = value.join(', ');
        else if (typeof value === 'object') strVal = JSON.stringify(value);
        else strVal = String(value || '');
        setEditValue(strVal);
        onSelect(source); // Auto-select the one being edited
    };

    const handleSaveEdit = (e: React.MouseEvent) => {
        e.stopPropagation();
        // Convert back to array if it looks like a list
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
        const colorClass = source === 'parser' ? 'indigo' : 'pink';

        return (
            <div
                data-field={fieldKey}
                data-source={source}
                className={`
          relative p-3 rounded-lg border transition-all cursor-pointer group backdrop-blur-sm
          ${isSelected
                        ? `bg-gradient-to-br from-${colorClass}-500/10 to-${colorClass}-600/5 border-${colorClass}-500/30`
                        : 'bg-white/5 border-white/5 hover:border-white/20 hover:bg-white/10'
                    }
        `}
                onClick={() => !isEditing && onSelect(source)}
            >
                <div className="flex items-center justify-between mb-2">
                    <span className={`text-[10px] uppercase tracking-wider font-bold font-hindi ${source === 'parser' ? 'text-indigo-300' : 'text-pink-300'}`}>
                        {source === 'parser' ? '🤖 पार्सर' : '🧠 बौद्धिक इंजन'}
                    </span>
                    <div className="flex items-center gap-2">
                        {!isEditing && isSelected && (
                            <button
                                onClick={(e) => handleStartEdit(e, source, data.value)}
                                className="p-1 hover:bg-white/10 rounded text-slate-400 hover:text-white transition-colors"
                                title="Edit manually"
                            >
                                <Pencil size={12} />
                            </button>
                        )}
                        <div className={`
                            w-4 h-4 rounded-full border flex items-center justify-center transition-all
                            ${isSelected
                                ? `bg-${colorClass}-500 border-${colorClass}-500`
                                : 'border-slate-600 bg-black/40 group-hover:border-slate-500'
                            }
                        `}>
                            {isSelected && <div className="w-2 h-2 bg-white rounded-full" />}
                        </div>
                    </div>
                </div>

                {isEditing ? (
                    <div className="relative">
                        <textarea
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            className="w-full bg-black/40 border border-white/20 rounded p-2 text-sm text-slate-200 font-hindi focus:outline-none focus:border-blue-500 min-h-[60px]"
                            onClick={(e) => e.stopPropagation()}
                            autoFocus
                        />
                        <div className="flex justify-end gap-2 mt-2">
                            <button onClick={handleCancelEdit} className="p-1 hover:bg-white/10 rounded text-red-400">
                                <X size={14} />
                            </button>
                            <button onClick={handleSaveEdit} className="p-1 hover:bg-white/10 rounded text-green-400">
                                <Check size={14} />
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="text-sm text-slate-200 font-hindi whitespace-pre-wrap break-words leading-relaxed">
                        {renderValue(data.value)}
                    </div>
                )}
            </div>
        );
    };

    // Mobile: Show only active tab
    if (isMobile) {
        return (
            <div className="mb-3">
                <div className="text-xs font-bold text-slate-400 mb-1.5 font-hindi flex items-center gap-2">
                    {label}
                    {comparison.conflict && (
                        <span className="text-[9px] bg-yellow-500/10 text-yellow-400 px-1.5 py-0.5 rounded border border-yellow-500/20 font-hindi">
                            ⚠️ मतभेद
                        </span>
                    )}
                </div>
                {activeTab === 'parser' && renderField('parser', comparison.parser)}
                {activeTab === 'llm' && renderField('llm', comparison.llm)}
            </div>
        );
    }

    // Desktop/Tablet: Show both columns
    return (
        <div className="mb-3">
            <div className="text-xs font-bold text-slate-400 mb-1.5 font-hindi flex items-center gap-2">
                {label}
                {comparison.conflict && (
                    <span className="text-[9px] bg-yellow-500/10 text-yellow-400 px-1.5 py-0.5 rounded border border-yellow-500/20 font-hindi">
                        ⚠️ मतभेद
                    </span>
                )}
            </div>

            <div className="grid grid-cols-2 gap-3">
                {renderField('parser', comparison.parser)}
                {renderField('llm', comparison.llm)}
            </div>
        </div>
    );
};

export default FieldRow;
