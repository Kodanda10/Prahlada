import React, { useState } from 'react';
import { Download, Map, Users, Target, Lightbulb, Building, Share2 } from 'lucide-react';
import { motion } from 'framer-motion';
import AnimatedGlassCard from '../components/AnimatedGlassCard';
import CustomPieChart from '../components/charts/CustomPieChart';
import CustomBarChart from '../components/charts/CustomBarChart';
import MapBoxVisual from '../components/analytics/MapBoxVisual';
import HierarchyMindMap from '../components/analytics/HierarchyMindMap';
import NumberTicker from '../components/NumberTicker';
import { exportToExcel, exportToPDF } from '../utils/export';

import { fetchAnalyticsData } from '../services/api';

// Initial empty data or loading state
const initialEventTypeData = [
  { name: 'जनसम्पर्क', value: 0, fill: '#8BF5E6' },
  { name: 'समीक्षा बैठक', value: 0, fill: '#3b82f6' },
  { name: 'उद्घाटन', value: 0, fill: '#a855f7' },
  { name: 'दौरा', value: 0, fill: '#ec4899' },
  { name: 'अन्य', value: 0, fill: '#64748b' },
];

// Parent variants for staggering
const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1
    }
  }
};

const AnalyticsDashboard = () => {
  const [geoViewMode, setGeoViewMode] = useState<'map' | 'hierarchy'>('map');
  const [eventTypeData, setEventTypeData] = useState(initialEventTypeData);
  const [developmentData, setDevelopmentData] = useState<any[]>([]);
  const [schemeData, setSchemeData] = useState<any[]>([]);

  React.useEffect(() => {
    const loadData = async () => {
      try {
        const events = await fetchAnalyticsData('event-types');
        if (events && events.length > 0) {
          // Map API data to chart format
          const mappedEvents = events.map((e: any, idx: number) => ({
            name: e.name,
            value: e.value,
            fill: ['#8BF5E6', '#3b82f6', '#a855f7', '#ec4899', '#64748b'][idx % 5]
          }));
          setEventTypeData(mappedEvents);
        }

        const districts = await fetchAnalyticsData('districts');
        // Use districts data or other endpoints as needed
      } catch (err) {
        console.error("Failed to load analytics data", err);
      }
    };
    loadData();
  }, []);

  const handleDownloadExcel = () => {
    // Combine all data for export
    const allData = [
      ...eventTypeData.map(d => ({ Category: 'Event Type', Name: d.name, Value: d.value })),
      ...developmentData.map(d => ({ Category: 'Development', Name: d.name, Value: d.value })),
      ...schemeData.map(d => ({ Category: 'Scheme', Name: d.name, Value: d.count })),
    ];
    exportToExcel(allData, 'analytics_report');
  };

  const handleDownloadPDF = () => {
    const allData = [
      ...eventTypeData.map(d => ({ Category: 'Event Type', Name: d.name, Value: d.value })),
      ...developmentData.map(d => ({ Category: 'Development', Name: d.name, Value: d.value })),
      ...schemeData.map(d => ({ Category: 'Scheme', Name: d.name, Value: d.count })),
    ];
    exportToPDF(allData, 'analytics_report');
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="space-y-6 font-sans pb-10"
    >

      {/* Top Filters & Export */}
      <motion.div
        variants={{ hidden: { y: -20, opacity: 0 }, show: { y: 0, opacity: 1 } }}
        className="flex flex-col xl:flex-row justify-between items-start xl:items-center gap-4 bg-white/5 p-4 rounded-2xl border border-white/10 backdrop-blur-xl shadow-lg"
      >
        <div className="flex flex-wrap gap-3 w-full xl:w-auto">
          <select className="bg-black/20 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-slate-300 focus:border-[#8BF5E6] outline-none cursor-pointer hover:bg-white/5 transition-colors w-full sm:w-auto font-hindi">
            <option>📍 सभी स्थान</option>
            <option>रायगढ़</option>
            <option>खरसिया</option>
          </select>
          <select className="bg-black/20 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-slate-300 focus:border-[#8BF5E6] outline-none cursor-pointer hover:bg-white/5 transition-colors w-full sm:w-auto font-hindi">
            <option>📑 सभी विषय</option>
            <option>विकास कार्य</option>
            <option>सामाजिक</option>
          </select>
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <input type="date" className="flex-1 bg-black/20 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-slate-300 outline-none" />
            <span className="text-slate-500 text-sm font-hindi">से</span>
            <input type="date" className="flex-1 bg-black/20 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-slate-300 outline-none" />
          </div>
        </div>

        <div className="flex gap-2 w-full xl:w-auto">
          <button
            onClick={handleDownloadExcel}
            className="flex-1 xl:flex-none justify-center items-center gap-2 px-6 py-2.5 bg-green-600/10 text-green-400 border border-green-500/20 rounded-xl hover:bg-green-600/20 transition-colors text-sm font-medium font-hindi"
          >
            <Download size={16} /> एक्सेल
          </button>
          <button
            onClick={handleDownloadPDF}
            className="flex-1 xl:flex-none justify-center items-center gap-2 px-6 py-2.5 bg-red-600/10 text-red-400 border border-red-500/20 rounded-xl hover:bg-red-600/20 transition-colors text-sm font-medium font-hindi"
          >
            <Download size={16} /> पीडीएफ
          </button>
        </div>
      </motion.div>

      {/* Main Grid Layout - 9 Sections - Responsive grid to prevent overlap */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

        {/* 1. Event Type Analysis */}
        <AnimatedGlassCard title="इवेंट प्रकार विश्लेषण" className="lg:col-span-1 min-h-[350px]">
          <CustomPieChart
            data={eventTypeData}
            height={280}
            centerLabel={
              <>
                <span className="text-3xl font-bold text-white">100%</span>
                <p className="text-xs text-slate-400 font-hindi">कुल</p>
              </>
            }
          />
        </AnimatedGlassCard>

        {/* 2. Geo Mapping & Hierarchy (Spans 2 columns, extra height to prevent bleed) */}
        <AnimatedGlassCard
          className="lg:col-span-2 min-h-[500px] flex flex-col"
          title="भू-मानचित्रण एवं कवरेज"
          action={
            <div className="flex bg-black/20 rounded-lg p-1 border border-white/5">
              <button
                onClick={() => setGeoViewMode('map')}
                className={`px-3 py-1.5 rounded-md text-xs flex items-center gap-1 transition-all font-hindi ${geoViewMode === 'map' ? 'bg-[#8BF5E6] text-[#0f172a] font-bold shadow-lg' : 'text-slate-400 hover:text-white'}`}
              >
                <Map size={12} /> मानचित्र
              </button>
              <button
                onClick={() => setGeoViewMode('hierarchy')}
                className={`px-3 py-1.5 rounded-md text-xs flex items-center gap-1 transition-all font-hindi ${geoViewMode === 'hierarchy' ? 'bg-[#8BF5E6] text-[#0f172a] font-bold shadow-lg' : 'text-slate-400 hover:text-white'}`}
              >
                <Share2 size={12} /> पदानुक्रम
              </button>
            </div>
          }
        >
          <div className="flex flex-col gap-4 h-full">
            {/* Visualization Container with responsive height */}
            <div className="flex-1 min-h-[350px] w-full rounded-xl overflow-hidden relative bg-[#0f172a]">
              {geoViewMode === 'map' ? <MapBoxVisual /> : <HierarchyMindMap />}
            </div>

            {/* Quick Stats Grid inside Geo Card - Pushed to bottom */}
            <div className="grid grid-cols-3 gap-4 mt-auto">
              <div className="p-3 bg-white/5 rounded-xl text-center border border-white/5">
                <NumberTicker value={5} className="text-2xl font-bold text-[#8BF5E6]" prefix="" />
                <div className="text-xs text-slate-400 mt-1 font-hindi">कुल जिले</div>
              </div>
              <div className="p-3 bg-white/5 rounded-xl text-center border border-white/5">
                <NumberTicker value={78} className="text-2xl font-bold text-blue-400" suffix="%" />
                <div className="text-xs text-slate-400 mt-1 font-hindi">कवरेज</div>
              </div>
              <div className="p-3 bg-white/5 rounded-xl text-center border border-white/5">
                <NumberTicker value={142} className="text-2xl font-bold text-purple-400" />
                <div className="text-xs text-slate-400 mt-1 font-hindi">ग्राम दौरे</div>
              </div>
            </div>
          </div>
        </AnimatedGlassCard>

        {/* 3. Tour Coverage */}
        <AnimatedGlassCard title="टूर कवरेज विश्लेषण" className="min-h-[300px]">
          <div className="space-y-4">
            <div className="flex justify-between items-center p-4 bg-white/5 rounded-xl border border-white/5">
              <span className="text-sm text-slate-300 font-hindi">औसत जुड़ाव</span>
              <span className="font-bold text-[#8BF5E6] text-lg">4.8k</span>
            </div>
            <div className="flex justify-between items-center p-4 bg-white/5 rounded-xl border border-white/5">
              <span className="text-sm text-slate-300 font-hindi">सक्रिय अवधि</span>
              <span className="font-bold text-blue-400 text-lg">12 <span className="text-sm font-hindi text-slate-300">दिन</span></span>
            </div>
            <div className="pt-2">
              <h4 className="text-xs uppercase text-slate-500 font-bold mb-3 font-hindi">शीर्ष स्थान</h4>
              <ul className="space-y-2 text-sm text-slate-300">
                <li className="flex justify-between p-2 hover:bg-white/5 rounded-lg transition-colors cursor-default">
                  <span className="font-hindi">1. खरसिया</span>
                  <span className="text-[#8BF5E6] font-mono">45 <span className="font-hindi text-slate-400">दौरे</span></span>
                </li>
                <li className="flex justify-between p-2 hover:bg-white/5 rounded-lg transition-colors cursor-default">
                  <span className="font-hindi">2. घरघोड़ा</span>
                  <span className="text-blue-400 font-mono">32 <span className="font-hindi text-slate-400">दौरे</span></span>
                </li>
                <li className="flex justify-between p-2 hover:bg-white/5 rounded-lg transition-colors cursor-default">
                  <span className="font-hindi">3. तमनार</span>
                  <span className="text-purple-400 font-mono">28 <span className="font-hindi text-slate-400">दौरे</span></span>
                </li>
              </ul>
            </div>
          </div>
        </AnimatedGlassCard>

        {/* 4. Development Work */}
        <AnimatedGlassCard title="विकास कार्य विश्लेषण" className="min-h-[300px]">
          <CustomBarChart
            data={developmentData}
            xKey="name"
            dataKey="value"
            height={250}
          />
        </AnimatedGlassCard>

        {/* 5. Community Outreach */}
        <AnimatedGlassCard title="समाज आधारित पहुँच" className="min-h-[300px]">
          <div className="flex flex-wrap gap-2 mb-6 content-start">
            {['युवा', 'किसान', 'महिला', 'आदिवासी', 'शिक्षक', 'छात्र'].map((tag, i) => (
              <motion.span
                key={i}
                whileHover={{ scale: 1.1 }}
                className="px-3 py-1.5 bg-white/10 rounded-full text-xs text-slate-300 border border-white/10 hover:bg-white/20 cursor-default transition-colors font-hindi"
              >
                {tag}
              </motion.span>
            ))}
          </div>
          <div className="space-y-4 mt-auto">
            <div className="flex justify-between text-sm text-slate-300 border-b border-white/5 pb-3">
              <span className="font-hindi">विशिष्ट समाज</span> <NumberTicker value={12} className="text-white font-bold text-lg" />
            </div>
            <div className="flex justify-between text-sm text-slate-300 border-b border-white/5 pb-3">
              <span className="font-hindi">कुल उल्लेख</span> <NumberTicker value={845} className="text-white font-bold text-lg" />
            </div>
          </div>
        </AnimatedGlassCard>

        {/* 6. Schemes */}
        <AnimatedGlassCard title="योजना विश्लेषण" className="min-h-[300px]">
          <div className="space-y-4">
            {schemeData.map((scheme, idx) => (
              <div key={idx} className="relative pt-1 group">
                <div className="flex mb-2 items-center justify-between">
                  <span className="text-xs font-semibold text-slate-300 group-hover:text-white transition-colors font-hindi">{scheme.name}</span>
                  <span className="text-xs font-semibold text-[#8BF5E6]">{scheme.count}</span>
                </div>
                <div className="overflow-hidden h-2 text-xs flex rounded-full bg-white/10">
                  <motion.div
                    initial={{ width: 0 }}
                    whileInView={{ width: `${(scheme.count / 150) * 100}%` }}
                    transition={{ duration: 1.2, delay: 0.1 * idx }}
                    className="shadow-[0_0_15px_rgba(59,130,246,0.6)] bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full"
                  />
                </div>
              </div>
            ))}
          </div>
        </AnimatedGlassCard>

        {/* 7. Target Groups */}
        <AnimatedGlassCard title="लक्षित वर्ग विश्लेषण" className="min-h-[400px]">
          <div className="grid grid-cols-2 gap-4 h-full content-start">
            <div className="p-4 bg-pink-500/10 border border-pink-500/20 rounded-xl flex flex-col items-center justify-center hover:bg-pink-500/20 transition-all hover:-translate-y-1 min-h-[140px]">
              <Users className="text-pink-400 mb-3" size={24} />
              <NumberTicker value={35} className="text-3xl font-bold text-white" suffix="%" />
              <span className="text-xs text-pink-300 mt-1 font-hindi">महिला</span>
            </div>
            <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-xl flex flex-col items-center justify-center hover:bg-yellow-500/20 transition-all hover:-translate-y-1 min-h-[140px]">
              <Users className="text-yellow-400 mb-3" size={24} />
              <NumberTicker value={28} className="text-3xl font-bold text-white" suffix="%" />
              <span className="text-xs text-yellow-300 mt-1 font-hindi">युवा</span>
            </div>
            <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-xl flex flex-col items-center justify-center hover:bg-green-500/20 transition-all hover:-translate-y-1 min-h-[140px]">
              <Users className="text-green-400 mb-3" size={24} />
              <NumberTicker value={22} className="text-3xl font-bold text-white" suffix="%" />
              <span className="text-xs text-green-300 mt-1 font-hindi">किसान</span>
            </div>
            <div className="p-4 bg-slate-500/10 border border-slate-500/20 rounded-xl flex flex-col items-center justify-center hover:bg-slate-500/20 transition-all hover:-translate-y-1 min-h-[140px]">
              <Users className="text-slate-400 mb-3" size={24} />
              <NumberTicker value={15} className="text-3xl font-bold text-white" suffix="%" />
              <span className="text-xs text-slate-300 mt-1 font-hindi">वरिष्ठ</span>
            </div>
          </div>
        </AnimatedGlassCard>

        {/* 8. Thematic */}
        <AnimatedGlassCard title="विषयगत विश्लेषण" className="min-h-[300px]">
          <div className="space-y-3">
            <div className="flex items-center gap-4 p-3 bg-white/5 rounded-xl border border-white/5 hover:bg-white/10 transition-colors">
              <div className="p-2 bg-yellow-500/20 rounded-lg text-yellow-400"><Lightbulb size={20} /></div>
              <span className="text-sm text-slate-300 font-medium font-hindi">रोजगार एवं नौकरी</span>
            </div>
            <div className="flex items-center gap-4 p-3 bg-white/5 rounded-xl border border-white/5 hover:bg-white/10 transition-colors">
              <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400"><Building size={20} /></div>
              <span className="text-sm text-slate-300 font-medium font-hindi">बुनियादी ढांचा</span>
            </div>
            <div className="flex items-center gap-4 p-3 bg-white/5 rounded-xl border border-white/5 hover:bg-white/10 transition-colors">
              <div className="p-2 bg-red-500/20 rounded-lg text-red-400"><Target size={20} /></div>
              <span className="text-sm text-slate-300 font-medium font-hindi">कानून व्यवस्था</span>
            </div>
          </div>
          <div className="mt-6 h-[100px] bg-black/20 rounded-xl flex items-center justify-center border border-white/5 group cursor-pointer hover:border-[#8BF5E6]/30 transition-colors">
            <span className="text-xs text-slate-500 group-hover:text-[#8BF5E6] transition-colors font-hindi">शब्द-मेघ (Wordcloud) देखें</span>
          </div>
        </AnimatedGlassCard>

        {/* 9. Raigarh Section */}
        <AnimatedGlassCard title="रायगढ़ विधानसभा" className="lg:col-span-1 min-h-[400px]">
          <div className="flex flex-col h-full">
            <div className="flex items-center gap-6 mb-6 bg-white/5 p-4 rounded-xl border border-white/5">
              <div className="relative w-16 h-16 flex-shrink-0">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="#1e293b"
                    strokeWidth="3"
                  />
                  <motion.path
                    initial={{ pathLength: 0 }}
                    whileInView={{ pathLength: 0.85 }}
                    transition={{ duration: 2, ease: "easeInOut" }}
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="#8BF5E6"
                    strokeWidth="3"
                    strokeDasharray="85, 100"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center text-sm font-bold text-white">85%</div>
              </div>
              <div>
                <h4 className="font-bold text-white mb-1 font-hindi">कवरेज प्रगति</h4>
                <p className="text-[10px] text-slate-400 font-hindi">लक्ष्य: दिसंबर तक 100%</p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 text-center mb-6">
              <div className="bg-white/5 p-2 rounded-lg border border-white/5">
                <NumberTicker value={1200} className="block font-bold text-white text-sm" />
                <span className="text-[10px] text-slate-400 font-hindi">पसंद</span>
              </div>
              <div className="bg-white/5 p-2 rounded-lg border border-white/5">
                <NumberTicker value={450} className="block font-bold text-white text-sm" />
                <span className="text-[10px] text-slate-400 font-hindi">रीपोस्ट</span>
              </div>
              <div className="bg-white/5 p-2 rounded-lg border border-white/5">
                <NumberTicker value={89} className="block font-bold text-white text-sm" />
                <span className="text-[10px] text-slate-400 font-hindi">उत्तर</span>
              </div>
            </div>

            <div className="bg-black/20 rounded-xl p-4 overflow-hidden border border-white/5 mt-auto">
              <h4 className="text-[10px] uppercase text-slate-500 font-bold mb-3 tracking-wider font-hindi">स्थानीय कार्यक्रम</h4>
              <ul className="space-y-3 text-sm">
                <li className="flex justify-between items-center border-b border-white/5 pb-2 last:border-0 last:pb-0">
                  <span className="text-slate-300 font-hindi">वार्ड 04 निरीक्षण</span>
                  <span className="text-[#8BF5E6] text-[10px] font-bold bg-[#8BF5E6]/10 px-2 py-1 rounded font-hindi">आज</span>
                </li>
                <li className="flex justify-between items-center border-b border-white/5 pb-2 last:border-0 last:pb-0">
                  <span className="text-slate-300 font-hindi">टाउन हॉल बैठक</span>
                  <span className="text-blue-400 text-[10px] font-bold bg-blue-400/10 px-2 py-1 rounded font-hindi">कल</span>
                </li>
              </ul>
            </div>
          </div>
        </AnimatedGlassCard>

      </div>
    </motion.div>
  );
};

export default AnalyticsDashboard;
