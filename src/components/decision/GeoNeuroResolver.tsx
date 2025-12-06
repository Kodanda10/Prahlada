import React, { useEffect, useMemo, useState, useCallback, useRef } from 'react';
import { AnimatePresence, motion, useSpring, useTransform } from 'framer-motion';
import { MapPin, Search, CheckCircle2, Sparkles, X, Building2, Trees, ChevronRight } from 'lucide-react';
import { BoundaryService } from '../../../services/BoundaryService';

// ============================================================================
// TYPES
// ============================================================================

interface GeoNeuroResolverProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (locationData: LocationState) => void;
  initialLocation?: Partial<LocationState>;
  suggestedLocation?: Partial<LocationState>; // AI-suggested location
}

type AreaType = 'URBAN' | 'RURAL';

// Dynamic step types based on area
type UrbanStep = 'DISTRICT' | 'VIDHANSABHA' | 'BLOCK' | 'ULB' | 'WARD';
type RuralStep = 'DISTRICT' | 'VIDHANSABHA' | 'BLOCK' | 'GP' | 'VILLAGE' | 'WARD';
type Step = UrbanStep | RuralStep;

interface LocationState {
  areaType: AreaType;
  district: string | null;
  vidhansabha: string | null;
  block: string | null;
  ulb: string | null;      // Urban only
  gp: string | null;       // Rural only - Gram Panchayat
  village: string | null;  // Rural only
  ward: string | null;
}

type VillageEntry = { code: string; name: string; name_hi?: string; lat?: number; lng?: number; gp_name?: string };

// New Hindi hierarchy structure
interface HindiHierarchyData {
  [districtEn: string]: {
    name_hi: string;
    acs: {
      [acEn: string]: {
        name_hi: string;
        blocks: {
          [blockEn: string]: {
            name_hi: string;
            villages: VillageEntry[];
          };
        };
      };
    };
  };
}

// Legacy type for compatibility
type HierarchyData = Record<string, Record<string, Record<string, VillageEntry[]>>>;

// ============================================================================
// CONSTANTS - All Hindi Labels
// ============================================================================

const URBAN_STEPS: UrbanStep[] = ['DISTRICT', 'VIDHANSABHA', 'BLOCK', 'ULB', 'WARD'];
const RURAL_STEPS: RuralStep[] = ['DISTRICT', 'VIDHANSABHA', 'BLOCK', 'GP', 'VILLAGE', 'WARD'];

const STEP_LABELS: Record<Step, string> = {
  DISTRICT: 'जिला',
  VIDHANSABHA: 'विधानसभा',
  BLOCK: 'ब्लॉक',
  ULB: 'यूएलबी',
  GP: 'ग्राम पंचायत',
  VILLAGE: 'गाँव',
  WARD: 'वार्ड',
};

const STEP_THEME: Record<Step, { chip: string; glow: string; accent: string; ring: string }> = {
  DISTRICT: { chip: 'bg-blue-500/20 border-blue-400/30', glow: 'shadow-[0_0_30px_rgba(59,130,246,0.35)]', accent: 'text-blue-200', ring: 'ring-blue-400/50' },
  VIDHANSABHA: { chip: 'bg-purple-500/20 border-purple-400/30', glow: 'shadow-[0_0_30px_rgba(168,85,247,0.35)]', accent: 'text-purple-200', ring: 'ring-purple-400/50' },
  BLOCK: { chip: 'bg-pink-500/20 border-pink-400/30', glow: 'shadow-[0_0_30px_rgba(236,72,153,0.35)]', accent: 'text-pink-200', ring: 'ring-pink-400/50' },
  ULB: { chip: 'bg-amber-500/20 border-amber-400/30', glow: 'shadow-[0_0_30px_rgba(245,158,11,0.35)]', accent: 'text-amber-200', ring: 'ring-amber-400/50' },
  GP: { chip: 'bg-teal-500/20 border-teal-400/30', glow: 'shadow-[0_0_30px_rgba(20,184,166,0.35)]', accent: 'text-teal-200', ring: 'ring-teal-400/50' },
  VILLAGE: { chip: 'bg-emerald-500/20 border-emerald-400/30', glow: 'shadow-[0_0_30px_rgba(16,185,129,0.35)]', accent: 'text-emerald-200', ring: 'ring-emerald-400/50' },
  WARD: { chip: 'bg-cyan-500/20 border-cyan-400/30', glow: 'shadow-[0_0_30px_rgba(6,182,212,0.35)]', accent: 'text-cyan-200', ring: 'ring-cyan-400/50' },
};

