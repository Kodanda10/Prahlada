# Project Dhruv - Visual Polish Checklist

## Status Legend
- ✅ OK - Consistent with GeoNeuro theme
- ⚠️ Needs Fix - Requires updates
- 🔲 Pending - Not yet audited

---

## Core Components

### Buttons
| Component | Theme | Hover | Animation | Test |
|-----------|-------|-------|-----------|------|
| PulseButton | ✅ | ✅ | ✅ | 🔲 |
| Primary buttons | ✅ | ✅ | ✅ | 🔲 |
| Icon buttons | ✅ | ✅ | ⚠️ | 🔲 |

### Cards / Sections
| Component | Theme | Hover | Animation | Test |
|-----------|-------|-------|-----------|------|
| AnimatedGlassCard | ✅ | ✅ | ✅ | 🔲 |
| ReviewCard | ✅ | ⚠️ | ⚠️ | 🔲 |
| DecisionRow | ✅ | ✅ | ✅ | `DecisionRow.test.tsx` |

### Chips / Tags
| Component | Theme | Hover | Animation | Test |
|-----------|-------|-------|-----------|------|
| Chip | ✅ | ✅ | ✅ | 🔲 |
| MagneticChip | ✅ | ✅ | ✅ | 🔲 |

### Tables
| Component | Theme | Hover | Animation | Test |
|-----------|-------|-------|-----------|------|
| TweetTable | ✅ | ✅ | 🔲 | `TweetTable.test.tsx` |

### Modals
| Component | Theme | Hover | Esc Key | Scroll | Test |
|-----------|-------|-------|---------|--------|------|
| GeoNeuroResolver | ✅ | ✅ | ✅ | ✅ | `GeoNeuroResolver.test.tsx` |
| TweetPreviewModal | ✅ | 🔲 | 🔲 | 🔲 | 🔲 |

### Navigation
| Component | Theme | Hover | Animation | Test |
|-----------|-------|-------|-----------|------|
| Navbar | ✅ | ✅ | ✅ | 🔲 |
| Tabs | ✅ | ⚠️ | 🔲 | 🔲 |

### Pipeline / Visualization
| Component | Theme | Hover | Animation | Test |
|-----------|-------|-------|-----------|------|
| DhruvVerticalNexus | ✅ | ✅ | ✅ | 🔲 |

### Maps
| Component | Theme | Hover | Animation | Test |
|-----------|-------|-------|-----------|------|
| MapView | ✅ | 🔲 | 🔲 | 🔲 |
| Legend | ✅ | 🔲 | 🔲 | 🔲 |

### Charts
| Component | Theme | Hover | Animation | Test |
|-----------|-------|-------|-----------|------|
| Recharts components | ✅ | 🔲 | 🔲 | 🔲 |

---

## Pages Audited

| Page | Theme Applied | Animations | Responsive | Test |
|------|---------------|------------|------------|------|
| Home | ✅ | ✅ | ✅ | `TweetTable.test.tsx` |
| Review | ✅ | ✅ | ✅ | `GeoNeuroResolver.test.tsx` |
| Analytics | ✅ | ⚠️ | ✅ | 🔲 |

---

## Priority Fixes Completed (This Session)

1. ✅ **Home कौन/टैग** - Uses only `people_canonical`/`people_mentioned`
2. ✅ **Date Typography** - Changed to `text-sm leading-relaxed`
3. ✅ **GeoResolver Esc** - Added keyboard listener
4. ✅ **GeoResolver Scroll** - Added `pb-8` to chip container
5. ✅ **Decision Hover** - Added motion.div with glow effect
