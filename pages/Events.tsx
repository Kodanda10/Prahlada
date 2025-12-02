
import React, { useState, useEffect } from 'react';
import { ExternalLink } from 'lucide-react';
import AnimatedGlassCard from '../components/AnimatedGlassCard';
import { LiquidLoader } from '../components/interactions/RiveLikeIcons';
import { fetchEvents } from '../services/api';
import { ParsedEvent } from '../types';

const Events = () => {
  const [events, setEvents] = useState<ParsedEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
          const data = await fetchEvents();
          setEvents(data);
      } catch (e) {
          console.error(e);
      } finally {
          setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="space-y-6 pb-10">
      <div className="flex justify-between items-center">
         <h2 className="text-2xl font-bold text-white font-hindi">इवेंट एक्सप्लोरर (Events)</h2>
         <div className="text-sm text-slate-400 font-hindi">DB से {events.length} हालिया ईवेंट दिखाए जा रहे हैं</div>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
            <LiquidLoader />
        </div>
      ) : (
      <div className="grid gap-4">
        {events.map((event, index) => (
          <AnimatedGlassCard key={event.tweet_id} className="flex flex-col md:flex-row gap-6 group" delay={index * 0.05}>
             <div className="flex-1">
                <div className="flex items-start justify-between mb-2">
                   <div className="flex gap-2 items-center mb-2 md:mb-0">
                      {event.event_type.map(t => (
                        <span key={t} className="px-2 py-1 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs rounded-full font-hindi">
                          {t}
                        </span>
                      ))}
                      <span className="text-slate-500 text-xs">|</span>
                      <span className="text-slate-400 text-xs font-hindi">{new Date(event.created_at).toLocaleDateString('hi-IN', { dateStyle: 'full' })}</span>
                   </div>
                   <a href={`https://twitter.com/user/status/${event.tweet_id}`} target="_blank" rel="noopener noreferrer" className="text-slate-500 hover:text-white transition-colors">
                     <ExternalLink size={16} />
                   </a>
                </div>
                <h3 className="text-lg text-slate-200 font-medium mb-2 font-hindi">{event.clean_text}</h3>
                <div className="flex flex-wrap gap-4 text-sm text-slate-500">
                   <div className="flex items-center gap-1 font-hindi">
                    <span className="w-1.5 h-1.5 bg-red-400 rounded-full"></span>
                    {event.location_text}
                   </div>
                   {event.scheme_tags.length > 0 && (
                      <div className="flex items-center gap-1 font-hindi">
                        <span className="w-1.5 h-1.5 bg-purple-400 rounded-full"></span>
                        {event.scheme_tags.join(', ')}
                      </div>
                   )}
                </div>
             </div>
          </AnimatedGlassCard>
        ))}
      </div>
      )}
    </div>
  );
};

export default Events;
