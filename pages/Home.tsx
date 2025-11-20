
import React, { useState } from 'react';
import { Filter, CheckSquare, MapPin, Tag, Calendar } from 'lucide-react';
import AnimatedGlassCard from '../components/AnimatedGlassCard';
import { PulseButton } from '../components/interactions/RiveLikeIcons';

const mockTweets = [
  { id: 1, date: '19 Nov', location: 'रायगढ़', event: 'बैठक', tags: ['विकास', 'प्रशासन'], desc: 'लंबित परियोजनाओं के संबंध में जिला प्रशासन की समीक्षा बैठक।', status: 'parsed' },
  { id: 2, date: '19 Nov', location: 'खरसिया', event: 'दौरा', tags: ['जनता', 'निरीक्षण'], desc: 'पेयजल योजनाओं का निरीक्षण करने के लिए स्थानीय गांवों का दौरा किया।', status: 'parsed' },
  { id: 3, date: '18 Nov', location: 'अज्ञात', event: 'ट्वीट', tags: [], desc: 'सभी को दिवाली की हार्दिक शुभकामनाएं! #त्योहार', status: 'unparsed' },
  { id: 4, date: '18 Nov', location: 'घरघोड़ा', event: 'उद्घाटन', tags: ['इंफ्रा', 'सड़क'], desc: 'खनन क्षेत्र को जोड़ने वाली नई बाईपास सड़क का उद्घाटन किया।', status: 'parsed' },
  { id: 5, date: '17 Nov', location: 'रायगढ़', event: 'बैठक', tags: ['युवा', 'खेल'], desc: 'खेल संघ के प्रतिनिधियों के साथ बैठक की।', status: 'parsed' },
];

