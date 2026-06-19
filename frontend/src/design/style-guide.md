# Style Guide

## Visual Identity
Shiksha Sahayak uses a **Restrained** color strategy to maintain focus on educational content. The interface is split into two distinct zones: the **Teaching Canvas** (Student-facing, light) and the **Teacher Console** (Control-facing, dark).

## Typography
- **Font**: Inter (Sans-serif) for both display and body.
- **Base Size**: 20px (1.25rem). All classroom text must be large enough for smartboard visibility.
- **Scale**:
  - H1: 4.5rem (72px) - Display hero
  - H2: 3.5rem (56px) - Section headers
  - H3: 2.5rem (40px) - Component headers
  - Body: 1.25rem (20px) - Primary reading
  - Small: 1rem (16px) - Metadata / Teacher notes

## Color Strategy
- **Primary Accent**: Indigo (`oklch(0.55 0.18 260)`). Used for focus, primary actions, and JULI-E state indicators.
- **Canvas (Student)**: Near-white tinted neutrals. High contrast for readability.
- **Console (Teacher)**: Dark navy/slate neutrals. Distinct from student-facing content.

## Components & Shapes
- **Radius**: Consistent 12px (`0.75rem`) for cards and buttons.
- **Shadows**: Soft, functional elevation to define hierarchy. No purely decorative shadows.

## Accessibility
- **Contrast**: Minimum 4.5:1 for all text.
- **Touch**: Buttons and interactive targets must be at least 44x44px.
- **Motion**: Reduced-motion media queries are required for all transitions.
