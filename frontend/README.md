# Frontend - CDF Classroom Assistant

React/Next.js frontend for the CDF classroom assistant. Provides deterministic rendering of backend responses using reusable, smart-board-friendly components.

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Backend

Create `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
npm run dev
```

Visit:
- **Demo Page**: http://localhost:3000/demo
- **Main App**: http://localhost:3000

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── globals.css       # Global TailwindCSS
│   │   ├── layout.tsx        # Root layout
│   │   ├── page.tsx          # Main application
│   │   └── demo/
│   │       └── page.tsx      # Phase 1 demo page
│   ├── components/
│   │   ├── index.ts          # Component exports
│   │   ├── ResponseRenderer.tsx
│   │   ├── AnswerBubble.tsx
│   │   ├── QuizCard.tsx
│   │   ├── LanguageBadge.tsx
│   │   ├── NextActions.tsx
│   │   └── ClarificationState.tsx
│   ├── types/
│   │   └── api.ts            # Backend response types
│   └── lib/
├── INTEGRATION.md            # Integration guide
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── next.config.js
```

## Components

### ResponseRenderer

Main component that renders backend `AssistantResponse` deterministically.

```tsx
import { ResponseRenderer } from "@/components";

<ResponseRenderer
  response={apiResponse}
  onNextAction={(action) => console.log(action)}
/>
```

### AnswerBubble

Displays explanations with bullets, examples, and recap.

```tsx
<AnswerBubble
  answer_text="Photosynthesis is..."
  title="Photosynthesis"
  bullets={["Plants make food...", "Water and CO2..."]}
  avatar_state="speaking"
/>
```

### QuizCard

One-question-at-a-time quiz interface.

```tsx
<QuizCard
  quiz={quizPayload}
  onAnswerSubmit={(qIdx, aIdx) => console.log(qIdx, aIdx)}
  onNavigate={(idx) => console.log(idx)}
/>
```

### LanguageBadge

Language mode indicator.

```tsx
<LanguageBadge language_mode="hinglish" />
```

### NextActions

Suggested next commands.

```tsx
<NextActions
  next_actions={["Explain...", "Quiz on..."]}
  onActionClick={(action) => handleCommand(action)}
/>
```

### ClarificationState

Shown when the command is unclear.

```tsx
<ClarificationState
  message="I didn't understand..."
  suggestions={["Try:", "Explain a topic", "Start a quiz"]}
/>
```

## API Integration

### Fetch Text Response

```typescript
const response = await fetch(
  `${process.env.NEXT_PUBLIC_API_URL}/api/v1/command/text`,
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: "user_123",
      text: "Explain photosynthesis",
    }),
  }
);

const data = await response.json();
// data = { status: "success", data: { ...AssistantResponse } }
```

### Fetch Audio Response

```typescript
const formData = new FormData();
formData.append("session_id", "user_123");
formData.append("audio", audioBlob, "audio.wav");

const response = await fetch(
  `${process.env.NEXT_PUBLIC_API_URL}/api/v1/command/audio`,
  {
    method: "POST",
    body: formData,
  }
);

const data = await response.json();
// data = { status: "success", data: { ...AssistantResponse } }
```

## Types

All TypeScript types mirror the backend schema:

```typescript
import { AssistantResponse, Mode, LanguageMode, AvatarState } from "@/types/api";

// AssistantResponse fields:
// - session_id: string
// - mode: "explain" | "quiz" | "followup" | "stop" | "unclear" | "clarify"
// - language_mode: "hinglish" | "english" | "hindi"
// - answer_text: string | null
// - quiz: QuizPayload | null
// - next_actions: string[]
// - confidence: number (0.0-1.0)
// - requires_clarification: boolean
// - avatar_state: "idle" | "speaking" | "listening" | "thinking"
// - source_refs: SourceRef[]
// - visuals: VisualRef[]
// - videos: VideoRef[]
```

## Styling

All components use **TailwindCSS** utilities. To customize:

1. Edit component files directly
2. Modify `tailwind.config.js` for theme changes
3. Use CSS modules or `globals.css` for global styles

## Demo Page

Visit http://localhost:3000/demo to see:
- Quick command buttons
- Example responses
- Error handling
- Raw response viewer (dev mode)

## Testing

### Test Backend Connection

```bash
curl -s http://localhost:8000/health | python -m json.tool
```

### Test Text Command

```bash
curl -s -X POST http://localhost:8000/api/v1/command/text \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_1",
    "text": "Explain photosynthesis"
  }' | python -m json.tool
```

See `backend/TESTING.md` for complete test suite.

## Environment Variables

### Development

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production

```
NEXT_PUBLIC_API_URL=https://api.example.com
```

## Build for Production

```bash
npm run build
npm run start
```

## Browser Support

- Chrome/Edge: Latest
- Firefox: Latest
- Safari: Latest
- Mobile browsers: iOS Safari 13+, Chrome Android

## Dependencies

- **Next.js 14.2+**: React framework
- **React 18+**: UI library
- **TailwindCSS 3.4+**: Styling
- **lucide-react**: Icons
- **clsx**: Utility for conditional classes

## Documentation

- [INTEGRATION.md](./INTEGRATION.md) - Detailed integration guide
- [backend/TESTING.md](../backend/TESTING.md) - Backend API testing
- [docs/api_contract.md](../docs/api_contract.md) - API contract

## Troubleshooting

### Backend Connection Error

```
Error: Failed to fetch from http://localhost:8000
```

**Solution**: Ensure backend is running:

```bash
cd backend
python -m app.main
```

### CORS Error

Backend CORS is pre-configured. If you still get errors:

1. Check `app/core/config.py` CORS settings
2. Verify frontend URL matches allowed origins
3. Try with `Content-Type: application/json`

### Styling Not Applied

```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

## Performance

- Components are lightweight renderers
- No external dependencies beyond essentials
- Optimized for smart board displays (large, readable)
- Supports up to 5-question quizzes comfortably

## Next Steps

1. **Try the demo**: http://localhost:3000/demo
2. **Read INTEGRATION.md**: Detailed usage guide
3. **Check backend TESTING.md**: API test examples
4. **Customize components**: Modify colors, fonts, layouts
5. **Add voice integration**: Connect STT/TTS services

## Support

For issues or questions, check:
- Component prop interfaces (TSDoc comments)
- Type definitions in `src/types/api.ts`
- Example code in `src/app/demo/page.tsx`
- Backend documentation in `backend/TESTING.md`
