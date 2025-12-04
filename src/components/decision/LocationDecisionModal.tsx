import React, { useEffect, useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { MapPin, Search, CheckCircle2, Sparkles, X } from 'lucide-react';
import { BoundaryService } from '../../../services/BoundaryService';

interface LocationDecisionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (locationData: any) => void;
  initialLocation?: any;
}

type Step = 'DISTRICT' | 'ASSEMBLY' | 'BLOCK' | 'VILLAGE';

interface LocationState {
  district: string | null;
  assembly: string | null;
  block: string | null;
  village: string | null;
}

type VillageEntry = { code: string; name: string; lat?: number; lng?: number; gp_name?: string };
type HierarchyData = Record<string, Record<string, Record<string, VillageEntry[]>>>;

const STEPS: Step[] = ['DISTRICT', 'ASSEMBLY', 'BLOCK', 'VILLAGE'];

const STEP_THEME: Record<Step, { chip: string; glow: string; accent: string }> = {
  DISTRICT: { chip: 'bg-blue-500/20 border-blue-300/20', glow: 'shadow-[0_0_25px_rgba(59,130,246,0.25)]', accent: 'text-blue-200' },
  ASSEMBLY: { chip: 'bg-purple-500/20 border-purple-300/20', glow: 'shadow-[0_0_25px_rgba(168,85,247,0.25)]', accent: 'text-purple-200' },
  BLOCK: { chip: 'bg-pink-500/20 border-pink-300/20', glow: 'shadow-[0_0_25px_rgba(236,72,153,0.25)]', accent: 'text-pink-200' },
  VILLAGE: { chip: 'bg-emerald-500/20 border-emerald-300/20', glow: 'shadow-[0_0_25px_rgba(16,185,129,0.25)]', accent: 'text-emerald-200' },
};

const gridVariants = {
  initial: { opacity: 0, x: 30, filter: 'blur(6px)' },
  animate: { opacity: 1, x: 0, filter: 'blur(0px)', transition: { duration: 0.25, ease: 'easeOut' } },
  exit: { opacity: 0, x: -30, filter: 'blur(6px)', transition: { duration: 0.2, ease: 'easeIn' } },
};

