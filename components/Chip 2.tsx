import React, { useState, useRef, useEffect } from 'react';
import { X, Check } from 'lucide-react';
import { translateToHindi } from '../utils/textUtils';

interface ChipProps {
    label: string;
    onRemove?: () => void;
    onEdit?: (newValue: string) => void;
    color?: 'slate' | 'blue' | 'emerald' | 'purple' | 'amber' | 'cyan' | 'violet';
    className?: string;
    readOnly?: boolean;
}

const Chip: React.FC<ChipProps> = ({
    label,
    onRemove,
    onEdit,
    color = 'slate',
    className = '',
    readOnly = false
}) => {
    const [isEditing, setIsEditing] = useState(false);
    const displayLabel = translateToHindi(label);
    const [editValue, setEditValue] = useState(displayLabel);
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (isEditing && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isEditing]);

    const handleDoubleClick = () => {
        if (!readOnly && onEdit) {
            setIsEditing(true);
            setEditValue(displayLabel);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            saveEdit();
        } else if (e.key === 'Escape') {
            cancelEdit();
        }
    };

    const saveEdit = () => {
        if (editValue.trim() && editValue !== displayLabel) {
            onEdit?.(editValue.trim());
        }
        setIsEditing(false);
    };

    const cancelEdit = () => {
        setIsEditing(false);
        setEditValue(displayLabel);
    };

    // Uniform styling as requested
    // Base: text-slate-100, clean glow
    const baseClasses = "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-hindi border transition-all cursor-default";

    // Map colors to border/bg styles, but keep text uniform as requested
    const colorStyles = {
        slate: "bg-slate-500/20 border-slate-500/30 shadow-[0_0_10px_rgba(100,116,139,0.1)]",
        blue: "bg-blue-500/20 border-blue-500/30 shadow-[0_0_10px_rgba(59,130,246,0.1)]",
        emerald: "bg-emerald-500/20 border-emerald-500/30 shadow-[0_0_10px_rgba(16,185,129,0.1)]",
        purple: "bg-purple-500/20 border-purple-500/30 shadow-[0_0_10px_rgba(168,85,247,0.1)]",
        amber: "bg-amber-500/20 border-amber-500/30 shadow-[0_0_10px_rgba(245,158,11,0.1)]",
        cyan: "bg-cyan-500/20 border-cyan-500/30 shadow-[0_0_10px_rgba(6,182,212,0.1)]",
        violet: "bg-violet-500/20 border-violet-500/30 shadow-[0_0_10px_rgba(139,92,246,0.1)]",
    };

    if (isEditing) {
        return (
            <div className={`${baseClasses} ${colorStyles[color]} ring-1 ring-white/50`}>
                <input
                    ref={inputRef}
                    type="text"
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    onBlur={saveEdit}
                    className="bg-transparent border-none outline-none text-white w-20 min-w-[50px] text-sm font-hindi p-0"
                />
                <button onClick={saveEdit} className="text-green-400 hover:text-green-300">
                    <Check size={12} />
                </button>
            </div>
        );
    }

    return (
        <span
            className={`${baseClasses} ${colorStyles[color]} text-slate-100 hover:bg-white/10 ${className}`}
            onDoubleClick={handleDoubleClick}
            title={!readOnly ? "Double click to edit" : undefined}
        >
            {displayLabel}
            {!readOnly && onRemove && (
                <button
                    onClick={(e) => { e.stopPropagation(); onRemove(); }}
                    className="opacity-60 hover:opacity-100 text-slate-300 hover:text-red-400 transition-all p-0.5 rounded-full hover:bg-black/20"
                >
                    <X size={12} />
                </button>
            )}
        </span>
    );
};

export default Chip;
