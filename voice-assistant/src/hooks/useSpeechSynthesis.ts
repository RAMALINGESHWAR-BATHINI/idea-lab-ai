import { useCallback, useEffect, useRef, useState } from "react";

const supported = typeof window !== "undefined" && "speechSynthesis" in window;

/** Remove markup that sounds wrong when read aloud (defensive; the backend already asks for plain text). */
export function stripForSpeech(text: string): string {
  return text
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`([^`]*)`/g, "$1")
    .replace(/https?:\/\/\S+/g, " ")
    .replace(/!?\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/^[#>*\-\s]+/gm, "")
    .replace(/[*_~|]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

/** Split into sentence-sized chunks; long utterances are cut off by some browsers. */
function chunk(text: string, max = 200): string[] {
  const sentences = text.match(/[^.!?\n]+[.!?]*/g) ?? [text];
  const chunks: string[] = [];
  let current = "";
  for (const sentence of sentences) {
    if ((current + sentence).length > max && current) {
      chunks.push(current.trim());
      current = "";
    }
    current += `${sentence} `;
  }
  if (current.trim()) chunks.push(current.trim());
  return chunks;
}

export function useSpeechSynthesis() {
  const [speaking, setSpeaking] = useState(false);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const runRef = useRef(0); // invalidates queued chunks when cancelled

  useEffect(() => {
    if (!supported) return;
    const load = () => setVoices(window.speechSynthesis.getVoices());
    load();
    window.speechSynthesis.addEventListener("voiceschanged", load);
    return () => window.speechSynthesis.removeEventListener("voiceschanged", load);
  }, []);

  const cancel = useCallback(() => {
    if (!supported) return;
    runRef.current += 1;
    window.speechSynthesis.cancel();
    setSpeaking(false);
  }, []);

  const speak = useCallback(
    (text: string, voiceURI: string | null, onDone?: () => void) => {
      const clean = stripForSpeech(text);
      if (!supported || !clean) {
        onDone?.();
        return;
      }
      window.speechSynthesis.cancel();
      runRef.current += 1;
      const run = runRef.current;
      const parts = chunk(clean);
      const voice = voiceURI
        ? window.speechSynthesis.getVoices().find((v) => v.voiceURI === voiceURI) ?? null
        : null;

      setSpeaking(true);
      const next = (index: number) => {
        if (run !== runRef.current) return; // cancelled or superseded
        if (index >= parts.length) {
          setSpeaking(false);
          onDone?.();
          return;
        }
        const utterance = new SpeechSynthesisUtterance(parts[index]);
        if (voice) {
          utterance.voice = voice;
          utterance.lang = voice.lang;
        }
        utterance.onend = () => next(index + 1);
        utterance.onerror = () => {
          if (run !== runRef.current) return;
          setSpeaking(false);
          onDone?.();
        };
        window.speechSynthesis.speak(utterance);
      };
      next(0);
    },
    [],
  );

  useEffect(() => cancel, [cancel]);

  return { supported, speaking, voices, speak, cancel };
}
