
import React, { useState, useEffect } from 'react';
import { Search, Filter, Check, X as XIcon, AlertTriangle, ChevronRight, Terminal, RefreshCw } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import { ParsedEvent, ParsingStatus } from '../types';
import { fetchEvents, fetchStats } from '../services/api';

const StatusBadge = ({ status }: { status: string }) => {
  switch (status) {
    case 'SUCCESS':
      return <span className="px-2 py-1 rounded-full bg-green-500/20 text-green-400 text-xs border border-green-500/30 flex items-center gap-1 w-fit"><Check size={12} /> Success</span>;
    case 'FAILED':
      return <span className="px-2 py-1 rounded-full bg-red-500/20 text-red-400 text-xs border border-red-500/30 flex items-center gap-1 w-fit"><XIcon size={12} /> Failed</span>;
    case 'PARTIAL':
      return <span className="px-2 py-1 rounded-full bg-yellow-500/20 text-yellow-400 text-xs border border-yellow-500/30 flex items-center gap-1 w-fit"><AlertTriangle size={12} /> Partial</span>;
    default:
      return <span className="px-2 py-1 rounded-full bg-slate-500/20 text-slate-400 text-xs border border-slate-500/30 w-fit">Pending</span>;
  }
};

const DetailPanel = ({ event, onClose }: { event: ParsedEvent; onClose: () => void }) => {
  if (!event) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-full md:w-[480px] bg-[#0f172a]/95 backdrop-blur-xl border-l border-white/10 p-6 shadow-2xl transform transition-transform duration-300 z-[60] overflow-y-auto">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-white">ट्वीट विवरण</h2>
        <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors">
          <XIcon size={20} />
        </button>
      </div>

      <div className="space-y-6">
        {/* Status Header */}
        <div className="flex items-center gap-4 p-4 rounded-xl bg-white/5 border border-white/10">
          <StatusBadge status={event.parsing_status} />
          <div className="text-sm text-slate-400 font-mono">ID: {event.tweet_id}</div>
        </div>

        {/* Original Text */}
        <div className="space-y-2">
          <label className="text-xs text-cyan-400 uppercase tracking-wider font-bold">Original Tweet</label>
          <div className="p-4 rounded-xl bg-black/30 border border-white/5 text-slate-200 text-sm leading-relaxed">
            {event.raw_text}
          </div>
        </div>

        {/* Extracted Entities */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-xs text-slate-500 uppercase tracking-wider">Event Type</label>
            <div className="flex flex-wrap gap-2">
              {event.event_type && event.event_type.length > 0 ? event.event_type.map(t => (
                <span key={t} className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded-md text-xs border border-blue-500/30">{t}</span>
              )) : <span className="text-slate-600 text-xs">-</span>}
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-xs text-slate-500 uppercase tracking-wider">Scheme</label>
             <div className="flex flex-wrap gap-2">
              {event.scheme_tags && event.scheme_tags.length > 0 ? event.scheme_tags.map(t => (
                <span key={t} className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded-md text-xs border border-purple-500/30">{t}</span>
              )) : <span className="text-slate-600 text-xs">-</span>}
            </div>
          </div>
        </div>

        {/* Geography */}
        <div className="space-y-2">
          <label className="text-xs text-slate-500 uppercase tracking-wider">Location</label>
          <div className="p-3 rounded-xl bg-emerald-900/20 border border-emerald-500/20">
            <div className="flex items-center gap-2 text-sm text-emerald-300 mb-1">
                <span className="w-2 h-2 bg-emerald-500 rounded-full"></span>
                {event.location_text || "Unknown"}
            </div>
            {event.location_canonical && (
                <div className="ml-4 border-l border-emerald-500/30 pl-3 text-xs text-emerald-400/80">
                Canonical: {event.location_canonical.district}
                </div>
            )}
          </div>
        </div>

        {/* Logs */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
             <Terminal size={14} className="text-slate-400"/>
             <label className="text-xs text-slate-500 uppercase tracking-wider">System Logs</label>
          </div>
          <div className="bg-black/50 rounded-lg p-3 font-mono text-xs text-slate-400 space-y-1 border border-white/5">
            {event.logs && event.logs.map((log, i) => (
              <div key={i}>&gt; {log}</div>
            ))}
            {(!event.logs || event.logs.length === 0) && <div>&gt; No logs available</div>}
          </div>
        </div>

      </div>
    </div>
  );
};

const Ingestion = () => {
  const [selectedEvent, setSelectedEvent] = useState<ParsedEvent | null>(null);
  const [filter, setFilter] = useState('all');
  const [events, setEvents] = useState<ParsedEvent[]>([]);
  const [stats, setStats] = useState<any>({});
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [eventsData, statsData] = await Promise.all([
        fetchEvents(filter),
        fetchStats()
      ]);
      setEvents(eventsData);
      setStats(statsData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filter]);

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex flex-col md:flex-row justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white">डेटा अंतर्ग्रहण और पार्सिंग</h2>
          <p className="text-slate-400 text-sm">रीयल-टाइम पाइपलाइन मॉनिटर</p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={loadData} 
            className="p-2 bg-white/5 rounded-lg hover:bg-white/10 transition-colors text-slate-400"
          >
            <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
          </button>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input 
              type="text" 
              placeholder="Search ID or Text..." 
              className="bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-cyan-500 w-full md:w-64"
            />
          </div>
          <select 
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-4 py-2 bg-white/10 rounded-lg border border-white/10 text-sm text-white focus:outline-none"
          >
            <option value="all">All Tweets</option>
            <option value="failed">Failed Only</option>
          </select>
        </div>
      </div>

      {/* Parsing Funnel Visual */}
      <GlassCard className="p-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-center md:text-left">
           <div className="flex-1 w-full">
             <div className="text-xs text-slate-400 uppercase mb-1">Ingested</div>
             <div className="h-2 bg-blue-900/50 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 w-full"></div>
             </div>
             <div className="text-lg font-bold text-blue-400 mt-1">{stats.total_tweets || 0}</div>
           </div>
           <div className="text-slate-600"><ChevronRight /></div>
           <div className="flex-1 w-full">
             <div className="text-xs text-slate-400 uppercase mb-1">Pending</div>
             <div className="h-2 bg-blue-900/50 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500" style={{width: '50%'}}></div>
             </div>
             <div className="text-lg font-bold text-indigo-400 mt-1">{stats.pending || 0}</div>
           </div>
           <div className="text-slate-600"><ChevronRight /></div>
           <div className="flex-1 w-full">
             <div className="text-xs text-slate-400 uppercase mb-1">Fully Parsed</div>
             <div className="h-2 bg-blue-900/50 rounded-full overflow-hidden">
                <div className="h-full bg-green-500" style={{width: '80%'}}></div>
             </div>
             <div className="text-lg font-bold text-green-400 mt-1">{stats.parsed_success || 0}</div>
           </div>
        </div>
      </GlassCard>

      {/* Table */}
      <GlassCard className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-white/5 text-slate-400 uppercase text-xs">
              <tr>
                <th className="px-6 py-4 font-medium">ID</th>
                <th className="px-6 py-4 font-medium">Timestamp</th>
                <th className="px-6 py-4 font-medium">Tweet Text (Snippet)</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {loading ? (
                <tr><td colSpan={5} className="text-center py-8 text-slate-500">Loading events from database...</td></tr>
              ) : events.length === 0 ? (
                 <tr><td colSpan={5} className="text-center py-8 text-slate-500">No tweets found matching criteria.</td></tr>
              ) : (
                events.map((event) => (
                  <tr 
                    key={event.tweet_id} 
                    onClick={() => setSelectedEvent(event)}
                    className="hover:bg-white/5 cursor-pointer transition-colors group"
                  >
                    <td className="px-6 py-4 font-mono text-slate-300">{event.tweet_id}</td>
                    <td className="px-6 py-4 text-slate-400 whitespace-nowrap">
                      {new Date(event.created_at).toLocaleDateString('hi-IN')} <br/>
                      <span className="text-xs opacity-50">{new Date(event.created_at).toLocaleTimeString()}</span>
                    </td>
                    <td className="px-6 py-4 text-slate-300 max-w-md truncate font-hindi">
                      {event.clean_text}
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={event.parsing_status} />
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="text-cyan-400 hover:text-cyan-300 opacity-0 group-hover:opacity-100 transition-opacity">
                        View
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </GlassCard>

      {/* Side Panel Overlay */}
      {selectedEvent && (
        <>
           <div 
             className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
             onClick={() => setSelectedEvent(null)}
           />
           <DetailPanel event={selectedEvent} onClose={() => setSelectedEvent(null)} />
        </>
      )}
    </div>
  );
};

export default Ingestion;
