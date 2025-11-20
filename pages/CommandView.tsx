
import React from 'react';
import { Activity, Database, Server, Terminal, Edit, ToggleRight, Download, Upload, AlertCircle } from 'lucide-react';
import AnimatedGlassCard from '../components/AnimatedGlassCard';

const HealthCard = ({ label, status }: { label: string, status: 'good' | 'warning' | 'bad' }) => (
  <div className="p-4 bg-white/5 rounded-xl border border-white/10 flex items-center justify-between hover:bg-white/10 transition-colors group">
    <span className="text-slate-300 text-sm font-medium group-hover:text-white transition-colors font-hindi">{label}</span>
    <div className="flex items-center gap-2">
       <span className={`text-xs font-bold font-hindi ${status === 'good' ? 'text-green-400' : status === 'warning' ? 'text-yellow-400' : 'text-red-400'}`}>
          {status === 'good' ? 'स्वस्थ' : status === 'warning' ? 'कमजोर' : 'बंद'}
       </span>
       <div className={`w-2.5 h-2.5 rounded-full ${status === 'good' ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)] animate-pulse' : status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'}`} />
    </div>
  </div>
);

const CommandView = () => {
  return (
    <div className="space-y-8 pb-10">
      
      {/* Section 1: System Health Overview */}
      <AnimatedGlassCard className="p-6" delay={0.1}>
        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2 font-hindi">
          <Activity className="text-[#8BF5E6]" /> सिस्टम स्थिति अवलोकन
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
           <HealthCard label="API गेटवे" status="good" />
           <HealthCard label="डेटाबेस (PostgreSQL)" status="good" />
           <HealthCard label="FAISS वेक्टर स्टोर" status="warning" />
           <HealthCard label="ट्विटर अंतर्ग्रहण (Ingestion)" status="good" />
           <HealthCard label="जेमिनी AI सेवा" status="good" />
           <HealthCard label="फ्रंटएंड बिल्ड" status="good" />
        </div>
      </AnimatedGlassCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Section 2: Configuration */}
        <AnimatedGlassCard title="⚙️ डैशबोर्ड कॉन्फ़िगरेशन" delay={0.2}>
           <div className="space-y-5">
              <div className="space-y-2">
                 <label className="text-xs text-slate-400 uppercase font-bold font-hindi">डैशबोर्ड शीर्षक</label>
                 <div className="flex gap-2">
                    <input type="text" defaultValue="सोशल मीडिया एनालिटिक्स डैशबोर्ड" className="flex-1 bg-black/20 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-[#8BF5E6] outline-none font-hindi" />
                    <button className="p-2.5 bg-white/10 rounded-xl hover:bg-white/20 text-white"><Edit size={18} /></button>
                 </div>
              </div>
              
              <div className="space-y-3">
                 <label className="text-xs text-slate-400 uppercase font-bold font-hindi">सक्रिय मॉड्यूल</label>
                 <div className="grid grid-cols-2 gap-3">
                    {['भू-मानचित्रण', 'टूर विश्लेषण', 'योजनाएँ', 'समुदाय'].map(m => (
                       <div key={m} className="flex items-center justify-between p-3 bg-white/5 rounded-xl border border-white/5 hover:bg-white/10 transition-colors">
                          <span className="text-sm text-slate-300 font-hindi">{m}</span>
                          <ToggleRight className="text-[#8BF5E6] cursor-pointer w-6 h-6" />
                       </div>
                    ))}
                 </div>
              </div>
           </div>
        </AnimatedGlassCard>

        {/* Section 3: Pipeline Monitor */}
        <AnimatedGlassCard title="🔄 डेटाबेस और पाइपलाइन मॉनिटर" delay={0.3}>
           <div className="space-y-5">
              <div className="grid grid-cols-2 gap-4">
                 <div className="p-4 bg-black/20 rounded-xl border border-white/5 text-center">
                    <div className="text-3xl font-bold text-blue-400 mb-1">12.5k</div>
                    <div className="text-xs text-slate-500 font-hindi">कुल ट्वीट्स</div>
                 </div>
                 <div className="p-4 bg-black/20 rounded-xl border border-white/5 text-center">
                    <div className="text-3xl font-bold text-yellow-400 mb-1">142</div>
                    <div className="text-xs text-slate-500 font-hindi">पार्सिंग लंबित</div>
                 </div>
              </div>
              <div className="h-[180px] bg-black/40 rounded-xl border border-white/5 p-4 font-mono text-xs text-green-400 overflow-y-auto leading-relaxed scrollbar-thin">
                 <div>[10:42:15] अंतर्ग्रहण सेवा शुरू हुई...</div>
                 <div>[10:42:18] ट्विटर API v2 से जुड़ा</div>
                 <div>[10:42:22] बैच #402 संसाधित (50 ट्वीट्स)</div>
                 <div>[10:42:25] जेमिनी API विलंबता: 240ms</div>
                 <div className="text-yellow-400">[10:42:28] चेतावनी: दर सीमा निकट है</div>
                 <div>[10:42:30] FAISS इंडेक्स अपडेट किया गया</div>
              </div>
           </div>
        </AnimatedGlassCard>

      </div>

      {/* Section 4: Advanced Tools */}
      <AnimatedGlassCard title="🔬 टेलीमेट्री और डिबग" delay={0.4}>
         <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="p-5 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-all text-left group">
               <Server className="text-slate-400 group-hover:text-[#8BF5E6] mb-3" size={24} />
               <h4 className="font-bold text-white mb-1 font-hindi">API विलंबता</h4>
               <p className="text-xs text-slate-500 font-hindi">एंडपॉइंट प्रदर्शन देखें</p>
            </button>
            <button className="p-5 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-all text-left group">
               <AlertCircle className="text-slate-400 group-hover:text-red-400 mb-3" size={24} />
               <h4 className="font-bold text-white mb-1 font-hindi">त्रुटि तालिकाएँ</h4>
               <p className="text-xs text-slate-500 font-hindi">हाल की पार्सिंग विफलताएँ देखें</p>
            </button>
            <button className="p-5 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-all text-left group">
               <Terminal className="text-slate-400 group-hover:text-purple-400 mb-3" size={24} />
               <h4 className="font-bold text-white mb-1 font-hindi">ट्रेस स्ट्रीम</h4>
               <p className="text-xs text-slate-500 font-hindi">लाइव लॉग टेलिंग</p>
            </button>
         </div>
         <div className="mt-8 pt-6 border-t border-white/10 flex gap-4">
            <button className="flex items-center gap-2 px-5 py-2.5 bg-blue-600/10 text-blue-400 border border-blue-500/20 rounded-xl hover:bg-blue-600/20 transition-colors text-sm font-medium font-hindi">
               <Download size={16} /> कॉन्फ़िग निर्यात
            </button>
            <button className="flex items-center gap-2 px-5 py-2.5 bg-purple-600/10 text-purple-400 border border-purple-500/20 rounded-xl hover:bg-purple-600/20 transition-colors text-sm font-medium font-hindi">
               <Upload size={16} /> कॉन्फ़िग आयात
            </button>
         </div>
      </AnimatedGlassCard>

    </div>
  );
};

export default CommandView;
