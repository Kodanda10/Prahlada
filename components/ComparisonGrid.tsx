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
    { key: 'event_type', label: 'घटना प्रकार (Event Type)' },
    { key: 'people', label: 'उल्लिखित व्यक्ति (People)' },
    { key: 'schemes', label: 'योजनाएं (Schemes)' },
    { key: 'communities', label: 'समुदाय (Communities)' },
    { key: 'location', label: 'स्थान (Location)' }
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
                <div className="grid grid-cols-2 gap-3 mb-2">
                    <div data-column="parser" className="text-center pb-3 border-b border-indigo-500/10">
                        <span className="text-sm font-bold text-indigo-200/80 uppercase tracking-wider font-hindi flex items-center justify-center gap-2">
                            <span className="p-1 bg-indigo-500/10 rounded-md"><BrainCircuit size={14} /></span> पार्सर (Parser V2)
                        </span>
                    </div>
                    <div data-column="llm" className="text-center pb-3 border-b border-pink-500/10">
                        <span className="text-sm font-bold text-pink-200/80 uppercase tracking-wider font-hindi flex items-center justify-center gap-2">
                            <span className="p-1 bg-pink-500/10 rounded-md"><Sparkles size={14} /></span> बौद्धिक इंजन (LLM)
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
