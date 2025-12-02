
import React, { useEffect, useState } from 'react';
import { Activity, CheckCircle2, AlertCircle, Clock } from 'lucide-react';
import AnimatedGlassCard from '../components/AnimatedGlassCard';
import NumberTicker from '../components/NumberTicker';
import { Stats } from '../types';
import CustomLineChart from '../components/charts/CustomLineChart';
import CustomPieChart from '../components/charts/CustomPieChart';
import { PulseButton, LiquidLoader } from '../components/interactions/RiveLikeIcons';

const StatCard = ({ label, value, subLabel, icon: Icon, color, delay }: any) => (
  <AnimatedGlassCard className="relative overflow-hidden group" delay={delay}>
    <div className={`absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity duration-500 ${color} scale-150`}>
      <Icon size={80} />
    </div>
    <div className="relative z-10">
      <p className="text-slate-400 text-sm font-medium mb-1 uppercase tracking-wider font-hindi">{label}</p>
      <h2 className="text-5xl font-bold text-white tracking-tight mb-2">
        <NumberTicker value={value} />
      </h2>
      {subLabel && <p className="text-xs text-slate-500 font-hindi">{subLabel}</p>}
    </div>
  </AnimatedGlassCard>
);

const HealthIndicator = ({ label, status, details }: { label: string, status: 'good' | 'warning' | 'error', details: string }) => (
  <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5 hover:bg-white/10 transition-colors">
    <div className="flex items-center gap-3">
      <div className={`w-2.5 h-2.5 rounded-full ${status === 'good' ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)] animate-pulse' : status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'}`} />
      <span className="font-medium text-slate-200 font-hindi">{label}</span>
    </div>
    <span className="text-xs text-slate-400 font-mono bg-black/20 px-2 py-1 rounded">{details}</span>
  </div>
);

const Overview = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  // Mock Data for Hindi Display
  const timeSeriesData = [
    { day: 'सोम', events: 40 },
    { day: 'मंगल', events: 30 },
    { day: 'बुध', events: 55 },
    { day: 'गुरु', events: 45 },
    { day: 'शुक्र', events: 80 },
    { day: 'शनि', events: 65 },
    { day: 'रवि', events: 20 },
  ];

  const eventTypesData = [
    { name: 'बैठक', value: 35 },
    { name: 'दौरा', value: 25 },
    { name: 'उद्घाटन', value: 15 },
    { name: 'अन्य', value: 25 },
  ];

  const loadData = async () => {
    setLoading(true);
    try {
        // Using mock stats for robust demo, replace with real API later
        setTimeout(() => {
          setStats({
              total_tweets: 12450,
              parsed_success: 11200,
              pending: 840,
              errors: 410
          });
          setLoading(false);
        }, 1500);
    } catch (e) {
        console.error("Failed to load overview data", e);
        setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-full w-full items-center justify-center min-h-[500px]">
        <LiquidLoader />
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-10">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2 font-hindi">डैशबोर्ड सारांश</h2>
          <p className="text-slate-400 font-hindi">सिस्टम की स्थिति और प्रमुख मेट्रिक्स</p>
        </div>
        <div className="text-right hidden sm:block">
          <PulseButton onClick={loadData} label="रिफ्रेश करें" />
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard label="कुल ट्वीट" value={stats?.total_tweets || 0} icon={Activity} color="text-blue-500" delay={0} />
        <StatCard label="सफल पार्स" value={stats?.parsed_success || 0} icon={CheckCircle2} color="text-green-500" delay={0.1} />
        <StatCard label="लंबित / री-क्यू" value={stats?.pending || 0} icon={Clock} color="text-yellow-500" delay={0.2} />
        <StatCard label="त्रुटियाँ" value={stats?.errors || 0} icon={AlertCircle} color="text-red-500" delay={0.3} />
      </div>

      {/* System Health */}
      <AnimatedGlassCard title="सिस्टम स्थिति (System Health)" delay={0.4}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <HealthIndicator label="अंतर्ग्रहण सेवा (Ingestion)" status="good" details="सक्रिय" />
          <HealthIndicator label="पार्सिंग पाइपलाइन" status="good" details="API: 8000 OK" />
          <HealthIndicator label="डेटाबेस कनेक्शन" status="good" details="जुड़ा हुआ (5ms)" />
        </div>
      </AnimatedGlassCard>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Line Chart */}
        <AnimatedGlassCard title="दैनिक कार्यक्रम रुझान" className="lg:col-span-2 min-h-[350px]" delay={0.5}>
          <CustomLineChart 
            data={timeSeriesData} 
            xKey="day" 
            dataKey="events" 
            height={280}
          />
        </AnimatedGlassCard>

        {/* Donut Chart */}
        <AnimatedGlassCard title="कार्यक्रम प्रकार वितरण" className="min-h-[350px]" delay={0.6}>
          <CustomPieChart 
            data={eventTypesData} 
            height={280}
            centerLabel={
               <>
                <span className="text-2xl font-bold text-white font-hindi">कुल</span>
              </>
            }
          />
        </AnimatedGlassCard>
      </div>
    </div>
  );
};

export default Overview;