// Area type themes - colors change based on ग्रामीण/शहरी selection
const AREA_THEMES = {
  RURAL: {
    gradient: 'from-emerald-950/95 via-green-900/90 to-teal-950/85',
    header: 'from-emerald-950/60 via-green-900/60 to-teal-950/60',
    accent: 'rgba(16,185,129,0.4)',
    secondary: 'rgba(20,184,166,0.3)',
    chipActive: 'bg-emerald-500/30 border-emerald-400/50 text-emerald-200 shadow-[0_0_20px_rgba(16,185,129,0.4)]',
    chipInactive: 'bg-white/5 border-white/10 text-slate-400 hover:bg-emerald-500/10 hover:border-emerald-400/30',
  },
  URBAN: {
    gradient: 'from-slate-950/95 via-blue-900/90 to-indigo-950/85',
    header: 'from-slate-950/60 via-blue-900/60 to-indigo-950/60',
    accent: 'rgba(59,130,246,0.4)',
    secondary: 'rgba(99,102,241,0.3)',
    chipActive: 'bg-blue-500/30 border-blue-400/50 text-blue-200 shadow-[0_0_20px_rgba(59,130,246,0.4)]',
    chipInactive: 'bg-white/5 border-white/10 text-slate-400 hover:bg-blue-500/10 hover:border-blue-400/30',
  },
};

// ============================================================================
// HINDI-FIRST: Complete District Mapping (SSOT for Hindi names)
// ============================================================================
const DISTRICT_HINDI_MAP: Record<string, string> = {
  'Balod': 'बलोद',
  'Baloda Bazar': 'बलौदा बाज़ार',
  'Balodabazar-Bhatapara': 'बालोदाबाज़ार-भाटापारा',
  'Balrampur': 'बलरामपुर',
  'Balrampur-Ramanujganj': 'बलरामपुर-रामानुजगंज',
  'Bastar': 'बस्तर',
  'Bemetara': 'बेमेतरा',
  'Bijapur': 'बीजापुर',
  'Bilaspur': 'बिलासपुर',
  'Dakshin Bastar Dantewada': 'दक्षिण बस्तर दंतेवाड़ा',
  'Dantewada': 'दंतेवाड़ा',
  'Dhamtari': 'धमतरी',
  'Durg': 'दुर्ग',
  'Gariaband': 'गरियाबंद',
  'Gariyaband': 'गरियाबंद',
  'Gaurela-Pendra-Marwahi': 'गौरेला-पेंड्रा-मरवाही',
  'Janjgir-Champa': 'जांजगीर-चांपा',
  'Jashpur': 'जशपुर',
  'Kabeerdham': 'कबीरधाम',
  'Kabirdham': 'कबीरधाम',
  'Kanker': 'कांकेर',
  'Kondagaon': 'कोंडागांव',
  'Korba': 'कोरबा',
  'Korea': 'कोरिया',
  'Koriya': 'कोरिया',
  'Khairagarh-Chhuikhadan-Gandai': 'खैरागढ़-छुईखदान-गंडई',
  'Mahasamund': 'महासमुंद',
  'Manendragarh-Chirmiri-Bharatpur(M C B)': 'मनेन्द्रगढ़-चिरमिरी-भरतपुर',
  'Manendragarh-Chirmiri-Bharatpur': 'मनेन्द्रगढ़-चिरमिरी-भरतपुर',
  'Mohla-Manpur-Ambagarh Chouki': 'मोहला-मानपुर-अंबागढ़ चौकी',
  'Mungeli': 'मुंगेली',
  'Narayanpur': 'नारायणपुर',
  'Raigarh': 'रायगढ़',
  'Raipur': 'रायपुर',
  'Rajnandgaon': 'राजनंदगांव',
  'Sakti': 'सक्ती',
  'Sarangarh-Bilaigarh': 'सारंगढ़-बिलाईगढ़',
  'Sukma': 'सुकमा',
  'Surajpur': 'सूरजपुर',
  'Surguja': 'सरगुजा',
  'Uttar Bastar Kanker': 'उत्तर बस्तर कांकेर',
};

// Helper to get Hindi name (ALWAYS returns Hindi)
const getHindiDistrictName = (englishName: string): string => {
  return DISTRICT_HINDI_MAP[englishName] || englishName;
};

// ============================================================================
// ANIMATION VARIANTS
// ============================================================================

const backdropVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.3 } },
  exit: { opacity: 0, transition: { duration: 0.2 } },
};