export default function LocationDecisionModal({ isOpen, onClose, onSelect, initialLocation }: LocationDecisionModalProps) {
  const [step, setStep] = useState<Step>('DISTRICT');
  const [selections, setSelections] = useState<LocationState>({
    district: null,
    assembly: null,
    block: null,
    village: null,
  });
  const [hierarchy, setHierarchy] = useState<HierarchyData | null>(null);
  const [items, setItems] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [tilt, setTilt] = useState({ x: 0, y: 0 });

  useEffect(() => {
    if (!isOpen) return;
    preloadHierarchy();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, initialLocation]);

  const normalize = (value?: string | null) => value?.trim().toLowerCase() || '';

  const findMatchingKey = (keys: string[], target?: string | null) => {
    if (!target) return null;
    const normalized = normalize(target);
    return keys.find(k => normalize(k) === normalized) || null;
  };

  const getVillages = (district: string, assembly: string, block: string) => {
    if (!hierarchy) return [];
    const entries = hierarchy[district]?.[assembly]?.[block] || [];
    return entries.map(v => v.name).filter(Boolean).sort();
  };

  const getItemsForStep = (targetStep: Step, loc: LocationState, data: HierarchyData) => {
    if (targetStep === 'DISTRICT') return Object.keys(data).sort();
    if (targetStep === 'ASSEMBLY' && loc.district) return Object.keys(data[loc.district] || {}).sort();
    if (targetStep === 'BLOCK' && loc.district && loc.assembly) return Object.keys(data[loc.district]?.[loc.assembly] || {}).sort();
    if (targetStep === 'VILLAGE' && loc.district && loc.assembly && loc.block) return getVillages(loc.district, loc.assembly, loc.block);
    return [];
  };

  const preloadHierarchy = async () => {
    setLoading(true);
    try {
      const data = await BoundaryService.loadHierarchyData();
      if (!data) return;
      setHierarchy(data);

      const district = findMatchingKey(Object.keys(data), initialLocation?.district);
      const assembly = district ? findMatchingKey(Object.keys(data[district]), initialLocation?.assembly) : null;
      const block = district && assembly ? findMatchingKey(Object.keys(data[district][assembly]), initialLocation?.block) : null;
      const village = district && assembly && block
        ? findMatchingKey(getVillages(district, assembly, block), initialLocation?.village)
        : null;

      const nextSelections: LocationState = { district, assembly, block, village };
      const autoStep: Step =
        district && assembly && block ? 'VILLAGE'
          : district && assembly ? 'BLOCK'
          : district ? 'ASSEMBLY'
          : 'DISTRICT';

      setSelections(nextSelections);
      setStep(autoStep);
      setItems(getItemsForStep(autoStep, nextSelections, data));
      setSearchQuery('');
    } catch (err) {
      console.error('Failed to load hierarchy', err);
    } finally {
      setLoading(false);
    }
  };

  const goToStep = (target: Step) => {
    if (!hierarchy) return;
    const targetIndex = STEPS.indexOf(target);
    const currentIndex = STEPS.indexOf(step);
    if (targetIndex > currentIndex) return;

    const resetSelections: LocationState = {
      district: target === 'DISTRICT' ? null : selections.district,
      assembly: target === 'ASSEMBLY' ? null : selections.assembly,
      block: target === 'BLOCK' ? null : selections.block,
      village: null,
    };

    setSelections(resetSelections);
    setStep(target);
    setItems(getItemsForStep(target, resetSelections, hierarchy));
    setSearchQuery('');
  };

  const handleSelection = (item: string) => {
    if (!hierarchy) return;

    if (step === 'DISTRICT') {
      const nextSelections: LocationState = { district: item, assembly: null, block: null, village: null };
      setSelections(nextSelections);
      setItems(getItemsForStep('ASSEMBLY', nextSelections, hierarchy));
      setStep('ASSEMBLY');
      setSearchQuery('');
      return;
    }

    if (step === 'ASSEMBLY') {
      const nextSelections = { ...selections, assembly: item, block: null, village: null };
      setSelections(nextSelections);
      setItems(getItemsForStep('BLOCK', nextSelections, hierarchy));
      setStep('BLOCK');
      setSearchQuery('');
      return;
    }

    if (step === 'BLOCK') {
      const nextSelections = { ...selections, block: item, village: null };
      setSelections(nextSelections);
      setItems(getItemsForStep('VILLAGE', nextSelections, hierarchy));
      setStep('VILLAGE');
      setSearchQuery('');
      return;
    }

    const finalSelections = { ...selections, village: item };
    setSelections(finalSelections);
    onSelect(finalSelections);
    onClose();
  };

  const suggestedChip = useMemo(() => {
    if (!initialLocation) return null;
    const forStep: Record<Step, string | null> = {
      DISTRICT: initialLocation?.district || null,
      ASSEMBLY: initialLocation?.assembly || null,
      BLOCK: initialLocation?.block || null,
      VILLAGE: initialLocation?.village || null,
    };
    const value = forStep[step];
    if (!value) return null;
    return value.toString().trim();
  }, [initialLocation, step]);

  const filteredItems = useMemo(() => {
    const needle = searchQuery.trim().toLowerCase();
    if (!needle) return items;
    return items.filter(item => item.toLowerCase().includes(needle));
  }, [items, searchQuery]);

  const handleTilt = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 6;
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * -6;
    setTilt({ x, y });
  };

  const resetTilt = () => setTilt({ x: 0, y: 0 });

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[200] flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-black/70 backdrop-blur-xl"
        />

        <motion.div
          initial={{ scale: 0.9, opacity: 0, y: 18 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.92, opacity: 0, y: 18 }}
          onMouseMove={handleTilt}
          onMouseLeave={resetTilt}
          style={{ rotateX: tilt.y, rotateY: tilt.x, perspective: 1200 }}
          className="relative w-full max-w-5xl bg-[#0b1224] border border-white/10 rounded-3xl shadow-[0_20px_80px_rgba(0,0,0,0.45)] overflow-hidden flex flex-col max-h-[86vh]"
        >
          <div className="p-6 border-b border-white/10 bg-gradient-to-r from-indigo-950/80 via-slate-900/80 to-purple-900/60 relative overflow-hidden">
            <div className="absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_20%_20%,rgba(99,102,241,0.3),transparent_40%),radial-gradient(circle_at_80%_0%,rgba(236,72,153,0.25),transparent_35%)]" />
            <div className="relative flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-2xl bg-indigo-500/20 border border-indigo-400/30 text-indigo-200">
                  <MapPin size={20} />
                </div>
                <div>
                  <p className="text-sm text-slate-300 uppercase tracking-[0.2em]">Geo Resolver</p>
                  <h2 className="text-2xl font-bold text-white font-hindi">स्थान चयन</h2>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {step !== 'DISTRICT' && (
                  <button
                    onClick={() => goToStep(STEPS[STEPS.indexOf(step) - 1])}
                    className="px-3 py-1.5 text-xs rounded-full bg-white/10 text-slate-200 border border-white/15 hover:bg-white/15 transition-colors"
                  >
                    पिछला चरण
                  </button>
                )}
                <button
                  onClick={onClose}
                  className="p-2 rounded-full text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            <div className="relative mt-6">
              <div className="h-[4px] w-full bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-indigo-400 via-purple-400 to-emerald-400"
                  initial={{ width: 0 }}
                  animate={{ width: `${((STEPS.indexOf(step) + 1) / STEPS.length) * 100}%` }}
                  transition={{ duration: 0.4, ease: 'easeInOut' }}
                />
              </div>
              <div className="flex items-center justify-between mt-4">
                {STEPS.map((s) => {
                  const isActive = s === step;
                  const isCompleted = STEPS.indexOf(s) < STEPS.indexOf(step);
                  const value = s === 'DISTRICT' ? selections.district : s === 'ASSEMBLY' ? selections.assembly : s === 'BLOCK' ? selections.block : selections.village;
                  const label = s === 'DISTRICT' ? 'जिला' : s === 'ASSEMBLY' ? 'विधानसभा' : s === 'BLOCK' ? 'ब्लॉक/यूएलबी' : 'गाँव/वार्ड';

                  return (
                    <motion.button
                      key={s}
                      onClick={() => goToStep(s)}
                      className={`relative flex items-center gap-2 px-3 py-2 rounded-full border transition-all ${
                        isActive
                          ? 'border-white/40 bg-white/10 text-white'
                          : isCompleted
                            ? 'border-emerald-400/40 bg-emerald-500/10 text-emerald-100'
                            : 'border-white/10 bg-white/5 text-slate-400'
                      }`}
                      whileHover={{ scale: 1.02 }}
                    >
                      {isCompleted ? <CheckCircle2 size={14} /> : <span className="w-3 h-3 rounded-full border border-current opacity-70" />}
                      <span className="text-xs font-hindi">{value || label}</span>
                    </motion.button>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="relative p-4 border-b border-white/10 bg-black/30">
            <div className="relative max-w-xl mx-auto">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="खोजें या टाइप करें... (Cmd/Ctrl + K)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-400/60 focus:bg-white/10 transition-all font-hindi shadow-[0_0_0_1px_rgba(255,255,255,0.05)]"
              />
              {searchQuery && (
                <button
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-300 hover:text-white"
                  onClick={() => setSearchQuery('')}
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto bg-gradient-to-b from-slate-950 via-[#0b1224] to-[#030712] custom-scrollbar p-6">
            {loading ? (
              <div className="flex justify-center items-center h-48">
                <div className="w-10 h-10 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : (
              <AnimatePresence mode="wait">
                <motion.div
                  key={step}
                  variants={gridVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3"
                >
                  {filteredItems.map((item, idx) => {
                    const matchesSearch = item.toLowerCase().includes(searchQuery.toLowerCase());
                    const isSuggested = suggestedChip && normalize(suggestedChip) === normalize(item);
                    const theme = STEP_THEME[step];

                    return (
                      <motion.button
                        key={item}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: matchesSearch ? 1 : 0.25, scale: matchesSearch ? 1 : 0.85 }}
                        transition={{ delay: idx * 0.02 }}
                        onClick={() => handleSelection(item)}
                        className={`relative px-4 py-3 rounded-2xl text-left border overflow-hidden backdrop-blur-sm ${theme.chip} ${theme.glow} hover:scale-105 hover:-translate-y-0.5 transition-all`}
                        whileTap={{ scale: 0.96 }}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <p className="text-sm text-white font-semibold font-hindi leading-tight">{item}</p>
                            <p className={`text-[10px] uppercase tracking-wide mt-1 ${theme.accent}`}>
                              {step === 'DISTRICT' ? 'District' : step === 'ASSEMBLY' ? 'Assembly' : step === 'BLOCK' ? 'Block / ULB' : 'Village / Ward'}
                            </p>
                          </div>
                          {isSuggested && (
                            <span className="flex items-center gap-1 text-[10px] text-amber-200 bg-amber-500/15 px-2 py-1 rounded-full border border-amber-400/30">
                              <Sparkles size={12} /> Suggested
                            </span>
                          )}
                        </div>
                      </motion.button>
                    );
                  })}
                </motion.div>
              </AnimatePresence>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
