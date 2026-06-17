# Frontend Integration Guide

This guide explains how to integrate the `ResponseRenderer` components with the backend API.

## Overview

The frontend provides deterministic rendering of backend responses with these components:

- **ResponseRenderer**: Main orchestrator component
- **AnswerBubble**: Displays explanations with bullets and examples
- **QuizCard**: One-question-at-a-time quiz interface
- **LanguageBadge**: Language mode indicator
- **NextActions**: Suggested next steps
- **ClarificationState**: Unclear command handling

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Backend URL

Create `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Or update your environment based on deployment:

```
NEXT_PUBLIC_API_URL=https://api.example.com
```

### 3. Type Safety

All TypeScript types are in `src/types/api.ts` and mirror the backend schema exactly.

---

## Usage Example

### Basic Response Rendering

```typescript
import { ResponseRenderer } from "@/components";
import { AssistantResponse } from "@/types/api";
import { useState } from "react";

export function ChatScreen() {
  const [response, setResponse] = useState<AssistantResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleCommand = async (text: string) => {
    setLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/command/text`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: "user_session_123",
            text: text,
          }),
        }
      );

      const data = await res.json();
      setResponse(data.data); // Backend wraps response in {status, data}
    } finally {
      setLoading(false);
    }
  };

  const handleNextAction = (action: string) => {
    handleCommand(action);
  };

  return (
    <div className="p-8 bg-white min-h-screen">
      {response && (
        <ResponseRenderer
          response={response}
          onNextAction={handleNextAction}
        />
      )}

      {loading && <div>Loading...</div>}

      {!response && !loading && (
        <div>Send a command to start...</div>
      )}
    </div>
  );
}
```

---

## Component Props

### ResponseRenderer

```typescript
interface ResponseRendererProps {
  response: AssistantResponse;
  onNextAction?: (action: string) => void;
  onQuizNavigate?: (questionIndex: number) => void;
  onQuizAnswerSubmit?: (questionIndex: number, selectedIndex: number) => void;
}
```

- **response**: The backend `AssistantResponse` object
- **onNextAction**: Callback when user clicks a next action button
- **onQuizNavigate**: Callback when quiz question changes
- **onQuizAnswerSubmit**: Callback when quiz answer is submitted

### AnswerBubble

```typescript
interface AnswerBubbleProps {
  answer_text?: string;
  title?: string;
  bullets?: string[];
  example?: string;
  recap?: string;
  avatar_state: AvatarState;
  audio_base64?: string;
}
```

Renders explanations with:
- Main answer text in a highlighted bubble
- Optional title
- Bullet points for smart board display
- Example section
- Recap section
- Avatar state indicator
- Optional audio playback button

### QuizCard

```typescript
interface QuizCardProps {
  quiz: QuizPayload;
  onAnswerSubmit?: (questionIndex: number, selectedIndex: number) => void;
  onNavigate?: (newIndex: number) => void;
}
```

Renders one question at a time with:
- Question text
- Multiple choice options (highlighted for correct/incorrect)
- Explanation after submission
- Previous/Next navigation
- Progress bar

### LanguageBadge

```typescript
interface LanguageBadgeProps {
  language_mode: LanguageMode;
}
```

Small badge showing current language mode:
- हिंग्लिश (hinglish)
- English (english)
- हिंदी (hindi)

### NextActions

```typescript
interface NextActionsProps {
  next_actions: string[];
  onActionClick?: (action: string) => void;
}
```

Displays suggested next commands as clickable buttons.

### ClarificationState

```typescript
interface ClarificationStateProps {
  message?: string;
  suggestions?: string[];
  onSuggestionClick?: (suggestion: string) => void;
}
```

Shown when the assistant doesn't understand the command.

---

## Rendering Modes

### Explain Mode

```json
{
  "mode": "explain",
  "answer_text": "Photosynthesis is...",
  "title": "Photosynthesis",
  "bullets": ["Plants make food...", "Water and CO2..."],
  "example": "Green leaves...",
  "avatar_state": "speaking"
}
```

→ Renders `AnswerBubble` with all fields

### Quiz Mode

```json
{
  "mode": "quiz",
  "quiz": {
    "title": "Quick Check: Fractions",
    "topic": "Fractions",
    "questions": [...],
    "current_index": 0,
    "total_questions": 3
  },
  "answer_text": "Let's start the quiz..."
}
```

→ Renders `QuizCard` with one question at a time

### Clarify Mode

```json
{
  "mode": "unclear",
  "requires_clarification": true,
  "answer_text": "I didn't understand...",
  "next_actions": ["Explain Photosynthesis", "Quiz on Gravity"]
}
```

→ Renders `ClarificationState` with suggestions

### Stop Mode

```json
{
  "mode": "stop",
  "answer_text": "Lesson paused...",
  "avatar_state": "idle"
}
```

→ Renders stop confirmation

### Followup Mode

```json
{
  "mode": "followup",
  "answer_text": "Let me explain that again...",
  "avatar_state": "speaking"
}
```

→ Renders `AnswerBubble` for repeat

---

## API Integration Patterns

### Pattern 1: Simple Text Input

```typescript
const handleSubmit = async (text: string) => {
  const response = await fetch("/api/v1/command/text", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      text: text,
    }),
  });

  const data = await response.json();
  setResponse(data.data);
};
```

### Pattern 2: With Mode Hint

```typescript
const handleExplainClick = async (topic: string) => {
  const response = await fetch("/api/v1/command/text", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      text: topic,
      mode_hint: "explain",
    }),
  });

  const data = await response.json();
  setResponse(data.data);
};
```

### Pattern 3: With Audio Input

```typescript
const handleAudioSubmit = async (audioBlob: Blob) => {
  const formData = new FormData();
  formData.append("session_id", sessionId);
  formData.append("audio", audioBlob, "audio.wav");

  const response = await fetch("/api/v1/command/audio", {
    method: "POST",
    body: formData,
  });

  const data = await response.json();
  setResponse(data.data);
};
```

---

## Styling Customization

All components use TailwindCSS utility classes. To customize:

### 1. Override Colors

Edit component files directly. For example, in `AnswerBubble.tsx`:

```typescript
// Change answer bubble color
<div className="bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200">
```

### 2. Change Layout

Adjust grid/flex properties:

```typescript
{/* Make quiz options display as grid instead of stack */}
<div className="grid grid-cols-2 gap-3">
```

### 3. Responsive Design

Components already include responsive classes:

```typescript
// Already handles mobile/tablet/desktop
<div className="max-w-4xl mx-auto">
```

---

## Error Handling

### Network Errors

```typescript
const handleCommand = async (text: string) => {
  try {
    const response = await fetch("/api/v1/command/text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id, text }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    setResponse(data.data);
  } catch (error) {
    console.error("API error:", error);
    setError(error.message);
  }
};
```

### Validation

```typescript
// Validate response shape
if (!response.session_id || !response.mode) {
  console.error("Invalid response shape");
  return;
}

// Check for required fields based on mode
if (response.mode === "quiz" && !response.quiz) {
  console.error("Quiz mode but no quiz payload");
  return;
}
```

---

## Testing Components

### Unit Test Example (Jest + React Testing Library)

```typescript
import { render, screen } from "@testing-library/react";
import { ResponseRenderer } from "@/components";
import { AssistantResponse } from "@/types/api";

describe("ResponseRenderer", () => {
  it("renders explain mode", () => {
    const response: AssistantResponse = {
      session_id: "test",
      mode: "explain",
      language_mode: "hinglish",
      answer_text: "Photosynthesis is...",
      avatar_state: "speaking",
      next_actions: [],
      confidence: 0.95,
      requires_clarification: false,
      source_refs: [],
      visuals: [],
      videos: [],
      bullets: [],
      questions: [],
    };

    render(<ResponseRenderer response={response} />);
    expect(screen.getByText(/Photosynthesis/)).toBeInTheDocument();
  });

  it("renders quiz mode", () => {
    const response: AssistantResponse = {
      // ... base fields
      mode: "quiz",
      quiz: {
        title: "Test Quiz",
        topic: "Fractions",
        questions: [
          {
            question: "What is 1/2?",
            options: ["Half", "Quarter", "Third"],
            correct_index: 0,
            explanation: "Half means divided into 2 parts",
          },
        ],
        current_index: 0,
        total_questions: 1,
      },
    };

    render(<ResponseRenderer response={response} />);
    expect(screen.getByText(/What is 1\/2\?/)).toBeInTheDocument();
  });
});
```

---

## Performance Notes

- Components are lightweight and pure renderers
- No external API calls within components
- Use `React.memo` for quiz cards if you have many questions:

```typescript
export const QuizCard = React.memo(function QuizCard(props) {
  // component code
});
```

---

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Next.js 14+ with React 18+
- TailwindCSS 3.4+

---

## Troubleshooting

### Components Not Rendering

Check that the response object has all required fields:

```typescript
console.log(JSON.stringify(response, null, 2));
```

### Styling Issues

Clear Next.js cache:

```bash
rm -rf .next
npm run dev
```

### Audio Not Playing

Check browser permissions and ensure audio data is valid base64.

---

## Next Steps

Once Phase 1 is working:

1. **Phase 2**: Add source grounding with `source_refs` rendering
2. **Phase 3**: Integrate with visuals layer
3. **Phase 4**: Add avatar animation based on `avatar_state`
4. **Phase 5**: Voice command integration with audio input
