import { useCallback, useEffect, useRef, useState } from "react";

// Minimal typings for the browser Web Speech API (not present in every TypeScript DOM lib).
interface SpeechAlternative {
  transcript: string;
}
interface SpeechResultLike {
  isFinal: boolean;
  length: number;
  [index: number]: SpeechAlternative;
}
interface SpeechEventLike {
  resultIndex: number;
  results: ArrayLike<SpeechResultLike>;
}
interface RecognitionLike {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  onresult: ((event: SpeechEventLike) => void) | null;
  onerror: ((event: { error: string }) => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
}
type RecognitionCtor = new () => RecognitionLike;

function getCtor(): RecognitionCtor | null {
  const w = window as unknown as {
    SpeechRecognition?: RecognitionCtor;
    webkitSpeechRecognition?: RecognitionCtor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

const ERROR_TEXT: Record<string, string> = {
  "not-allowed": "Microphone access was blocked. Allow the microphone for this site in your browser, or type your question instead.",
  "service-not-allowed": "Speech recognition is not allowed in this browser. Type your question instead.",
  "audio-capture": "No microphone was found. Connect one, or type your question instead.",
  "no-speech": "I didn't hear anything. Tap the microphone and try again.",
  network: "Speech recognition needs an internet connection in this browser. Type your question instead.",
  "language-not-supported": "This browser does not support speech recognition for the selected language.",
};

export function useSpeechRecognition(lang: string) {
  const supported = getCtor() !== null;
  const [listening, setListening] = useState(false);
  const [interim, setInterim] = useState("");
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<RecognitionLike | null>(null);

  const stop = useCallback(() => {
    recognitionRef.current?.stop(); // delivers the final result, then fires onend
  }, []);

  const abort = useCallback(() => {
    recognitionRef.current?.abort();
  }, []);

  const start = useCallback(
    (onFinal: (text: string) => void) => {
      const Ctor = getCtor();
      if (!Ctor || recognitionRef.current) return;

      setError(null);
      setInterim("");
      const recognition = new Ctor();
      recognition.lang = lang;
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;

      let finalText = "";
      let failed = false;

      recognition.onresult = (event) => {
        let interimText = "";
        for (let i = event.resultIndex; i < event.results.length; i += 1) {
          const result = event.results[i];
          const transcript = result[0]?.transcript ?? "";
          if (result.isFinal) finalText += transcript;
          else interimText += transcript;
        }
        setInterim(interimText);
      };
      recognition.onerror = (event) => {
        if (event.error === "aborted") return;
        failed = true;
        setError(ERROR_TEXT[event.error] ?? `Speech recognition failed (${event.error}).`);
      };
      recognition.onend = () => {
        recognitionRef.current = null;
        setListening(false);
        setInterim("");
        const text = finalText.trim();
        if (text && !failed) onFinal(text);
      };

      recognitionRef.current = recognition;
      try {
        recognition.start();
        setListening(true);
      } catch {
        recognitionRef.current = null;
        setError("Could not start the microphone. Try again.");
      }
    },
    [lang],
  );

  useEffect(() => () => recognitionRef.current?.abort(), []);

  return { supported, listening, interim, error, start, stop, abort };
}
