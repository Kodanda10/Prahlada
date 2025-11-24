import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Activity, Server, Database, Brain, Map as MapIcon,
  RefreshCw, AlertTriangle, CheckCircle, XCircle,
  Settings, Edit3, ToggleLeft, ToggleRight, Terminal, Download
} from 'lucide-react';
import AnimatedGlassCard from '../components/AnimatedGlassCard';
import { apiService } from '../services/api';
import { useConfig } from '../contexts/ConfigContext';
import NumberTicker from '../components/NumberTicker';
import { exportToExcel, exportToPDF } from '../utils/export';

// --- Types ---
interface SystemHealth {
  cpu_usage: number;
  memory_usage: number;
  memory_total_gb: number;
  services: {
    [key: string]: { status: 'up' | 'down'; latency_ms?: number; details?: string };
  };
  parser_uptime_seconds: number;
  api_error_rate: number;
  p95_latency_ms: number;
}

interface AnalyticsHealth {
  data_freshness: {
    status: 'fresh' | 'stale';
    last_updated: number;
    source: string;
  };
  modules: {
    [key: string]: { status: 'fresh' | 'stale'; cache_hit: boolean };
  };
}

// --- Components ---

const StatusBadge = ({ status }: { status: 'up' | 'down' | 'fresh' | 'stale' }) => {
  const isGood = status === 'up' || status === 'fresh';
  return (
    <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider flex items-center gap-1 ${isGood ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-red-500/20 text-red-400 border border-red-500/30'
      }`}>
      {isGood ? <CheckCircle size={10} /> : <XCircle size={10} />}
      {status}
    </span>
  );
};

const ModuleWrapper = ({ id, children }: { id: string, children: React.ReactNode }) => {
  const { config } = useConfig();
  if (config && config.modules[id] === false) return null;
  return <>{children}</>;
};

const ControlHub = () => {
  const { config, updateConfig } = useConfig();
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [analyticsHealth, setAnalyticsHealth] = useState<AnalyticsHealth | null>(null);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const handleDownloadExcel = () => {
    if (!systemHealth) return;
    const data = [
      { Category: 'System', Metric: 'CPU', Value: systemHealth.cpu_usage + '%' },
      { Category: 'System', Metric: 'Memory', Value: systemHealth.memory_usage + '%' },
      { Category: 'API', Metric: 'Latency P95', Value: systemHealth.p95_latency_ms + 'ms' },
      { Category: 'API', Metric: 'Error Rate', Value: systemHealth.api_error_rate + '%' },
      ...Object.entries(systemHealth.services).map(([k, v]) => ({
        Category: 'Service', Metric: k, Value: v.status
      }))
    ];
    exportToExcel(data, 'system_health_report');
  };

  const handleDownloadPDF = () => {
    if (!systemHealth) return;
    const data = [
      { Category: 'System', Metric: 'CPU', Value: systemHealth.cpu_usage + '%' },
      { Category: 'System', Metric: 'Memory', Value: systemHealth.memory_usage + '%' },
      { Category: 'API', Metric: 'Latency P95', Value: systemHealth.p95_latency_ms + 'ms' },
      { Category: 'API', Metric: 'Error Rate', Value: systemHealth.api_error_rate + '%' },
      ...Object.entries(systemHealth.services).map(([k, v]) => ({
        Category: 'Service', Metric: k, Value: v.status
      }))
    ];
    exportToPDF(data, 'system_health_report');
  };

  // Fallback data for when backend is unreachable
  const fallbackSystemHealth: SystemHealth = {
    cpu_usage: 0,
    memory_usage: 0,
    memory_total_gb: 0,
    services: {
      ollama: { status: 'down', details: 'Unreachable' },
      cognitive_engine: { status: 'down', details: 'Unreachable' },
      database_file: { status: 'down', details: 'Unreachable' },
      mapbox_integration: { status: 'down', details: 'Unreachable' }
    },
    parser_uptime_seconds: 0,
    api_error_rate: 1,
    p95_latency_ms: 0
  };

  const fallbackAnalyticsHealth: AnalyticsHealth = {
    data_freshness: { status: 'stale', last_updated: 0, source: 'Unknown' },
    modules: {
      controlhub_header_systemhealth: { status: 'stale', cache_hit: false },
      controlhub_grid_analytics_sync: { status: 'stale', cache_hit: false }
    }
  };

  const fetchData = async () => {
    try {
      const sys = await apiService.get('/health/system') as SystemHealth;
      const ana = await apiService.get('/health/analytics') as AnalyticsHealth;

      if (sys) {
        // Merge with fallback to guard against missing keys from the backend
        const normalizedSys: SystemHealth = {
          ...fallbackSystemHealth,
          ...sys,
          services: {
            ...fallbackSystemHealth.services,
            ...(sys.services || {})
          }
        };
        setSystemHealth(normalizedSys);
      } else {
        setSystemHealth(fallbackSystemHealth);
      }

      if (ana) setAnalyticsHealth(ana);
      else setAnalyticsHealth(fallbackAnalyticsHealth);

      setLastRefresh(new Date());
    } catch (e) {
      console.error("Failed to fetch health data", e);
      // Use fallback data on error so the UI still renders
      setSystemHealth(fallbackSystemHealth);
      setAnalyticsHealth(fallbackAnalyticsHealth);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  // Only block if config is missing. Health data now has fallbacks.
  if (!config) {
    return (
      <div className="flex items-center justify-center h-[50vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#8BF5E6]"></div>
      </div>
    );
  }

  // Ensure health data exists before rendering (it should due to fallbacks, but for safety)
  if (!systemHealth || !analyticsHealth) {
    return null; // Should not happen with fallbacks
  }

  return (
    <div className="space-y-6 pb-20">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white font-hindi">कंट्रोल हब (Control Hub)</h1>
          <p className="text-slate-400 text-sm font-hindi">सिस्टम स्वास्थ्य और कॉन्फ़िगरेशन केंद्र</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex gap-2">
            <button
              onClick={handleDownloadExcel}
              className="p-2 bg-green-600/10 text-green-400 border border-green-500/20 rounded-lg hover:bg-green-600/20 transition-colors"
              title="Download Excel"
            >
              <Download size={16} />
            </button>
            <button
              onClick={handleDownloadPDF}
              className="p-2 bg-red-600/10 text-red-400 border border-red-500/20 rounded-lg hover:bg-red-600/20 transition-colors"
              title="Download PDF"
            >
              <Download size={16} />
            </button>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <RefreshCw size={12} className="animate-spin-slow" />
            Updated: {lastRefresh.toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* A. System Health Overview */}
      <ModuleWrapper id="controlhub_header_systemhealth">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <AnimatedGlassCard className="p-4">
            <div className="flex items-center gap-3 mb-2">
              <Activity className="text-[#8BF5E6]" size={20} />
              <span className="text-sm text-slate-300 font-hindi">API स्वास्थ्य</span>
            </div>
            <div className="flex justify-between items-end">
              <div>
                <div className="text-2xl font-bold text-white">
                  {systemHealth.p95_latency_ms}ms
                </div>
                <div className="text-xs text-slate-500">P95 Latency</div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-green-400">
                  {(100 - systemHealth.api_error_rate * 100).toFixed(1)}%
                </div>
                <div className="text-xs text-slate-500">Success Rate</div>
              </div>
            </div>
          </AnimatedGlassCard>

          <AnimatedGlassCard className="p-4">
            <div className="flex items-center gap-3 mb-2">
              <Server className="text-blue-400" size={20} />
              <span className="text-sm text-slate-300 font-hindi">संसाधन (Resources)</span>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">CPU</span>
                <span className="text-white">{systemHealth.cpu_usage}%</span>
              </div>
              <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
                <div className="bg-blue-500 h-full" style={{ width: `${systemHealth.cpu_usage}%` }} />
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">RAM</span>
                <span className="text-white">{systemHealth.memory_usage}% ({systemHealth.memory_total_gb}GB)</span>
              </div>
              <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
                <div className="bg-purple-500 h-full" style={{ width: `${systemHealth.memory_usage}%` }} />
              </div>
            </div>
          </AnimatedGlassCard>

          <AnimatedGlassCard className="p-4">
            <div className="flex items-center gap-3 mb-2">
              <Brain className="text-pink-400" size={20} />
              <span className="text-sm text-slate-300 font-hindi">AI इंजन</span>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-400">Ollama</span>
                <StatusBadge status={systemHealth.services.ollama.status} />
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-400">Cognitive</span>
                <StatusBadge status={systemHealth.services.cognitive_engine.status} />
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-400">Parser</span>
                <span className="text-xs text-green-400 font-mono">
                  {Math.floor(systemHealth.parser_uptime_seconds / 3600)}h {(Math.floor(systemHealth.parser_uptime_seconds % 3600) / 60).toFixed(0)}m
                </span>
              </div>
            </div>
          </AnimatedGlassCard>

          <AnimatedGlassCard className="p-4">
            <div className="flex items-center gap-3 mb-2">
              <Database className="text-yellow-400" size={20} />
              <span className="text-sm text-slate-300 font-hindi">डेटा पाइपलाइन</span>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-400">Database</span>
                <StatusBadge status={systemHealth.services.database_file.status} />
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-400">Mapbox</span>
                <StatusBadge status={systemHealth.services.mapbox_integration.status} />
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-400">Freshness</span>
                <StatusBadge status={analyticsHealth.data_freshness.status} />
              </div>
            </div>
          </AnimatedGlassCard>
        </div>
      </ModuleWrapper>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* B. Analytics Sync Health */}
        <ModuleWrapper id="controlhub_grid_analytics_sync">
          <AnimatedGlassCard title="एनालिटिक्स सिंक स्थिति" className="min-h-[300px]">
            <div className="space-y-4">
              <div className="p-3 bg-white/5 rounded-lg border border-white/5 flex justify-between items-center">
                <div>
                  <div className="text-xs text-slate-400 font-hindi">डेटा स्रोत</div>
                  <div className="text-sm font-mono text-[#8BF5E6]">{analyticsHealth.data_freshness.source}</div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-slate-400 font-hindi">अंतिम अपडेट</div>
                  <div className="text-xs text-white">
                    {new Date(analyticsHealth.data_freshness.last_updated * 1000).toLocaleString()}
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-500 uppercase font-hindi">मॉड्यूल स्थिति</h4>
                {Object.entries(analyticsHealth.modules).map(([key, val]) => (
                  <div key={key} className="flex justify-between items-center p-2 hover:bg-white/5 rounded transition-colors">
                    <span className="text-sm text-slate-300 capitalize">{key.replace('_', ' ')}</span>
                    <div className="flex items-center gap-2">
                      <span className={`text-[10px] px-1.5 py-0.5 rounded ${val.cache_hit ? 'bg-blue-500/20 text-blue-300' : 'bg-yellow-500/20 text-yellow-300'}`}>
                        {val.cache_hit ? 'CACHE' : 'LIVE'}
                      </span>
                      <StatusBadge status={val.status} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </AnimatedGlassCard>
        </ModuleWrapper>

        {/* D. Title & Header Editor */}
        <ModuleWrapper id="controlhub_panel_title_editor">
          <AnimatedGlassCard title="शीर्षक संपादक (Title Editor)" className="min-h-[300px] lg:col-span-2">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(config.titles).map(([key, value]) => (
                <div key={key} className="space-y-1">
                  <label className="text-xs text-slate-500 font-mono">{key}</label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={value}
                      onChange={(e) => updateConfig('titles', key, e.target.value)}
                      className="flex-1 bg-black/20 border border-white/10 rounded px-3 py-2 text-sm text-white focus:border-[#8BF5E6] outline-none font-hindi"
                    />
                    <button className="p-2 bg-white/5 hover:bg-white/10 rounded text-slate-400 hover:text-white">
                      <Edit3 size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </AnimatedGlassCard>
        </ModuleWrapper>
      </div>

      {/* E. Module Visibility Control */}
      <ModuleWrapper id="controlhub_panel_api_health">
        <AnimatedGlassCard title="मॉड्यूल दृश्यता (Module Visibility)" className="min-h-[200px]">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {Object.entries(config.modules).map(([key, enabled]) => (
              <div key={key} className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/5">
                <span className="text-xs text-slate-300 font-mono truncate mr-2" title={key}>
                  {key.replace('controlhub_', '').replace('analytics_', '')}
                </span>
                <button
                  onClick={() => updateConfig('modules', key, !enabled)}
                  className={`transition-colors ${enabled ? 'text-[#8BF5E6]' : 'text-slate-600'}`}
                >
                  {enabled ? <ToggleRight size={24} /> : <ToggleLeft size={24} />}
                </button>
              </div>
            ))}
          </div>
        </AnimatedGlassCard>
      </ModuleWrapper>

      {/* API Health Matrix */}
      <ModuleWrapper id="controlhub_panel_api_health">
        <AnimatedGlassCard title="API और बैकएंड मैट्रिक्स" className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/10 text-xs text-slate-500 uppercase font-hindi">
                  <th className="p-3">सेवा (Service)</th>
                  <th className="p-3">स्थिति (Status)</th>
                  <th className="p-3">विवरण (Details)</th>
                  <th className="p-3">विलंबता (Latency)</th>
                </tr>
              </thead>
              <tbody className="text-sm text-slate-300">
                {Object.entries(systemHealth.services).map(([name, info]) => (
                  <tr key={name} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="p-3 font-mono text-xs">{name}</td>
                    <td className="p-3"><StatusBadge status={info.status} /></td>
                    <td className="p-3 text-xs text-slate-400">{info.details || '-'}</td>
                    <td className="p-3 text-xs font-mono">{info.latency_ms || 0}ms</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </AnimatedGlassCard>
      </ModuleWrapper>

    </div>
  );
};

export default ControlHub;
