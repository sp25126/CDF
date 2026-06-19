# Design

## Visual Theme

A calm, high-contrast educational interface optimized for classroom smartboards.

## Color Palette

Uses OKLCH for perceptually uniform colors.

- **Primary**: `oklch(0.55 0.18 260)` (Indigo)
- **Canvas BG**: `oklch(0.98 0.005 260)` (Near-white)
- **Console BG**: `oklch(0.25 0.03 260)` (Dark Navy)
- **Ink**: `oklch(0.2 0.02 260)` (Deep Slate)

## Typography

- **Family**: "Inter", system-ui, sans-serif
- **Base**: 20px (1.25rem)
- **Scale**: 1.125 ratio

## Components

- **AppShell**: Root 3-zone container.
- **TopContextBar**: Context anchor.
- **TeachingCanvas**: Learning area.
- **TeacherConsole**: Control center.
- **MediaRail**: Supporting visuals.

## Layout

Fixed 3-zone vertical stack:
1. Header (64px)
2. Content (Flexible)
3. Footer (128px)
