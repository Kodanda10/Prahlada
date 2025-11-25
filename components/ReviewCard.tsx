import React, { useState } from 'react';
import { Check, Edit2, MapPin, Sparkles, BrainCircuit, Activity, ExternalLink } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { ParsedEvent } from '../types';
import FieldDisplay from './FieldDisplay';
import TweetPreviewModal from './TweetPreviewModal';

interface ReviewCardProps {
  event: ParsedEvent;
  onApprove: (excludeFromAnalytics: boolean) => void;
  onEdit: () => void;
  onSave?: (newData: any) => void;
}

const LocationBreadcrumbs = ({ location }: { location: ParsedEvent['parsed_data_v8']['location'] }) => {
  if (!location) return <span className="text-red-400 text-xs font-hindi">स्थान पार्स नहीं हुआ</span>;

  const isUrban = !!location.ulb;

  const BreadcrumbItem = ({ label, type, isLast }: { label?: string | null, type: string, isLast?: boolean }) => {
    if (!label) return null;
    return (
      <div className="flex items-center">
        <div className={`flex flex-col ${isLast ? 'opacity-100' : 'opacity-60 group-hover:opacity-80 transition-opacity'}`}>
          <span className={`text-xs font-bold font-hindi ${isLast ? 'text-[#8BF5E6]' : 'text-slate-300'}`}>{label}</span>
          <span className="text-[9px] text-slate-500 uppercase tracking-wider font-hindi">{type}</span>
        </div>
        {!isLast && <span className="text-slate-700 mx-1.5">›</span>}
      </div>
    );
  };

  return (
    <div className="flex flex-wrap items-center gap-y-2 bg-black/30 p-3 rounded-xl border border-white/10 w-full">
      <BreadcrumbItem label={location.district} type="जिला" />
      <BreadcrumbItem label={location.assembly} type="विधानसभा" />

      {isUrban ? (
        <>
          <BreadcrumbItem label={location.ulb} type="निकाय" />
          <BreadcrumbItem label={location.zone} type="जोन" />
          <BreadcrumbItem label={location.ward} type="वार्ड" isLast />
        </>
      ) : (
        <>
          <BreadcrumbItem label={location.block} type="विकासखंड" />
          <BreadcrumbItem label={location.gp} type="ग्राम पंचायत" />
          <BreadcrumbItem label={location.village} type="ग्राम" isLast />
        </>
      )}
    </div>
  );
};