const modalVariants = {
  hidden: { scale: 0.92, opacity: 0, y: 20 },
  visible: { scale: 1, opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 25 } },
  exit: { scale: 0.95, opacity: 0, y: 10, transition: { duration: 0.2 } },
};

const gridVariants = {
  initial: { opacity: 0, x: 60, filter: 'blur(8px)' },
  animate: { opacity: 1, x: 0, filter: 'blur(0px)', transition: { duration: 0.35, ease: [0.25, 0.1, 0.25, 1] } },
  exit: { opacity: 0, x: -60, filter: 'blur(8px)', transition: { duration: 0.25, ease: 'easeIn' } },
};

const chipVariants = {
  initial: { opacity: 0, scale: 0.8, filter: 'blur(10px)' },
  animate: (i: number) => ({
    opacity: 1,
    scale: 1,
    filter: 'blur(0px)',
    transition: { delay: i * 0.04, type: 'spring', stiffness: 400, damping: 20 },
  }),
  exit: { opacity: 0, scale: 0, transition: { duration: 0.15 } },
  hover: { scale: 1.06, y: -3, transition: { type: 'spring', stiffness: 400, damping: 15 } },
  tap: { scale: 0.95 },
};

// ============================================================================
// SUBCOMPONENTS
// ============================================================================

// Neural Path Node
const PathNode: React.FC<{ label: string; isActive: boolean; isCompleted: boolean; onClick?: () => void }> = ({
  label,
  isActive,
  isCompleted,
  onClick,
}) => (
  <motion.button
    onClick={onClick}
    whileHover={{ scale: 1.05 }}
    whileTap={{ scale: 0.95 }}
    className={`
      flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all
      ${isActive
        ? 'bg-gradient-to-r from-indigo-500/30 to-purple-500/30 border border-indigo-400/50 text-white shadow-[0_0_20px_rgba(99,102,241,0.4)] ring-2 ring-indigo-400/30'
        : isCompleted
          ? 'bg-emerald-500/20 border border-emerald-400/40 text-emerald-200'
          : 'bg-white/5 border border-white/10 text-slate-400'
      }
    `}
  >
    {isCompleted && <CheckCircle2 size={12} className="text-emerald-400" />}
    {isActive && (
      <motion.div
        layoutId="active-pulse"
        className="w-2 h-2 rounded-full bg-indigo-400"
        animate={{ scale: [1, 1.3, 1], opacity: [1, 0.7, 1] }}
        transition={{ repeat: Infinity, duration: 1.5 }}
      />
    )}
    <span className="font-hindi">{label}</span>
  </motion.button>
);

