# Control Hub Layout Specification

## 1. Grid Structure & Layout
The Control Hub utilizes a responsive grid system built with Tailwind CSS.

*   **Container:** `max-w-7xl mx-auto w-full`
*   **Grid System:**
    *   **Mobile:** Single column (`grid-cols-1`)
    *   **Tablet:** Two columns (`md:grid-cols-2`)
    *   **Desktop:** Three or Four columns (`lg:grid-cols-3` or `lg:grid-cols-4`)
*   **Spacing:**
    *   Page Padding: `p-4` (mobile), `p-8` (desktop)
    *   Gap: `gap-4` (cards), `gap-6` (sections)

## 2. Component Identity System
All sections follow the `page_zone_function` naming convention for `ModuleWrapper` IDs:

*   `controlhub_header_systemhealth`: Top-level system metrics.
*   `controlhub_grid_analytics_sync`: Analytics freshness and sync status.
*   `controlhub_panel_title_editor`: Configuration editor for UI labels.
*   `controlhub_panel_api_health`: Detailed service status matrix.
*   `controlhub_panel_mindmap_mapbox`: Visual layer health (future extension).

## 3. Typography & Colors
*   **Font Family:** Inter (English), Noto Sans Devanagari (Hindi).
*   **Headings:** `text-2xl font-bold text-white` (Page Title), `text-sm text-slate-300` (Section Headers).
*   **Status Colors:**
    *   **Green (Good/Up/Fresh):** `#4ade80` (Text), `bg-green-500/20` (Badge Background).
    *   **Red (Bad/Down/Stale):** `#f87171` (Text), `bg-red-500/20` (Badge Background).
    *   **Blue (Info/Resource):** `#60a5fa`.
    *   **Purple (Memory/AI):** `#a855f7`.
    *   **Primary Accent:** `#8BF5E6` (Cyan/Teal).

## 4. Interaction Patterns
*   **Toggles:** Click to toggle module visibility. Immediate optimistic UI update + API call.
*   **Inputs:** Live editing for titles.
*   **Cards:** Glassmorphic effect (`bg-white/5 backdrop-blur-xl border border-white/10`).

## 5. Mobile Responsiveness
*   **Header:** Admin profile collapses to icon-only on mobile to prevent overlap with title.
*   **Navigation:** Bottom tab bar on mobile, Sidebar on desktop.
*   **Tables:** Horizontal scroll (`overflow-x-auto`) for data tables on small screens.