const Home = () => {
  const [isBulkReview, setIsBulkReview] = useState(false);
  const [tweets] = useState(mockTweets);
  const [isLoading, setIsLoading] = useState(false);

  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 1500);
  };

  return (
    <div className="w-full">
      
      {/* Consolidated Single Card for seamless UI */}
      <AnimatedGlassCard className="p-0 overflow-hidden min-h-[600px]">
        
        {/* Header & Filters Section */}
        <div className="p-5 border-b border-white/10 bg-white/5">
          <div className="flex flex-col xl:flex-row gap-6 justify-between items-center">
            
            {/* Title & Count */}
            <div className="flex items-center gap-4 w-full xl:w-auto">
               <div className="p-3 bg-[#8BF5E6]/10 rounded-xl border border-[#8BF5E6]/20">
                  <Filter size={24} className="text-[#8BF5E6]" />
               </div>
               <div>
                 <h2 className="text-xl font-bold text-white font-hindi">ट्वीट डेटाबेस</h2>
                 <p className="text-sm text-slate-400 font-hindi">कुल {tweets.length} रिकॉर्ड्स</p>
               </div>
            </div>

            {/* Controls */}
            <div className="flex flex-wrap gap-3 w-full xl:w-auto justify-end items-center">
              <div className="relative group flex-1 xl:flex-none">
                <MapPin className="absolute left-3 top-3 text-slate-400 group-hover:text-[#8BF5E6] transition-colors" size={16} />
                <input type="text" placeholder="स्थान फ़िल्टर..." className="pl-10 pr-4 py-2.5 bg-black/20 border border-white/10 rounded-xl text-sm text-white focus:border-[#8BF5E6] outline-none w-full transition-all font-hindi placeholder:text-slate-500" />
              </div>
              <div className="relative group flex-1 xl:flex-none">
                <Tag className="absolute left-3 top-3 text-slate-400 group-hover:text-[#8BF5E6] transition-colors" size={16} />
                <input type="text" placeholder="टैग/मेंशन..." className="pl-10 pr-4 py-2.5 bg-black/20 border border-white/10 rounded-xl text-sm text-white focus:border-[#8BF5E6] outline-none w-full transition-all font-hindi placeholder:text-slate-500" />
              </div>
              <div className="relative group flex-1 xl:flex-none">
                <Calendar className="absolute left-3 top-3 text-slate-400 group-hover:text-[#8BF5E6] transition-colors" size={16} />
                <input type="text" placeholder="तिथि चुनें..." className="pl-10 pr-4 py-2.5 bg-black/20 border border-white/10 rounded-xl text-sm text-slate-300 focus:border-[#8BF5E6] outline-none w-full transition-all font-hindi placeholder:text-slate-500" />
              </div>
              
              <div className="h-10 w-[1px] bg-white/10 hidden xl:block mx-2"></div>

              {/* Bulk Review Toggle */}
              <div className="flex items-center gap-1 bg-black/20 p-1.5 rounded-xl border border-white/10">
                <button 
                  onClick={() => setIsBulkReview(false)}
                  className={`px-4 py-2 rounded-lg text-xs font-medium transition-all font-hindi ${!isBulkReview ? 'bg-white/10 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
                >
                  मानक
                </button>
                <button 
                  onClick={() => setIsBulkReview(true)}
                  className={`px-4 py-2 rounded-lg text-xs font-medium transition-all flex items-center gap-1 font-hindi ${isBulkReview ? 'bg-[#8BF5E6] text-[#0f172a] font-bold shadow-[0_0_10px_rgba(139,245,230,0.3)]' : 'text-slate-400 hover:text-slate-200'}`}
                >
                  <CheckSquare size={14} /> थोक समीक्षा
                </button>
              </div>

              <div className="ml-2">
                <PulseButton onClick={handleRefresh} isLoading={isLoading} label="" className="w-10 h-10 justify-center px-0" />
              </div>
            </div>
          </div>
        </div>

        {/* Table Area */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-white/5 text-slate-400 uppercase text-xs border-b border-white/5">
              <tr>
                <th className="px-6 py-5 font-medium tracking-wider font-hindi">दिन / दिनांक</th>
                <th className="px-6 py-5 font-medium tracking-wider font-hindi">📍 स्थान</th>
                <th className="px-6 py-5 font-medium tracking-wider font-hindi">🎯 दौरा / कार्यक्रम</th>
                <th className="px-6 py-5 font-medium tracking-wider font-hindi">👥 कौन/टैग</th>
                <th className="px-6 py-5 font-medium tracking-wider w-1/3 font-hindi">📝 विवरण</th>
                {isBulkReview && <th className="px-6 py-5 font-medium text-right tracking-wider font-hindi">स्थिति</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-slate-300">
              {tweets.map((tweet) => (
                <tr key={tweet.id} className="hover:bg-white/5 transition-colors group">
                  <td className="px-6 py-4 whitespace-nowrap text-slate-400 font-mono text-xs">{tweet.date}</td>
                  <td className="px-6 py-4 font-medium text-white">
                    <div className="flex items-center gap-2">
                       <div className="p-1.5 bg-white/5 rounded-full"><MapPin size={12} className="text-[#8BF5E6]" /></div>
                       <span className="font-hindi">{tweet.location}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border font-hindi ${
                      tweet.event === 'बैठक' ? 'bg-blue-500/10 border-blue-500/20 text-blue-300' :
                      tweet.event === 'दौरा' ? 'bg-pink-500/10 border-pink-500/20 text-pink-300' :
                      tweet.event === 'जनसम्पर्क' ? 'bg-green-500/10 border-green-500/20 text-green-300' :
                      'bg-slate-500/10 border-slate-500/20 text-slate-300'
                    }`}>
                      {tweet.event}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-1.5 flex-wrap">
                      {tweet.tags.length > 0 ? tweet.tags.map(tag => (
                        <span key={tag} className="text-[10px] px-2 py-1 bg-white/5 rounded-md text-slate-400 border border-white/5 font-hindi">#{tag}</span>
                      )) : <span className="text-slate-600">-</span>}
                    </div>
                  </td>
                  <td className="px-6 py-4 max-w-md truncate text-slate-400 group-hover:text-slate-200 transition-colors font-hindi">
                    {tweet.desc}
                  </td>
                  {isBulkReview && (
                    <td className="px-6 py-4 text-right">
                      {tweet.status === 'parsed' ? (
                         <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-500/10 border border-green-500/20 text-green-400 text-xs font-medium font-hindi">
                           <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                           पूर्ण
                         </span>
                      ) : (
                         <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 text-xs font-medium font-hindi">
                           <span className="w-1.5 h-1.5 rounded-full bg-yellow-500"></span>
                           लंबित
                         </span>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </AnimatedGlassCard>

    </div>
  );
};

export default Home;