// Neural Path SVG Line
const NeuralPathLine: React.FC<{ progress: number }> = ({ progress }) => (
  <svg className="w-6 h-0.5 overflow-visible" viewBox="0 0 24 2">
    <defs>
      <linearGradient id="path-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stopColor="rgba(99,102,241,0.6)" />
        <stop offset="50%" stopColor="rgba(168,85,247,0.6)" />
        <stop offset="100%" stopColor="rgba(16,185,129,0.6)" />
      </linearGradient>
    </defs>
    <motion.line
      x1="0"
      y1="1"
      x2="24"
      y2="1"
      stroke="url(#path-gradient)"
      strokeWidth="2"
      strokeLinecap="round"
      initial={{ pathLength: 0, opacity: 0 }}
      animate={{ pathLength: progress, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
    />
  </svg>
);

// Magnetic Chip (attracts toward cursor) - Now with Hindi display
const MagneticChip: React.FC<{
  item: string;
  itemHindi?: string;
  index: number;
  theme: typeof STEP_THEME.DISTRICT;
  isSuggested: boolean;
  isVisible: boolean;
  onClick: () => void;
}> = ({ item, itemHindi, index, theme, isSuggested, isVisible, onClick }) => {
  const ref = useRef<HTMLButtonElement>(null);
  const [magnetOffset, setMagnetOffset] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const deltaX = (e.clientX - centerX) * 0.15;
    const deltaY = (e.clientY - centerY) * 0.15;
    setMagnetOffset({ x: deltaX, y: deltaY });
  }, []);

  const handleMouseLeave = useCallback(() => {
    setMagnetOffset({ x: 0, y: 0 });
    setIsHovered(false);
  }, []);

  const handleMouseEnter = useCallback(() => {
    setIsHovered(true);
  }, []);

  // Display Hindi name if available, otherwise English
  const displayName = itemHindi && itemHindi !== item ? itemHindi : item;

  return (
    <motion.button
      ref={ref}
      custom={index}
      variants={chipVariants}
      initial="initial"
      animate={isVisible ? "animate" : { opacity: 0.15, scale: 0.85, filter: 'blur(4px)' }}
      whileHover="hover"
      whileTap="tap"
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onMouseEnter={handleMouseEnter}
      onClick={onClick}
      style={{
        x: magnetOffset.x,
        y: magnetOffset.y,
        zIndex: isHovered ? 50 : 1, // Fix 3D tilt overlapping
        isolation: 'isolate',
      }}
      className={`
        group relative px-4 py-3 rounded-2xl text-left border backdrop-blur-sm overflow-hidden
        ${theme.chip} hover:${theme.glow}
        transition-shadow duration-300
      `}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm text-white font-semibold font-hindi leading-tight">{displayName}</span>
        <ChevronRight className="w-4 h-4 text-white/20 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
      </div>

      {isSuggested && (
        <motion.span
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="absolute top-1 right-1 flex items-center gap-1 text-[10px] text-amber-200 bg-amber-500/20 px-2 py-0.5 rounded-full border border-amber-400/40"
        >
          <Sparkles size={10} /> एआई
        </motion.span>
      )}

      {/* Glow effect */}
      <div className="absolute inset-0 -z-10 bg-gradient-to-br from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
    </motion.button>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function GeoNeuroResolver({
  isOpen,
  onClose,
  onSelect,
  initialLocation,
  suggestedLocation,
}: GeoNeuroResolverProps) {
  // State
  const [areaType, setAreaType] = useState<AreaType>('RURAL');
  const [step, setStep] = useState<Step>('DISTRICT');
  const [selections, setSelections] = useState<LocationState>({
    areaType: 'RURAL',
    district: null,
    vidhansabha: null,
    block: null,
    ulb: null,
    gp: null,
    village: null,
    ward: null,
  });
  const [hierarchy, setHierarchy] = useState<HierarchyData | null>(null);
  const [hindiHierarchy, setHindiHierarchy] = useState<HindiHierarchyData | null>(null);
  const [items, setItems] = useState<string[]>([]);
  const [displayItems, setDisplayItems] = useState<{ en: string; hi: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [tilt, setTilt] = useState({ x: 0, y: 0 });

  // Current area theme
  const areaTheme = AREA_THEMES[areaType];

  // Get current steps based on area type
  const currentSteps = areaType === 'URBAN' ? URBAN_STEPS : RURAL_STEPS;
  const currentStepIndex = currentSteps.indexOf(step as any);

  // Load hierarchy on mount
  useEffect(() => {
    if (!isOpen) return;
    loadHierarchy();
  }, [isOpen]);

  // Body scroll lock when modal is open
  useEffect(() => {
    if (isOpen) {
      // Lock body scroll
      const originalOverflow = document.body.style.overflow;
      const originalPaddingRight = document.body.style.paddingRight;

      // Get scrollbar width to prevent layout shift
      const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;

      document.body.style.overflow = 'hidden';
      document.body.style.paddingRight = `${scrollbarWidth}px`;

      return () => {
        // Restore on unmount/close
        document.body.style.overflow = originalOverflow;
        document.body.style.paddingRight = originalPaddingRight;
      };
    }
  }, [isOpen]);

  // Esc key to close modal
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const loadHierarchy = async () => {
    setLoading(true);
    try {
      // Load both legacy and Hindi hierarchy
      const [legacyData, hindiData] = await Promise.all([
        BoundaryService.loadHierarchyData(),
        fetch('/chhattisgarh_hierarchy_hindi.json').then(r => r.ok ? r.json() : null).catch(() => null)
      ]);

      // Prefer Hindi hierarchy as the primary source to ensure Hindi labels render.
      const chosenHierarchy = (hindiData as any) || legacyData;
      if (chosenHierarchy) {
        setHierarchy(chosenHierarchy);
        setItems(Object.keys(chosenHierarchy).sort());
      }

      if (hindiData) {
        setHindiHierarchy(hindiData);
        // Build display items with Hindi names - ALWAYS use DISTRICT_HINDI_MAP first
        const districtItems = Object.entries(hindiData).map(([en, data]) => ({
          en,
          hi: DISTRICT_HINDI_MAP[en] || (data as any).name_hi || en
        })).sort((a, b) => a.hi.localeCompare(b.hi, 'hi'));
        setDisplayItems(districtItems);
      } else {
        console.warn('Hindi hierarchy not loaded; falling back to English-only hierarchy');
      }
    } catch (err) {
      console.error('पदानुक्रम लोड करने में विफल', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle area type selection (now with separate chips)
  const handleAreaSelect = useCallback((type: AreaType) => {
    if (type === areaType) return;
    setAreaType(type);
    setSelections(prev => ({ ...prev, areaType: type }));
    // Reset to district if beyond common steps
    if (currentStepIndex > 2) {
      setStep('DISTRICT');
      if (hierarchy) setItems(Object.keys(hierarchy).sort());
    }
  }, [areaType, currentStepIndex, hierarchy]);

  // Get items for current step
  const getItemsForStep = useCallback((targetStep: Step, loc: LocationState) => {
    if (!hierarchy) return [];

    switch (targetStep) {
      case 'DISTRICT':
        return Object.keys(hierarchy).sort();
      case 'VIDHANSABHA':
        return loc.district ? Object.keys(hierarchy[loc.district] || {}).sort() : [];
      case 'BLOCK':
        return loc.district && loc.vidhansabha
          ? Object.keys(hierarchy[loc.district]?.[loc.vidhansabha] || {}).sort()
          : [];
      case 'ULB':
      case 'GP':
      case 'VILLAGE':
      case 'WARD':
        // For now, use villages from hierarchy
        if (loc.district && loc.vidhansabha && loc.block) {
          const entries = hierarchy[loc.district]?.[loc.vidhansabha]?.[loc.block] || [];
          return entries.map(v => v.name).filter(Boolean).sort();
        }
        return [];
      default:
        return [];
    }
  }, [hierarchy]);

  // Handle selection
  const handleSelection = useCallback((item: string) => {
    if (!hierarchy) return;

    const newSelections = { ...selections };
    const steps = areaType === 'URBAN' ? URBAN_STEPS : RURAL_STEPS;
    const stepIndex = steps.indexOf(step as any);

    // Update selection for current step
    switch (step) {
      case 'DISTRICT':
        newSelections.district = item;
        newSelections.vidhansabha = null;
        newSelections.block = null;
        newSelections.ulb = null;
        newSelections.gp = null;
        newSelections.village = null;
        newSelections.ward = null;
        break;
      case 'VIDHANSABHA':
        newSelections.vidhansabha = item;
        newSelections.block = null;
        newSelections.ulb = null;
        newSelections.gp = null;
        newSelections.village = null;
        newSelections.ward = null;
        break;
      case 'BLOCK':
        newSelections.block = item;
        newSelections.ulb = null;
        newSelections.gp = null;
        newSelections.village = null;
        newSelections.ward = null;
        break;
      case 'ULB':
        newSelections.ulb = item;
        newSelections.ward = null;
        break;
      case 'GP':
        newSelections.gp = item;
        newSelections.village = null;
        newSelections.ward = null;
        break;
      case 'VILLAGE':
        newSelections.village = item;
        newSelections.ward = null;
        break;
      case 'WARD':
        newSelections.ward = item;
        break;
    }

    setSelections(newSelections);

    // Move to next step or complete
    if (stepIndex < steps.length - 1) {
      const nextStep = steps[stepIndex + 1];
      setStep(nextStep);
      setItems(getItemsForStep(nextStep, newSelections));
      setSearchQuery('');
    } else {
      // Final selection
      onSelect(newSelections);
      onClose();
    }
  }, [hierarchy, selections, step, areaType, getItemsForStep, onSelect, onClose]);

  // Go back to previous step
  const goBack = useCallback(() => {
    const steps = areaType === 'URBAN' ? URBAN_STEPS : RURAL_STEPS;
    const stepIndex = steps.indexOf(step as any);
    if (stepIndex > 0) {
      const prevStep = steps[stepIndex - 1];
      setStep(prevStep);
      setItems(getItemsForStep(prevStep, selections));
      setSearchQuery('');
    }
  }, [step, areaType, getItemsForStep, selections]);

  // Go to specific step
  const goToStep = useCallback((targetStep: Step) => {
    const steps = areaType === 'URBAN' ? URBAN_STEPS : RURAL_STEPS;
    const currentIdx = steps.indexOf(step as any);
    const targetIdx = steps.indexOf(targetStep as any);

    if (targetIdx < currentIdx) {
      setStep(targetStep);
      setItems(getItemsForStep(targetStep, selections));
      setSearchQuery('');
    }
  }, [step, areaType, getItemsForStep, selections]);

  // Flatten hierarchy for Global Search
  const flattenedItems = useMemo(() => {
    if (!hindiHierarchy && !hierarchy) return [];

    const results: { name: string; nameHi: string; type: Step; path: LocationState }[] = [];

    // Helper to walk the tree
    // We prioritize Hindi hierarchy if available as it contains the structure
    const sourceData = hindiHierarchy || hierarchy;
    if (!sourceData) return [];

    Object.entries(sourceData).forEach(([distName, distData]: [string, any]) => {
      const distHi = (distData as any).name_hi || DISTRICT_HINDI_MAP[distName] || distName;

      // Add District
      results.push({
        name: distName,
        nameHi: distHi,
        type: 'DISTRICT',
        path: { areaType: 'RURAL', district: distName, vidhansabha: null, block: null, gp: null, village: null, ulb: null, ward: null }
      });

      // Walk ACs
      const acs = (distData as any).acs || (distData as any).vidhansabhas || {};
      Object.entries(acs).forEach(([acName, acData]: [string, any]) => {
        const acHi = (acData as any).name_hi || acName;

        // Add AC (skip for simplified search if needed, but keeping for completeness)
        // results.push({ ...type: 'VIDHANSABHA'... })

        // Walk Blocks
        const blocks = (acData as any).blocks || {};
        Object.entries(blocks).forEach(([blockName, blockData]: [string, any]) => {
          const blockHi = (blockData as any).name_hi || blockName;

          // Add Block
          results.push({
            name: blockName,
            nameHi: blockHi,
            type: 'BLOCK',
            path: { areaType: 'RURAL', district: distName, vidhansabha: acName, block: blockName, gp: null, village: null, ulb: null, ward: null }
          });

          // Walk Villages/GPs
          const villages = (blockData as any).villages || [];
          villages.forEach((v: any) => {
            const vName = typeof v === 'string' ? v : v.name;
            const vHi = typeof v === 'string' ? v : (v.name_hi || vName);

            // Add Village
            results.push({
              name: vName,
              nameHi: vHi,
              type: 'VILLAGE',
              path: { areaType: 'RURAL', district: distName, vidhansabha: acName, block: blockName, gp: null, village: vName, ulb: null, ward: null }
            });
          });
        });
      });
    });

    return results;
  }, [hindiHierarchy, hierarchy]);

  // Filter items by search (Global vs Local)
  const filteredItems = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) return items;

    // Local filter if query is short
    if (query.length < 2) {
      return items.filter(item => item.toLowerCase().includes(query));
    }

    // Global Search Mode
    // We don't return 'items' here, we need a special display mode.
    // But to keep it simple within existing UI, we might need a separate 'searchResults' state.
    // For now, let's just filter the current level items if we stay in local mode.
    // BUT the user asked for Global Search.
    return items.filter(item => item.toLowerCase().includes(query));
  }, [items, searchQuery]);

  // Global Search Results (separate from current step items)
  const globalSearchResults = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query || query.length < 3) return null; // Only trigger global search on 3+ chars

    return flattenedItems.filter(item =>
      item.name.toLowerCase().includes(query) ||
      item.nameHi.includes(query)
    ).slice(0, 50); // Limit results
  }, [flattenedItems, searchQuery]);

  // Check if item matches suggestion
  const isSuggested = useCallback((item: string) => {
    if (!suggestedLocation) return false;
    const normalize = (s: string) => s?.trim().toLowerCase() || '';

    switch (step) {
      case 'DISTRICT': return normalize(suggestedLocation.district || '') === normalize(item);
      case 'VIDHANSABHA': return normalize(suggestedLocation.vidhansabha || '') === normalize(item);
      case 'BLOCK': return normalize(suggestedLocation.block || '') === normalize(item);
      default: return false;
    }
  }, [suggestedLocation, step]);

  // Get Hindi name for an item based on current step - HINDI-FIRST priority
  const getHindiName = useCallback((item: string): string => {
    try {
      switch (step) {
        case 'DISTRICT':
          // ALWAYS use DISTRICT_HINDI_MAP first (Single Source of Truth)
          return DISTRICT_HINDI_MAP[item] || hindiHierarchy?.[item]?.name_hi || item;
        case 'VIDHANSABHA':
          if (selections.district && hindiHierarchy) {
            return hindiHierarchy[selections.district]?.acs?.[item]?.name_hi || item;
          }
          return item;
        case 'BLOCK':
          if (selections.district && selections.vidhansabha && hindiHierarchy) {
            return hindiHierarchy[selections.district]?.acs?.[selections.vidhansabha]?.blocks?.[item]?.name_hi || item;
          }
          return item;
        case 'VILLAGE':
        case 'GP':
          // Villages have name_hi in the array
          if (selections.district && selections.vidhansabha && selections.block && hindiHierarchy) {
            const villages = hindiHierarchy[selections.district]?.acs?.[selections.vidhansabha]?.blocks?.[selections.block]?.villages || [];
            // Handle both string array and object array
            const village = villages.find((v: any) => (typeof v === 'string' ? v : v.name) === item);
            return typeof village === 'string' ? village : (village?.name_hi || item);
          }
          return item;
        default:
          return item;
      }
    } catch (e) {
      return item;
    }
  }, [hindiHierarchy, step, selections]);

  // 3D Tilt effect
  const handleTilt = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 8;
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * -8;
    setTilt({ x, y });
  }, []);

  const resetTilt = useCallback(() => setTilt({ x: 0, y: 0 }), []);

  // Get value for step in breadcrumb
  const getStepValue = useCallback((s: Step): string | null => {
    switch (s) {
      case 'DISTRICT': return selections.district;
      case 'VIDHANSABHA': return selections.vidhansabha;
      case 'BLOCK': return selections.block;
      case 'ULB': return selections.ulb;
      case 'GP': return selections.gp;
      case 'VILLAGE': return selections.village;
      case 'WARD': return selections.ward;
      default: return null;
    }
  }, [selections]);

  if (!isOpen) return null;

  const theme = STEP_THEME[step] || STEP_THEME.DISTRICT;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[200] flex items-center justify-center p-4">
        {/* Backdrop - Glassmorphic */}
        <motion.div
          variants={backdropVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
          onClick={onClose}
          className="absolute inset-0 bg-slate-950/80 backdrop-blur-2xl"
        />

        {/* Modal - 3D Tilt */}
        <motion.div
          variants={modalVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
          onMouseMove={handleTilt}
          onMouseLeave={resetTilt}
          style={{
            rotateX: tilt.y,
            rotateY: tilt.x,
            perspective: 1200,
            transformStyle: 'preserve-3d',
          }}
          className={`relative w-full max-w-5xl bg-gradient-to-b ${areaTheme.gradient} border border-white/10 rounded-3xl shadow-[0_25px_100px_rgba(0,0,0,0.5)] flex flex-col max-h-[90vh] overflow-hidden transition-all duration-500`}
        >
          {/* Header */}
          <div className={`relative p-6 border-b border-white/10 bg-gradient-to-r ${areaTheme.header} transition-all duration-500 shrink-0`}>
            {/* Background decorations - dynamic based on area type */}
            <div className="absolute inset-0 opacity-30 transition-all duration-500" style={{ background: `radial-gradient(circle at 20% 30%, ${areaTheme.accent}, transparent 50%), radial-gradient(circle at 80% 20%, ${areaTheme.secondary}, transparent 40%)` }} />

            <div className="relative flex items-center justify-between gap-4">
              {/* Title */}
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-2xl bg-gradient-to-br from-indigo-500/30 to-purple-500/30 border border-indigo-400/30">
                  <MapPin size={22} className="text-indigo-300" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white font-hindi">स्थान चयन</h2>
                </div>
              </div>

              {/* Area Type Chips + Back + Close */}
              <div className="flex items-center gap-3">
                {/* Two separate chips for ग्रामीण and शहरी */}
                <div className="flex gap-2">
                  <motion.button
                    onClick={() => handleAreaSelect('RURAL')}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`
                      flex items-center gap-2 px-4 py-2 rounded-full border transition-all duration-300
                      ${areaType === 'RURAL' ? areaTheme.chipActive : AREA_THEMES.RURAL.chipInactive}
                    `}
                  >
                    <Trees size={16} />
                    <span className="text-sm font-hindi font-medium">ग्रामीण</span>
                  </motion.button>

                  <motion.button
                    onClick={() => handleAreaSelect('URBAN')}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`
                      flex items-center gap-2 px-4 py-2 rounded-full border transition-all duration-300
                      ${areaType === 'URBAN' ? areaTheme.chipActive : AREA_THEMES.URBAN.chipInactive}
                    `}
                  >
                    <Building2 size={16} />
                    <span className="text-sm font-hindi font-medium">शहरी</span>
                  </motion.button>
                </div>

                {step !== 'DISTRICT' && (
                  <motion.button
                    onClick={goBack}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-4 py-2 text-sm rounded-full bg-white/10 text-slate-200 border border-white/15 hover:bg-white/15 transition-colors font-hindi"
                  >
                    पिछला चरण
                  </motion.button>
                )}

                <motion.button
                  onClick={onClose}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  className="p-2.5 rounded-full text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                >
                  <X size={20} />
                </motion.button>
              </div>
            </div>

            {/* Neural Path Breadcrumb */}
            <div className="relative mt-6">
              {/* Progress Line */}
              <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${((currentStepIndex + 1) / currentSteps.length) * 100}%` }}
                  transition={{ duration: 0.5, ease: 'easeInOut' }}
                />
              </div>

              {/* Step Nodes */}
              <div className="flex items-center gap-2 mt-4 overflow-x-auto no-scrollbar pb-1">
                {currentSteps.map((s, i) => {
                  const isActive = s === step;
                  const isCompleted = i < currentStepIndex;
                  const value = getStepValue(s);
                  const label = value || STEP_LABELS[s];

                  return (
                    <React.Fragment key={s}>
                      {i > 0 && <NeuralPathLine progress={i <= currentStepIndex ? 1 : 0} />}
                      <PathNode
                        label={label}
                        isActive={isActive}
                        isCompleted={isCompleted}
                        onClick={() => goToStep(s)}
                      />
                    </React.Fragment>
                  );
                })}
                {/* Next step placeholder - removed per user request */}
              </div>
            </div>
          </div>

          {/* Search Bar */}
          <div className="relative p-4 border-b border-white/5 bg-black/20 shrink-0">
            <div className="relative max-w-2xl mx-auto">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="खोजें (गांव, ब्लॉक, जिला)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-2xl py-3.5 pl-12 pr-4 text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-400/60 focus:bg-white/10 focus:ring-2 focus:ring-indigo-500/20 transition-all font-hindi text-base"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-xs text-slate-300 hover:text-white px-2 py-1 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                >
                  साफ़ करें
                </button>
              )}
            </div>
          </div>

          {/* Main Content Area: Grid or Global Search Results */}
          <div className="flex-1 overflow-y-auto custom-scrollbar p-6 pt-4 pb-8">
            {loading ? (
              <div className="flex justify-center items-center h-48">
                <motion.div
                  className="w-12 h-12 border-2 border-indigo-400 border-t-transparent rounded-full"
                  animate={{ rotate: 360 }}
                  transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
                />
              </div>
            ) : globalSearchResults ? (
              // GLOBAL SEARCH RESULTS VIEW
              <div className="space-y-2">
                {globalSearchResults.length === 0 ? (
                  <div className="text-center py-12 text-slate-400 font-hindi">
                    <p>"{searchQuery}" से मेल खाता कोई स्थान नहीं मिला</p>
                  </div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="grid grid-cols-1 md:grid-cols-2 gap-3"
                  >
                    {globalSearchResults.map((res, idx) => (
                      <button
                        key={`${res.type}-${res.name}-${idx}`}
                        onClick={() => {
                          setSelections(res.path);
                          // If leaf node, select. If district/block just navigate?
                          // Requirement: "user can to be sure and selected it"
                          // Let's select it directly.
                          onSelect(res.path);
                          onClose();
                        }}
                        className="flex flex-col items-start p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-indigo-400/30 transition-all text-left group"
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${res.type === 'VILLAGE' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-indigo-500/20 text-indigo-300'}`}>
                            {STEP_LABELS[res.type]}
                          </span>
                          <span className="font-bold text-white font-hindi">{res.nameHi}</span>
                          <span className="text-xs text-slate-500">({res.name})</span>
                        </div>
                        <div className="text-sm text-slate-400 font-hindi pl-1">
                          {res.path.district} {res.path.block ? `> ${res.path.block}` : ''}
                        </div>
                      </button>
                    ))}
                  </motion.div>
                )}
              </div>
            ) : (
              // STEP-BY-STEP GRID VIEW
              <AnimatePresence mode="wait">
                <motion.div
                  key={step}
                  variants={gridVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3"
                >
                  {filteredItems.map((item, idx) => (
                    <MagneticChip
                      key={item}
                      item={item}
                      itemHindi={getHindiName(item)}
                      index={idx}
                      theme={theme}
                      isSuggested={isSuggested(item)}
                      isVisible={!searchQuery || item.toLowerCase().includes(searchQuery.toLowerCase())}
                      onClick={() => handleSelection(item)}
                    />
                  ))}
                </motion.div>
              </AnimatePresence>
            )}

            {!loading && !globalSearchResults && filteredItems.length === 0 && (
              <div className="text-center py-12 text-slate-400 font-hindi">
                <p>"{searchQuery}" से मेल खाता कोई स्थान नहीं मिला</p>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
