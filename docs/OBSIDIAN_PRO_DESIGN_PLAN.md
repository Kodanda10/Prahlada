# 🍎 Obsidian Pro: Design System Plan
> **"The interface is not just a tool. It is a destination."**

This plan outlines the transformation of the Review Dashboard into a state-of-the-art, Apple-inspired "Obsidian Pro" experience. We retain 100% of the functionality while elevating the aesthetics to a global benchmark.

---

## 💎 Core Design Language: "Hyper-Glass & Liquid Light"

We are moving away from "Flat Dark Mode" to "Cinematic Materiality".

### 1. The Material: "Obsidian Glass"
Instead of simple gray backgrounds, every surface is a piece of light-absorbing glass.
- **Backdrop Blur:** `blur-2xl` to `blur-3xl` (24px - 40px).
- **Surface:** `#050505` with 80% opacity.
- **Border:** `1px` gradient border that catches the light (White to Transparent).
- **Texture:** A subtle "Noise" overlay to give it tactile grain (like high-end paper).

### 2. The Lighting: "Liquid Cursor"
- The cursor acts as a **torch**.
- As you move your mouse, a `radial-gradient` glow follows it, revealing the texture of the glass beneath.
- **Active Elements** emit their own neon glow (Cyan/Emerald/Violet).

### 3. The Physics: "Spring & Magnetism"
- **Entrance:** Elements don't just fade in. They **assemble** with spring physics.
- **Hover:** Buttons are "Magnetic". They pull slightly towards your cursor.
- **Click:** Haptic visual feedback (scale down + ripple).

---

## 🏗️ Component Transformation Plan

### 1. The Stage (`Review.tsx`)
**Current:** A grid layout.
**New:** A **"Command Center Cockpit"**.
- **Background:** The `AuroraBackground` is pushed deeper (z-index -10) and given a "Starfield" depth.
- **Layout:**
  - **Left Panel (Nexus):** A tall, thin "Monolith" of glass on the left.
  - **Center Stage:** The `ArbitrationCard` floats in the center, levitating 50px off the "floor" (shadow).
  - **Right Panel (Stats):** A "Heads Up Display" (HUD) floating on the right.

### 2. The Hero (`ArbitrationCard.tsx`)
**Current:** A standard card with borders.
**New:** A **"Levitating Obsidian Slab"**.
- **Container:**
  - `backdrop-filter: blur(40px)`
  - `box-shadow: 0 40px 80px -20px rgba(0,0,0,0.7)` (Deep depth).
  - **Tilt Effect:** The card subtly tilts (3D) as you move your mouse to corners.
- **Header:**
  - Tweet ID becomes a **"Holographic Chip"** (glowing text inside a glass pill).
  - Date is a subtle caption.
- **The Tweet:**
  - **Typography:** "Cinematic Caption". Large (`text-xl`), centered, `font-light`.
  - **Glow:** A soft spotlight behind the text to make it pop.

### 3. The Decision Engine (`DecisionRow.tsx`)
**Current:** A grid of rows.
**New:** **"Floating Islands"**.
- Each row (Event Type, People, etc.) is a separate "Island" floating in the void.
- **The Interaction:**
  - **Parser (Cyan) & AI (Violet):** These are "Energy Orbs" on the left.
  - **Final Decision (Emerald):** A "Dock" on the right.
  - **Action:** When you click a suggestion, it **morphs** (layout animation) and flies into the Dock.
  - **Conflict:** A "Tension Line" connects conflicting values, glowing red until resolved.

### 4. The Controls (Buttons & Inputs)
- **Approve Button:**
  - **State:** "Liquid Fill". On hover, emerald liquid fills the button from the bottom.
  - **Icon:** The checkmark animates (draws itself).
- **Skip Button:**
  - **State:** "Ghost". Barely visible text that lights up white on hover.
- **Inputs:**
  - "Underline" style that expands when focused.

---

## 🎬 Animation Orchestration

We will use `framer-motion` for a choreographed entrance:
1.  **T=0.0s**: Background Nebula ignites.
2.  **T=0.2s**: The Left Nexus Monolith slides in.
3.  **T=0.4s**: The Central Card **unfolds** (height expands).
4.  **T=0.6s**: The Tweet Text types out (fast typewriter).
5.  **T=0.8s**: The Decision Islands float up one by one (staggered).

---

## 🛠️ Implementation Strategy

1.  **Step 1: The Foundation**
    - Create `styles/obsidian-pro.css` with the new utility classes (glass, noise, glow).
    - Update `Review.tsx` layout to the "Cockpit".

2.  **Step 2: The Card**
    - Refactor `ArbitrationCard.tsx` to use the new "Levitating Slab" design.
    - Implement the "Cinematic Tweet" typography.

3.  **Step 3: The Interaction**
    - Refactor `DecisionRow.tsx` to the "Floating Islands" model.
    - Add the "Morph" animations for selection.

4.  **Step 4: The Polish**
    - Add "Magnetic Buttons".
    - Add "Liquid Cursor" effect.

---

**Ready for Approval.**
*Do you authorize the upgrade to Obsidian Pro?*
