import React, { useEffect, useState } from 'react';
import DecisionRow from './DecisionRow';
import { ParsedEvent } from '../../src/types';

interface DecisionConsoleProps {
    event: ParsedEvent;
    comparison: any;
    onFinalDataChange: (data: any) => void;
}

const DecisionConsole: React.FC<DecisionConsoleProps> = ({ event, comparison, onFinalDataChange }) => {
    // State for final decisions
    const [finalData, setFinalData] = useState<Record<string, any>>({
        event_type: [],
        people: [],
        schemes: [],
        communities: [],
        location: [], // Will hold location object(s) or strings
        word_buckets: []
    });

    // Initialize state from comparison or event data
    useEffect(() => {
        if (comparison) {
            // Logic to pre-fill: Use Parser if high confidence, else empty?
            // For now, let's pre-fill with Parser to be helpful
            const newFinal: any = {};
            ['event_type', 'people', 'schemes', 'communities', 'location'].forEach(field => {
                const parserVal = comparison.comparison[field]?.parser?.value;
                newFinal[field] = parserVal ? (Array.isArray(parserVal) ? parserVal : [parserVal]) : [];
            });

            // Word buckets might come from event data directly if not in comparison
            newFinal.word_buckets = event.parsed_data_v8.word_buckets || [];

            setFinalData(newFinal);
        }
    }, [comparison, event]);

    // Propagate changes up
    useEffect(() => {
        onFinalDataChange(finalData);
    }, [finalData, onFinalDataChange]);

    const handleUpdate = (field: string, values: any[]) => {
        setFinalData(prev => ({ ...prev, [field]: values }));
    };

    if (!comparison) return null;

    return (
        <div className="flex flex-col gap-2">
            <DecisionRow
                label="घटना का प्रकार"
                fieldKey="event_type"
                parserValues={comparison.comparison.event_type?.parser?.value}
                aiValues={comparison.comparison.event_type?.llm?.value}
                finalValues={finalData.event_type || []}
                onUpdateFinal={(vals) => handleUpdate('event_type', vals)}
                type="text"
            />

            <DecisionRow
                label="व्यक्ति / नेता"
                fieldKey="people"
                parserValues={comparison.comparison.people?.parser?.value}
                aiValues={comparison.comparison.people?.llm?.value}
                finalValues={finalData.people || []}
                onUpdateFinal={(vals) => handleUpdate('people', vals)}
                type="person"
            />

            <DecisionRow
                label="योजनाएं"
                fieldKey="schemes"
                parserValues={comparison.comparison.schemes?.parser?.value}
                aiValues={comparison.comparison.schemes?.llm?.value}
                finalValues={finalData.schemes || []}
                onUpdateFinal={(vals) => handleUpdate('schemes', vals)}
                type="text"
            />

            <DecisionRow
                label="समुदाय / लक्ष्य समूह"
                fieldKey="communities"
                parserValues={comparison.comparison.communities?.parser?.value}
                aiValues={comparison.comparison.communities?.llm?.value}
                finalValues={finalData.communities || []}
                onUpdateFinal={(vals) => handleUpdate('communities', vals)}
                type="text"
            />

            <DecisionRow
                label="स्थान"
                fieldKey="location"
                parserValues={comparison.comparison.location?.parser?.value ? [comparison.comparison.location.parser.value] : []}
                aiValues={comparison.comparison.location?.llm?.value ? [comparison.comparison.location.llm.value] : []}
                finalValues={finalData.location || []}
                onUpdateFinal={(vals) => handleUpdate('location', vals)}
                type="location"
            />
        </div>
    );
};

export default DecisionConsole;
