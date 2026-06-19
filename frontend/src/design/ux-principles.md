# UX Principles

## 1. Teacher Clarity
The interface must make the teacher's next action obvious. Controls should be grouped and labeled clearly. The teacher is the conductor; the app is the instrument.

## 2. Student Focus
Student-facing content (Learning Canvas) must be dominant. Distractions like technical logs, complex settings, or avatar internal states should be hidden from this zone.

## 3. Low Cognitive Load
One primary action per area. Use progressive disclosure for complex information. Avoid "wall of text" responses; use bullet points and visual cards.

## 4. Predictable Behavior
Components must behave consistently across all modes. Buttons in the Teacher Console should always follow the same feedback pattern.

## 5. Classroom Friendliness
Large fonts, high contrast, and touch-friendly targets. The app must remain usable when projected on a low-resolution smartboard or viewed from the back of a 40-student classroom.

## Visibility Rules
- **Always Visible**: JULI-E Avatar (state anchor), Top Context Bar (topic/mode indicator), Teacher Console (unless explicitly hidden for full-screen mode).
- **Secondary**: Detailed source logs, transcript history (accessible via scroll/toggle), advanced settings.

## State Feedback
- **JULI-E States**:
  - `idle`: Calm, breathing animation.
  - `listening`: Pulsing glow around avatar, "Listening..." indicator.
  - `thinking`: Soft thinking bubble or ambient glow variation.
  - `speaking`: Lip-sync (if available) or subtle bounce/scale animation.
- **System States**:
  - `loading`: Skeleton screens for cards, not spinners.
  - `empty`: Instructional prompts ("Ask me about...") or next-action suggestions.
  - `success`: Subtle green check or primary accent highlight.
  - `error`: Clear, readable message with a specific "Try Again" or "Switch Mode" action.
