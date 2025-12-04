# ⚡ The Kundalini Reactor (Dhruv Vertical Nexus)

> **"Not a checklist. A Vertical Energy Spine."**

We have replaced the generic vertical list with the **Kundalini Reactor** — a vertical plasma spine that physically "charges up" the pipeline.

---

## 🎨 Design Philosophy

### 1. The "Live" Beam
Instead of static lines, we have a **Laser Beam** (`motion.div`) that shoots down from the top.
- **Physics**: It flows like liquid plasma.
- **Logic**: `height: ${((currentStage - 1) / (totalStages - 1)) * 100}%`

### 2. Node States (The "Ignition")
Nodes don't just change color. They change **physics**:

| State | Visual | Physics | Meaning |
| :--- | :--- | :--- | :--- |
| **Pending** | Dim, Blurred | Asleep | Waiting for energy |
| **Active** | **Spinning Gold Ring** | **High Energy** | Processing now |
| **Done** | Solid Emerald Gem | Locked | Secure & Complete |

### 3. Visual Hierarchy
- **Icons**: Replaced numbers with semantic icons (Database, Brain, Eye).
- **Text**: Added `text-shadow-glow` for that sci-fi terminal feel.
- **Subtitles**: Added Hindi context for every stage.

---

## 🛠️ Implementation Details

### Component: `DhruvVerticalNexus.tsx`
- **Location**: `/components/DhruvVerticalNexus.tsx`
- **Props**: `currentStage` (number 1-9)
- **Tech**: Framer Motion `layoutId` for the spinning ring, `animate` for the beam.

### Integration: `Review.tsx`
- Replaced `QuantumPipeline` with `DhruvVerticalNexus`.
- **Logic**:
  - **Stage 6 (Human Review)**: Default state when reviewing tweets.
  - **Stage 7 (Final Approval)**: Triggers momentarily when you click "Approve".
  - **Stage 9 (Analytics)**: Reached when pipeline is fully drained.

---

## 🚀 How to See It

1.  Go to the **Review Tab**.
2.  Look at the left sidebar.
3.  You will see the **Vertical Plasma Spine**.
4.  **Approve a tweet** → Watch the beam shoot down to "Final Approval" (Stage 7) and the ring spin!

---

**Status: ✅ DEPLOYED**
**Vibe: 🔥 KUNDALINI ACTIVATED**
