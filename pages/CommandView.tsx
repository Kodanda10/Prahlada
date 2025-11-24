import React from 'react';
import { Terminal, Shield, Activity, BookOpen } from 'lucide-react';
import AnimatedGlassCard from '../components/AnimatedGlassCard';
import GlassCard from '../components/GlassCard';

const CommandView: React.FC = () => {
  return (
    <div className="space-y-6">
      <AnimatedGlassCard
        title="कमान्ड कंसोल"
        className="min-h-[200px]"
        action={
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Terminal size={14} />
            <span className="font-hindi">सुरक्षित मोड</span>
          </div>
        }
      >
        <p className="text-slate-300 text-sm leading-relaxed font-hindi">
          यह सुरक्षित कंसोल व्यवस्थापकों के लिए त्वरित निदान, स्वास्थ्य जांच और बैकएंड सेवाओं की निगरानी का दृश्य प्रदान करता है।
          लाइव कमांड निष्पादन निष्क्रिय है; केवल-पढ़ने वाले विज़ुअल संकेत सक्रिय हैं।
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
          <GlassCard title="API Health" className="glass-card">
            <div className="flex items-center gap-2 text-sm text-slate-300">
              <Activity size={16} className="text-[#8BF5E6]" />
              <span>p95 latency snapshots</span>
            </div>
          </GlassCard>
          <GlassCard title="Security" className="glass-card">
            <div className="flex items-center gap-2 text-sm text-slate-300">
              <Shield size={16} className="text-green-400" />
              <span>Authentication enforced</span>
            </div>
          </GlassCard>
          <GlassCard title="Playbook" className="glass-card">
            <div className="flex items-center gap-2 text-sm text-slate-300">
              <BookOpen size={16} className="text-blue-400" />
              <span>Operational runbook</span>
            </div>
          </GlassCard>
        </div>
      </AnimatedGlassCard>
    </div>
  );
};

export default CommandView;
