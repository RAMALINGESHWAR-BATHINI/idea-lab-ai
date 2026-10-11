# Voice Assistant

## Overview

The voice assistant is a **separate React application** that shares the same backend API as the website. It enables users to speak or type questions and receive spoken answers, making it ideal for hands-free interaction with IdeaLab information.

## Running

```powershell
cd voice
npm install
npm run dev
```

Open `http://localhost:5174`.

## Tech Stack
- React 19
- TypeScript 6.0
- Vite 8.3
- Web Speech API (browser-native, no external service)

## How It Works

### Speech Input
1. User clicks microphone button
2. Browser's `SpeechRecognition` API captures audio
3. Audio is transcribed to text in real-time
4. Transcription is sent to the AI chat endpoint

### Speech Output
1. AI response text is received
2. Browser's `SpeechSynthesis` API reads it aloud
3. User can pause/resume playback

### Channel Tagging
The voice app sends `channel: "voice"` to `/api/ai/chat`. The backend uses this to:
- Return shorter, more concise answers (suitable for spoken delivery)
- Adjust tone for voice interaction

## Features

- Voice input (speech-to-text)
- Voice output (text-to-speech)
- Fallback to typed input (Firefox doesn't support speech recognition)
- Consent notice before enabling microphone
- Works on localhost or HTTPS

## Browser Compatibility

| Browser | Speech Recognition | Speech Synthesis |
|---|---|---|
| Chrome/Edge | ✅ | ✅ |
| Firefox | ❌ (falls back to typing) | ✅ |
| Safari | ✅ | ✅ |

## Privacy Note

In Chrome/Edge, audio is typically sent to the browser vendor's speech service. The voice app shows a consent notice before enabling the microphone.

## API Integration

The voice app calls the same `/api/ai/chat` endpoint as the website, with the additional `channel: "voice"` field:

```json
{
  "message": "What events are happening this week?",
  "conversation_id": "abc-123",
  "use_search": true,
  "channel": "voice"
}
```

## Files

```
voice/
├── src/
│   ├── App.tsx          # Main app component
│   ├── main.tsx         # Entry point
│   └── index.css        # Styles
├── vite.config.ts       # Vite config (port 5174)
├── package.json
└── tsconfig.json
```