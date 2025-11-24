import React from 'react';
import { CheckSquare, Clock, SkipForward, List } from 'lucide-react';
import { useReviewStatus } from '../../utils/reviewStatusStore';

interface ReviewStatusPanelProps {
    totalCount: number;
    approvedCount: number;
    pendingCount: number;
    skippedCount: number;
}

const ReviewStatusPanel: React.FC<ReviewStatusPanelProps> = ({
    totalCount,
    approvedCount,
    pendingCount,
    skippedCount,
}) => {
    const {
        showApproved,
        showPending,
        showSkipped,
        toggleApproved,
        togglePending,
        toggleSkipped,
    } = useReviewStatus();

    return (
        <div className="bg-[#0f172a]/95 backdrop-blur-xl border border-white/10 rounded-xl p-4 w-64 shadow-2xl">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 font-hindi border-b border-white/5 pb-2">
                समीक्षा स्थिति
            </h4>

            <div className="space-y-1">
                {/* Total Count (No Checkbox) */}
                <div className="flex justify-between items-center p-2 rounded-lg hover:bg-white/5 transition-colors">
                    <div className="flex items-center gap-2 text-slate-300">
                        <List size={14} className="text-blue-400" />
                        <span className="text-sm font-hindi">कुल ट्वीट्स</span>
                    </div>
                    <span className="text-sm font-bold text-white">{totalCount}</span>
                </div>

                {/* Approved */}
                <div
                    className="flex justify-between items-center p-2 rounded-lg hover:bg-white/5 transition-colors cursor-pointer group"
                    onClick={toggleApproved}
                >
                    <div className="flex items-center gap-2 text-slate-300 group-hover:text-white transition-colors">
                        <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${showApproved ? 'bg-green-500 border-green-500' : 'border-slate-500'}`}>
                            {showApproved && <CheckSquare size={10} className="text-white" />}
                        </div>
                        <span className="text-sm font-hindi">स्वीकृत</span>
                    </div>
                    <span className="text-xs font-medium text-slate-400 bg-white/5 px-2 py-0.5 rounded-full">{approvedCount}</span>
                </div>

                {/* Pending */}
                <div
                    className="flex justify-between items-center p-2 rounded-lg hover:bg-white/5 transition-colors cursor-pointer group"
                    onClick={togglePending}
                >
                    <div className="flex items-center gap-2 text-slate-300 group-hover:text-white transition-colors">
                        <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${showPending ? 'bg-yellow-500 border-yellow-500' : 'border-slate-500'}`}>
                            {showPending && <Clock size={10} className="text-white" />}
                        </div>
                        <span className="text-sm font-hindi">लंबित</span>
                    </div>
                    <span className="text-xs font-medium text-slate-400 bg-white/5 px-2 py-0.5 rounded-full">{pendingCount}</span>
                </div>

                {/* Skipped */}
                <div
                    className="flex justify-between items-center p-2 rounded-lg hover:bg-white/5 transition-colors cursor-pointer group"
                    onClick={toggleSkipped}
                >
                    <div className="flex items-center gap-2 text-slate-300 group-hover:text-white transition-colors">
                        <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${showSkipped ? 'bg-slate-500 border-slate-500' : 'border-slate-500'}`}>
                            {showSkipped && <SkipForward size={10} className="text-white" />}
                        </div>
                        <span className="text-sm font-hindi">स्किप्ड</span>
                    </div>
                    <span className="text-xs font-medium text-slate-400 bg-white/5 px-2 py-0.5 rounded-full">{skippedCount}</span>
                </div>
            </div>
        </div>
    );
};

export default ReviewStatusPanel;
