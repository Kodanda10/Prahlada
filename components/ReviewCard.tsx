import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Edit2, MapPin } from 'lucide-react';
import GeoNeuroResolver from '../src/components/decision/GeoNeuroResolver';
import { ParsedEvent } from '../src/types';

type ReviewCardProps = {
  event: ParsedEvent;
  onApprove?: (excludeFromAnalytics?: boolean) => void;
  onEdit?: () => void;
  onSave?: (updated: ParsedEvent) => void;
};

const LocationBreadcrumbs = ({ location }: { location: ParsedEvent['parsed_data_v8']['location'] }) => {
  // Check if location has any meaningful data
  const hasLocation = location && (
    location.district || 
    location.assembly || 
    location.block || 
    location.village || 
    location.gp || 
    location.ulb || 
    location.ward
  );
  
  if (!hasLocation) {
    return (
      <div className="text-amber-400/80 text-sm font-hindi italic">
        कोई स्थान उल्लेखित नहीं
      </div>
    );
  }

  const isUrban = !!location.ulb;
  const render = (label: string | null | undefined, tag: string, isLast?: boolean) =>
    label ? (
      <div className="flex items-center" key={`${tag}-${label}`}>
        <div className="flex flex-col">
          <span className={`text-xs font-bold font-hindi ${isLast ? 'text-emerald-400' : 'text-slate-300'}`}>{label}</span>
          <span className="text-[9px] text-slate-500 uppercase tracking-wider font-mono">{tag}</span>
        </div>
        {!isLast && <span className="text-slate-700 mx-2">/</span>}
      </div>
    ) : null;

  return (
    <div className="flex flex-wrap items-center gap-y-2 w-full">
      {render(location.district, 'DISTRICT')}
      {render(location.assembly, 'ASSEMBLY')}
      {isUrban ? (
        <>
          {render(location.ulb, 'ULB')}
          {render(location.zone, 'ZONE')}
          {render(location.ward, 'WARD', true)}
        </>
      ) : (
        <>
          {render(location.block, 'BLOCK')}
          {render(location.gp, 'PANCHAYAT')}
          {render(location.village, 'VILLAGE', true)}
        </>
      )}
    </div>
  );
};

const ReviewCard: React.FC<ReviewCardProps> = ({ event, onApprove, onEdit, onSave }) => {
  const [isLocationModalOpen, setIsLocationModalOpen] = useState(false);
  const [editedLocation, setEditedLocation] = useState(event.parsed_data_v8.location);

  const handleLocationSelect = (locationData: any) => {
    // Handle both Urban and Rural hierarchies
    const isUrban = locationData.areaType === 'URBAN';
    setEditedLocation(prev => ({
      ...prev,
      district: locationData.district,
      assembly: locationData.vidhansabha,
      block: locationData.block,
      village: isUrban ? null : locationData.village,
      gp: isUrban ? null : locationData.gp,
      ulb: isUrban ? locationData.ulb : null,
      zone: null,
      ward: locationData.ward,
    }));
    if (onSave) {
      onSave({
        ...event,
        parsed_data_v8: {
          ...event.parsed_data_v8,
          location: {
            ...event.parsed_data_v8.location,
            district: locationData.district,
            assembly: locationData.vidhansabha,
            block: locationData.block,
            village: isUrban ? null : locationData.village,
            gp: isUrban ? null : locationData.gp,
            ulb: isUrban ? locationData.ulb : null,
            ward: locationData.ward,
          },
        },
      });
    }
    setIsLocationModalOpen(false);
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-slate-900/60 border border-white/10 rounded-2xl p-6 text-white shadow-lg"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">Tweet ID</p>
          <p className="text-sm font-mono text-indigo-200">{event.tweet_id}</p>
          <p className="text-sm text-slate-300 mt-2 font-hindi">{event.raw_text}</p>
        </div>
        <div className="flex gap-2">
          {onEdit && (
            <button onClick={onEdit} className="text-xs px-3 py-1 rounded-full border border-white/15 bg-white/5 hover:bg-white/10 transition-colors">
              Edit
            </button>
          )}
          {onApprove && (
            <button onClick={() => onApprove(false)} className="text-xs px-3 py-1 rounded-full border border-emerald-400/40 text-emerald-200 bg-emerald-500/10 hover:bg-emerald-500/20 transition-colors">
              Approve
            </button>
          )}
        </div>
      </div>

      <div className="mt-6">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-1.5 text-xs text-slate-400 uppercase tracking-wider font-bold font-hindi">
            <MapPin size={12} className="text-[#8BF5E6]" /> अनुमानित स्थान पदानुक्रम
          </div>
          <button
            onClick={() => setIsLocationModalOpen(true)}
            className="text-[10px] text-indigo-300 hover:text-indigo-200 flex items-center gap-1 transition-colors font-hindi bg-indigo-500/10 px-2 py-1 rounded border border-indigo-500/20"
          >
            <Edit2 size={10} /> स्थान बदलें
          </button>
        </div>
        <LocationBreadcrumbs location={editedLocation} />
      </div>

      <GeoNeuroResolver
        isOpen={isLocationModalOpen}
        onClose={() => setIsLocationModalOpen(false)}
        onSelect={handleLocationSelect}
        initialLocation={{
          district: editedLocation?.district || null,
          vidhansabha: editedLocation?.assembly || null,
          block: editedLocation?.block || null,
          village: editedLocation?.village || null,
          gp: editedLocation?.gp || null,
          ulb: editedLocation?.ulb || null,
          ward: editedLocation?.ward || null,
          areaType: editedLocation?.ulb ? 'URBAN' : 'RURAL',
        }}
      />
    </motion.div>
  );
};

export default ReviewCard;
