import React from 'react';
import { motion } from 'framer-motion';
import { BrainCircuit, Sparkles } from 'lucide-react';
import FieldRow from './FieldRow';

interface FieldComparison {
    parser: { value: any; confidence: number; source?: string };
    llm: { value: any; confidence: number; source?: string };
    conflict: boolean;
}

interface ComparisonGridProps {
    comparison: Record<string, FieldComparison>;
    selectedValues: Record<string, 'parser' | 'llm'>;
    onFieldSelect: (field: string, source: 'parser' | 'llm') => void;
    onManualEdit: (field: string, value: any) => void;
    isMobile: boolean;
    activeTab: 'parser' | 'llm';
}

const FIELD_ORDER = [
    { key: 'event_type', label: 'घटना प्रकार' },
    { key: 'people', label: 'उल्लिखित व्यक्ति' },
    { key: 'schemes', label: 'योजनाएं' },
    { key: 'communities', label: 'समुदाय' },
    { key: 'location', label: 'स्थान' }
];

const ComparisonGrid: React.FC<ComparisonGridProps> = ({
    comparison,
    selectedValues,
    onFieldSelect,
    onManualEdit,
    isMobile,
    activeTab
}) => {
    return (
        <div className="space-y-3">
            {/* Header Row (Desktop/Tablet only) */}
            {!isMobile && (
                <div className="grid grid-cols-2 gap-4 mb-4 px-1">
                    <div data-column="parser" className="pb-2 border-b border-cyan-500/20">
                        <span className="text-xs font-bold text-cyan-400 uppercase tracking-widest font-hindi flex items-center gap-2">
                            <BrainCircuit size={14} /> पार्सर इंजन
                        </span>
                    </div>
                    <div data-column="llm" className="pb-2 border-b border-violet-500/20">
                        <span className="text-xs font-bold text-violet-400 uppercase tracking-widest font-hindi flex items-center gap-2">
                            <Sparkles size={14} /> एआई इंजन
                        </span>
                    </div>
                </div>
            )}

            {/* Field Rows */}
            {FIELD_ORDER.map((field, index) => {
                const fieldComp = comparison[field.key];
                if (!fieldComp) return null;

                return (
                    <motion.div
                        key={field.key}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                    >
                        <FieldRow
                            fieldKey={field.key}
                            label={field.label}
                            comparison={fieldComp}
                            selected={selectedValues[field.key]}
                            onSelect={(source) => onFieldSelect(field.key, source)}
                            onManualEdit={(value) => onManualEdit(field.key, value)}
                            isMobile={isMobile}
                            activeTab={activeTab}
                        />
                    </motion.div>
                );
            })}
        </div>
    );
};

export default ComparisonGrid;
