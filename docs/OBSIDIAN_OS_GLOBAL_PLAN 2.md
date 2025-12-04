# 🌌 Obsidian OS: Global Design System Plan
> **"Same Soul. New Body."**

This plan outlines the global upgrade of the entire application's UI to a state-of-the-art (SOTA) "Obsidian OS" design language.
**CRITICAL:** The core theme (Deep Purple, Cyan, Emerald) remains **unchanged**. We are upgrading the *physics* and *materiality*, not the *brand*.

---

## 💎 The "Hyper-Glass" Philosophy

We are moving from "2D Layers" to "3D Intelligent Glass".

### 1. The Global Shell (App.tsx)
**Current:** Static gradient background.
**Upgrade:** **"Deep Space Parallax"**
- **Background:** The deep purple/black void remains, but we add a **Starfield** layer that moves slowly.
- **Header:** Becomes a **"Frosted Bar"**.
  - `backdrop-filter: blur(20px)`
  - `border-bottom: 1px solid rgba(255,255,255,0.05)`
  - Shrinks slightly on scroll (Apple style).

### 2. The Core Primitive: `AnimatedGlassCard`
This component is used everywhere. Upgrading it upgrades the whole app.
**Upgrade:** **"Prismatic Glass"**
- **Material:**
  - **Blur:** Increased to `40px` (from 12px) for a premium, creamy depth.
  - **Texture:** A subtle **Noise Overlay** is added to simulate high-end matte glass.
  - **Border:** A **Gradient Border** (White → Transparent) that catches light at the top.
- **Interaction (3D):**
  - **Tilt:** Cards subtly tilt (2-3 degrees) towards the mouse cursor.
  - **Spotlight:** A radial gradient glow follows the mouse *inside* the card.

### 3. The Navigation: `AnimatedNavTabs`
**Current:** Standard tabs.
**Upgrade:** **"Floating Dock"**
- **Design:** Resembles the macOS Dock.
- **Physics:** Icons scale up (1.2x) and glow when hovered.
- **Active State:** A "Lamp" effect (glow from the bottom) instead of a simple underline.

### 4. Global Micro-interactions
- **Cursor:** A global **"Liquid Light"** spotlight follows your mouse across the entire screen, revealing textures in the dark background.
- **Scrollbar:** A thin, translucent "Liquid" scrollbar that expands on hover.
- **Typography:**
  - Headers: `tracking-tight` (tighter spacing) for a modern, editorial look.
  - Numbers: `font-variant-numeric: tabular-nums` for stable data display.

---

## 🛠️ Implementation Strategy

### Phase 1: The Foundation (CSS)
- Create `styles/obsidian-global.css`.
- Define the **Noise Texture** and **Gradient Borders**.
- Update `index.css` to import this new system.

### Phase 2: The Core Upgrade (`AnimatedGlassCard`)
- Refactor `AnimatedGlassCard.tsx` to include:
  - `framer-motion` 3D Tilt.
  - Mouse-following Spotlight.
  - Noise Texture layer.

### Phase 3: The Shell Upgrade (`App.tsx`)
- Implement the **Starfield Background**.
- Upgrade the Header to the **Frosted Bar**.
- Add the global **Liquid Light** cursor.

### Phase 4: The Navigation Upgrade (`AnimatedNavTabs`)
- Refactor to the **Floating Dock** design with magnification physics.

---

## 🔒 Theme Preservation Guarantee
- **Colors:** We stick strictly to the existing Palette (Cyan `#22d3ee`, Emerald `#10b981`, Deep Purple `#2e1065`).
- **Fonts:** We keep `Noto Sans Devanagari`.
- **Layout:** No structural changes to grids or page flows.

**Ready for Approval.**
*Do you authorize the Global Obsidian OS Upgrade?*