const ReviewCard: React.FC<ReviewCardProps> = ({ event, onApprove, onEdit, onSave }) => {
  const [excludeFromAnalytics, setExcludeFromAnalytics] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState(event.parsed_data_v8);

  const handleApprove = () => {
    onApprove(excludeFromAnalytics);
  };

  const handleSaveEdit = () => {
    setIsEditing(false);
    console.log("Saved data:", editedData);

    if (onSave) {
      onSave(editedData);
    }

    // Trigger simulation
    setIsSimulating(true);
    // Simulate API call (or wait for prop update)
    // setTimeout(() => setIsSimulating(false), 2000);
  };

  const [hoverState, setHoverState] = useState<{ isOpen: boolean, x: number, y: number }>({ isOpen: false, x: 0, y: 0 });

  const handleMouseEnter = (e: React.MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setHoverState({
      isOpen: true,
      x: rect.right + 10,
      y: rect.top - 20
    });
  };

  const handleMouseLeave = () => {
    setHoverState(prev => ({ ...prev, isOpen: false }));
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -100 }}
      className="bg-white/5 p-5 rounded-2xl border border-white/10 mb-4 hover:bg-white/10 transition-colors group relative shadow-lg"
    >
      <TweetPreviewModal
        isOpen={hoverState.isOpen}
        tweetId={event.tweet_id}
        text={event.raw_text}
        x={hoverState.x}
        y={hoverState.y}
      />

      {/* Tweet Text */}
      <div className="relative">
        <p className="text-sm text-slate-200 mb-4 leading-relaxed font-hindi bg-black/20 p-3 rounded-lg border border-white/5">
          "{event.raw_text}"
        </p>
        <div className="absolute top-2 right-2">
          <a
            href={`https://twitter.com/i/web/status/${event.tweet_id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 hover:text-blue-300 transition-colors"
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
          >
            <ExternalLink size={14} />
          </a>
        </div>
      </div>

      {/* Parsed Metadata */}
      <div className="space-y-4 mb-5">

        {/* Event Type & Confidence */}
        <div className="flex items-center justify-between">
          <div className="flex gap-2">
            {isEditing ? (
              <input
                className="bg-black/40 border border-white/20 rounded px-2 py-1 text-xs text-white font-hindi"
                value={editedData.event_type}
                onChange={(e) => setEditedData({ ...editedData, event_type: e.target.value })}
              />
            ) : (
              <span className="px-3 py-1 bg-purple-500/20 text-purple-300 text-xs rounded-lg border border-purple-500/30 font-medium font-hindi">
                {editedData.event_type}
              </span>
            )}
            {event.parsed_data_v8.event_type_secondary?.map(type => (
              <span key={type} className="px-3 py-1 bg-slate-500/20 text-slate-300 text-xs rounded-lg border border-slate-500/30 font-medium font-hindi">
                {type}
              </span>
            ))}
          </div>
          <div className="flex items-center gap-2 text-xs bg-black/30 px-3 py-1 rounded-full border border-white/10">
            <span className="text-slate-400 font-hindi">AI आत्मविश्वास:</span>
            <span className={`font-bold ${event.parsed_data_v8.confidence > 0.9 ? 'text-green-400' : 'text-yellow-400'}`}>
              {(event.parsed_data_v8.confidence * 100).toFixed(0)}%
            </span>
          </div>
        </div>

        {/* Hierarchical Location */}
        <div>
          <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-2 uppercase tracking-wider font-bold font-hindi">
            <MapPin size={12} className="text-[#8BF5E6]" /> अनुमानित स्थान पदानुक्रम
          </div>
          <LocationBreadcrumbs location={event.parsed_data_v8.location} />
        </div>

        {/* Expanded Metadata Fields */}
        <div className="grid grid-cols-2 gap-3">
          <FieldDisplay
            label="लक्ष्य समूह"
            values={event.parsed_data_v8.target_groups}
            color="amber"
          />
          <FieldDisplay
            label="समुदाय"
            values={event.parsed_data_v8.communities}
            color="pink"
          />
          <FieldDisplay
            label="योजनाएं"
            values={event.parsed_data_v8.schemes_mentioned}
            color="green"
          />
          <FieldDisplay
            label="उल्लिखित व्यक्ति"
            values={event.parsed_data_v8.people_canonical}
            color="blue"
          />
        </div>

        {/* Word Bucket (Consolidated Keywords for Cognitive Engine) */}
        <div className="mt-4 pt-4 border-t border-white/5">
          <div className="flex items-center gap-2 text-xs text-slate-500 mb-3 font-hindi uppercase tracking-wider font-bold">
            <BrainCircuit size={14} className="text-yellow-400" />
            <span>वर्ड बकेट (Word Bucket - Cognitive Input)</span>
          </div>

          <div className="flex flex-col gap-2 bg-black/20 p-3 rounded-xl border border-white/5">
            {/* Locations */}
            {event.parsed_data_v8.location && (
              <div className="flex items-start gap-2">
                <MapPin size={12} className="text-[#8BF5E6] mt-1 shrink-0" />
                <div className="flex flex-wrap gap-1.5">
                  {[
                    event.parsed_data_v8.location.district,
                    event.parsed_data_v8.location.ulb,
                    event.parsed_data_v8.location.village,
                    event.parsed_data_v8.location.zone
                  ].filter(Boolean).map((loc, i) => (
                    <span key={`loc-${i}`} className="px-2 py-0.5 bg-[#8BF5E6]/10 text-[#8BF5E6] text-[10px] rounded border border-[#8BF5E6]/20 font-hindi">
                      {loc}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* People */}
            {event.parsed_data_v8.people_canonical && event.parsed_data_v8.people_canonical.length > 0 && (
              <div className="flex items-start gap-2">
                <Activity size={12} className="text-blue-400 mt-1 shrink-0" />
                <div className="flex flex-wrap gap-1.5">
                  {event.parsed_data_v8.people_canonical.map((person, i) => (
                    <span key={`person-${i}`} className="px-2 py-0.5 bg-blue-500/10 text-blue-300 text-[10px] rounded border border-blue-500/20 font-hindi">
                      {person}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Schemes */}
            {event.parsed_data_v8.schemes_mentioned && event.parsed_data_v8.schemes_mentioned.length > 0 && (
              <div className="flex items-start gap-2">
                <Sparkles size={12} className="text-green-400 mt-1 shrink-0" />
                <div className="flex flex-wrap gap-1.5">
                  {event.parsed_data_v8.schemes_mentioned.map((scheme, i) => (
                    <span key={`scheme-${i}`} className="px-2 py-0.5 bg-green-500/10 text-green-300 text-[10px] rounded border border-green-500/20 font-hindi">
                      {scheme}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Other Entities (Groups, Communities, Orgs) */}
            {(event.parsed_data_v8.target_groups?.length || event.parsed_data_v8.communities?.length || event.parsed_data_v8.organizations?.length) ? (
              <div className="flex items-start gap-2">
                <div className="w-3 h-3 rounded-full bg-slate-500/50 mt-1 shrink-0" />
                <div className="flex flex-wrap gap-1.5">
                  {[
                    ...(event.parsed_data_v8.target_groups || []),
                    ...(event.parsed_data_v8.communities || []),
                    ...(event.parsed_data_v8.organizations || [])
                  ].map((item, i) => (
                    <span key={`other-${i}`} className="px-2 py-0.5 bg-white/5 text-slate-300 text-[10px] rounded border border-white/10 font-hindi">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        </div>

        {/* Visual Thought Interface (Placeholder for Phase 6) */}
        <div className="mt-4 pt-4 border-t border-white/5">
          <div className="flex items-center gap-2 text-xs text-slate-500 mb-2 font-hindi">
            <BrainCircuit size={14} className="text-indigo-400" />
            <span>AI तर्क (Nightly Brain)</span>
          </div>
          <div className="bg-black/30 p-3 rounded-lg border border-indigo-500/20 text-[10px] text-indigo-200/70 font-mono leading-relaxed">
            {isSimulating ? (
              <span className="flex items-center gap-2">
                <Activity size={10} className="animate-pulse" /> सिमुलेशन चल रहा है...
              </span>
            ) : (
              "कोई विसंगति नहीं मिली। नियम v8.2 के अनुसार पार्स किया गया।"
            )}
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-col gap-3">

        {/* Skip-Box Checkbox */}
        <label className="flex items-center gap-2 cursor-pointer group w-fit">
          <input
            type="checkbox"
            checked={excludeFromAnalytics}
            onChange={(e) => setExcludeFromAnalytics(e.target.checked)}
            className="w-4 h-4 rounded border-white/20 bg-black/20 checked:bg-red-500 focus:ring-0 focus:ring-offset-0"
          />
          <span className="text-xs text-slate-400 group-hover:text-slate-200 font-hindi transition-colors">
            एनालिटिक्स में शामिल न करें (Skip Analytics)
          </span>
        </label>

        <div className="flex gap-3">
          <button
            onClick={handleApprove}
            className="flex-1 bg-green-600/20 text-green-400 py-2.5 rounded-xl hover:bg-green-600/30 transition-all text-xs border border-green-600/30 flex justify-center items-center gap-2 font-bold hover:scale-[1.02] active:scale-[0.98] font-hindi"
          >
            <Check size={16} /> स्वीकृत करें
          </button>

          {isEditing ? (
            <button
              onClick={handleSaveEdit}
              className="flex-1 bg-indigo-600/20 text-indigo-400 py-2.5 rounded-xl hover:bg-indigo-600/30 transition-all text-xs border border-indigo-600/30 flex justify-center items-center gap-2 font-bold hover:scale-[1.02] active:scale-[0.98] font-hindi"
            >
              <Check size={16} /> सहेजें (Save)
            </button>
          ) : (
            <button
              onClick={() => setIsEditing(true)}
              className="flex-1 bg-blue-600/20 text-blue-400 py-2.5 rounded-xl hover:bg-blue-600/30 transition-all text-xs border border-blue-600/30 flex justify-center items-center gap-2 font-bold hover:scale-[1.02] active:scale-[0.98] font-hindi"
            >
              <Edit2 size={16} /> संशोधन करें
            </button>
          )}
        </div>

        {/* Micro-Hint for Dynamic Learning */}
        <div className="text-center pt-1">
          <span className="text-[10px] text-slate-500 flex items-center justify-center gap-1.5 opacity-60 group-hover:opacity-100 transition-opacity font-hindi">
            <Sparkles size={10} className="text-yellow-500" /> आपके सुधार AI को भविष्य में बेहतर बनाते हैं (डायनामिक लर्निंग)
          </span>
        </div>
      </div>
    </motion.div>
  );
};

export default ReviewCard;
