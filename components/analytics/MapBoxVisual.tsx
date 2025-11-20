
import React, { useState } from 'react';
import { MapPin, Navigation } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface MapMarker {
  id: string;
  lat: number; 
  lng: number;
  label: string; // e.g. "खरसिया (05)"
  type: 'event' | 'location';
  details: string;
  date: string;
}

// Mock Data with Hindi Labels and English Numerals
const MARKERS: MapMarker[] = [
  { id: '1', lat: 30, lng: 40, label: 'खरसिया (05)', type: 'event', details: 'जनसम्पर्क अभियान', date: '19 नवंबर' },
  { id: '2', lat: 45, lng: 60, label: 'रायगढ़ शहर (12)', type: 'location', details: 'समीक्षा बैठक', date: '18 नवंबर' },
  { id: '3', lat: 60, lng: 30, label: 'घरघोड़ा (03)', type: 'event', details: 'उद्घाटन समारोह', date: '17 नवंबर' },
  { id: '4', lat: 50, lng: 70, label: 'तमनार (02)', type: 'location', details: 'ग्राम दौरा', date: '16 नवंबर' },
  { id: '5', lat: 20, lng: 55, label: 'लैलूंगा (08)', type: 'event', details: 'विकास कार्य निरीक्षण', date: '15 नवंबर' },
];

const MapBoxVisual = () => {
  const [activeMarker, setActiveMarker] = useState<string | null>(null);

  return (
    <div className="relative w-full h-full min-h-[350px] bg-[#0f172a] rounded-xl overflow-hidden border border-white/10 group shadow-inner">
      
      {/* Dark Map Texture */}
      <div className="absolute inset-0 opacity-40" 
           style={{
             backgroundImage: 'radial-gradient(circle at 50% 50%, #334155 1px, transparent 1px)',
             backgroundSize: '24px 24px'
           }}>
      </div>
      
      {/* Vector Geometry (Rivers/Roads) Simulation */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-30" viewBox="0 0 100 100" preserveAspectRatio="none">
        <path d="M10,30 Q40,10 60,30 T90,60" fill="none" stroke="#3b82f6" strokeWidth="0.6" />
        <path d="M20,80 Q50,60 70,80" fill="none" stroke="#8BF5E6" strokeWidth="0.4" />
        <path d="M30,0 Q35,50 30,100" fill="none" stroke="#64748b" strokeWidth="0.3" strokeDasharray="3 2" />
      </svg>

      {/* Interactive Markers */}
      {MARKERS.map((marker) => (
        <motion.div
          key={marker.id}
          className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer z-10"
          style={{ top: `${marker.lat}%`, left: `${marker.lng}%` }}
          onMouseEnter={() => setActiveMarker(marker.id)}
          onMouseLeave={() => setActiveMarker(null)}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          whileHover={{ scale: 1.2 }}
        >
          <div className="relative flex flex-col items-center">
            {/* Pulse Ring */}
            <div className={`absolute inset-0 rounded-full animate-ping opacity-75 w-full h-full ${marker.type === 'event' ? 'bg-[#8BF5E6]' : 'bg-purple-500'}`}></div>
            
            {/* Marker Pin */}
            <div className={`relative z-10 w-6 h-6 md:w-8 md:h-8 rounded-full flex items-center justify-center shadow-lg border border-white/20 ${
              marker.type === 'event' ? 'bg-[#8BF5E6] text-black' : 'bg-purple-600 text-white'
            }`}>
              <MapPin size={14} fill="currentColor" />
            </div>

            {/* Persistent Label (Hindi) */}
            <div className="mt-1 px-2 py-0.5 bg-black/60 backdrop-blur-sm rounded text-[9px] text-white whitespace-nowrap border border-white/10 font-hindi shadow-sm">
               {marker.label}
            </div>

            {/* Animated Tooltip on Hover */}
            <AnimatePresence>
              {activeMarker === marker.id && (
                <motion.div 
                  initial={{ opacity: 0, y: 10, scale: 0.9 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.9 }}
                  className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-48 bg-[#0f172a]/95 backdrop-blur-xl border border-white/10 rounded-xl p-3 shadow-2xl z-50"
                >
                  <div className="text-xs font-bold text-[#8BF5E6] mb-1 font-hindi">{marker.label.split(' ')[0]}</div>
                  <div className="text-[10px] text-slate-300 border-b border-white/10 pb-2 mb-2 leading-relaxed font-hindi">
                     <span className="text-slate-500 block text-[9px] uppercase">विवरण:</span>
                     {marker.details}
                  </div>
                  <div className="flex justify-between items-center text-[10px]">
                    <span className="text-slate-400 font-hindi">{marker.date}</span>
                    <span className="text-green-400 flex items-center gap-1 font-medium bg-green-900/20 px-1.5 py-0.5 rounded font-hindi"><Navigation size={8} /> दिशा</span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      ))}

      {/* Info Legend */}
      <div className="absolute top-4 left-4 bg-black/40 backdrop-blur-md border border-white/10 rounded-lg px-4 py-2 pointer-events-none">
        <span className="text-xs font-bold text-slate-200 flex items-center gap-2 font-hindi">
           <MapPin size={12} className="text-[#8BF5E6]" /> रायगढ़ जिला कवरेज
        </span>
      </div>
    </div>
  );
};

export default MapBoxVisual;
