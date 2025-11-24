import React from 'react';
import HierarchyMindMap from '../components/analytics/HierarchyMindMap';
import AnimatedGlassCard from '../components/AnimatedGlassCard';

const Mindmap = () => {
    return (
        <div className="space-y-6 pb-20">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-white font-hindi">पदानुक्रम माइंडमैप (Hierarchy Mindmap)</h1>
                    <p className="text-slate-400 text-sm font-hindi">विस्तृत पदानुक्रम दृश्य</p>
                </div>
            </div>

            <AnimatedGlassCard className="min-h-[80vh]">
                <HierarchyMindMap height={800} />
            </AnimatedGlassCard>
        </div>
    );
};

export default Mindmap;
