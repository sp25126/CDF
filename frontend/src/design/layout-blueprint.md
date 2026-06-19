# Layout Blueprint: Shiksha Sahayak

## The 3-Zone Architecture
Optimized for classroom smartboards and teacher co-piloting.

### 1. Top Context Bar (Student-Facing)
- **Role**: Persistent context and state anchor.
- **Content**: Topic title, current mode indicator, language badge, and JULI-E state text.
- **Aesthetic**: Minimal, high contrast, non-interactive.

### 2. Main Teaching Canvas (Student-Facing)
- **Role**: The primary learning area.
- **Content**: JULI-E Avatar (left/center), Learning Cards (center/right), Transcript (optional overlay/sidebar), Media Rail (right/bottom).
- **Aesthetic**: Light-themed, calm, maximized for content visibility.

### 3. Bottom Teacher Console (Teacher-Facing)
- **Role**: Control center for the teacher.
- **Content**: Voice trigger, mode switchers, hands-free toggle, session management, and next-action suggestions.
- **Aesthetic**: Dark-themed, distinct from the student area, high-density touch controls.

## Responsive Strategy
- **Smartboard (Large)**: 3-zone stack is fully expanded. Teacher console is fixed at the bottom.
- **Tablet (Medium)**: Teacher console becomes a collapsible bottom-drawer or side-panel to maximize teaching space.
- **Mobile (Small)**: Not a primary target, but layout collapses to a vertical stack with the console as a bottom sheet.

## Component Hierarchy
```
AppShell
├── TopContextBar
├── TeachingCanvas
│   ├── AvatarZone (JULI-E)
│   ├── ContentZone (Response Cards / Quiz)
│   └── MediaRail (Visuals / Videos)
└── TeacherConsole
    ├── ControlsZone (Voice / Modes)
    └── SuggestionZone (Next Actions)
```
