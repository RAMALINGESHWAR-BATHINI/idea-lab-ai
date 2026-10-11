import { useCallback, useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { ApiError, fetchMe, login, sendVoiceMessage } from "./lib/api.ts";
import type { ChatSource } from "./lib/api.ts";
import { useSpeechRecognition } from "./hooks/useSpeechRecognition.ts";
import { useSpeechSynthesis } from "./hooks/useSpeechSynthesis.ts";

type Phase = "idle" | "listening" | "thinking" | "speaking";

interface Turn {
  id: number;
  role: "user" | "assistant";
  text: string;
  sources?: ChatSource[];
  isError?: boolean;
}

const WEBSITE_URL: string = import.meta.env.VITE_WEBSITE_URL || "http://localhost:5173";
const LANG = typeof navigator !== "undefined" && navigator.language ? navigator.language : "en-US";

const PHASE_TEXT: Record<Phase, string> = {
  idle: "Ready. Tap the microphone and ask a question.",
  listening: "Listening… tap again when you finish.",
  thinking: "Thinking…",
  speaking: "Speaking… tap to stop.",
};

export default function App() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [thinking, setThinking] = useState(false);
  const [typed, setTyped] = useState("");
  const [voiceConsent, setVoiceConsent] = useState(false);
  const [readAloud, setReadAloud] = useState(true);
  const [voiceURI, setVoiceURI] = useState("");
  const [notice, setNotice] = useState<string | null>(null);

  const [token, setToken] = useState<string | null>(null);
  const [userName, setUserName] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const abortRef = useRef<AbortController | null>(null);
  const nextId = useRef(1);
  const logEndRef = useRef<HTMLDivElement>(null);

  const recognition = useSpeechRecognition(LANG);
  const synthesis = useSpeechSynthesis();

  const phase: Phase = recognition.listening
    ? "listening"
    : thinking
      ? "thinking"
      : synthesis.speaking
        ? "speaking"
        : "idle";

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [turns, thinking]);

  const addTurn = useCallback((turn: Omit<Turn, "id">) => {
    setTurns((prev) => [...prev, { ...turn, id: nextId.current++ }]);
  }, []);

  const ask = useCallback(
    async (text: string) => {
      const message = text.trim();
      if (!message) return;
      setNotice(null);
      synthesis.cancel();
      addTurn({ role: "user", text: message });
      setThinking(true);

      const controller = new AbortController();
      abortRef.current = controller;
      try {
        const result = await sendVoiceMessage(message, conversationId, token, controller.signal);
        if (result.conversation_id) setConversationId(result.conversation_id);
        addTurn({
          role: "assistant",
          text: result.content || "I don't have an answer for that.",
          sources: result.sources,
          isError: !result.ai_available,
        });
        if (readAloud && result.ai_available && result.content) {
          synthesis.speak(result.content, voiceURI || null);
        }
      } catch (err) {
        if (controller.signal.aborted && !(err instanceof ApiError)) {
          setNotice("Cancelled.");
        } else if (err instanceof ApiError && err.status === 401) {
          setToken(null);
          setUserName(null);
          setConversationId(null);
          setNotice("Your session expired. Sign in again, or continue as a visitor.");
        } else {
          addTurn({
            role: "assistant",
            text: err instanceof ApiError ? err.message : "Something went wrong. Please try again.",
            isError: true,
          });
        }
      } finally {
        abortRef.current = null;
        setThinking(false);
      }
    },
    [addTurn, conversationId, readAloud, synthesis, token, voiceURI],
  );

  const onMicClick = () => {
    if (phase === "listening") {
      recognition.stop();
    } else if (phase === "thinking") {
      abortRef.current?.abort();
    } else if (phase === "speaking") {
      synthesis.cancel();
    } else {
      synthesis.cancel();
      recognition.start((text) => void ask(text));
    }
  };

  const onTypedSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (thinking || recognition.listening) return;
    const text = typed;
    setTyped("");
    void ask(text);
  };

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [signingIn, setSigningIn] = useState(false);
  const [signInError, setSignInError] = useState<string | null>(null);

  const onSignIn = async (event: FormEvent) => {
    event.preventDefault();
    setSigningIn(true);
    setSignInError(null);
    try {
      const tokens = await login(email.trim(), password);
      const me = await fetchMe(tokens.access_token);
      setToken(tokens.access_token);
      setUserName(me.full_name);
      setConversationId(null);
      setPassword("");
    } catch (err) {
      setSignInError(err instanceof ApiError ? err.message : "Sign-in failed.");
    } finally {
      setSigningIn(false);
    }
  };

  const onSignOut = () => {
    setToken(null);
    setUserName(null);
    setConversationId(null);
  };

  const micLabel =
    phase === "listening"
      ? "Stop listening"
      : phase === "thinking"
        ? "Cancel request"
        : phase === "speaking"
          ? "Stop speaking"
          : "Start listening";

  return (
    <div className="app">
      <header className="header">
        <h1>IdeaLab Voice</h1>
        <a className="link" href={WEBSITE_URL} rel="noopener noreferrer">
          Back to IdeaLab website
        </a>
      </header>

      <main className="main">
        <section className="stage" aria-label="Voice control">
          {recognition.supported && voiceConsent ? (
            <button
              type="button"
              className={`mic mic--${phase}`}
              onClick={onMicClick}
              aria-label={micLabel}
              aria-pressed={phase === "listening"}
            >
              <svg viewBox="0 0 24 24" width="40" height="40" aria-hidden="true">
                <path
                  fill="currentColor"
                  d="M12 14a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2Z"
                />
              </svg>
            </button>
          ) : null}

          <p className="status" role="status" aria-live="polite">
            {recognition.supported && voiceConsent ? PHASE_TEXT[phase] : "Type a question below."}
          </p>
          {recognition.interim ? <p className="interim">“{recognition.interim}”</p> : null}
          {recognition.error ? (
            <p className="alert" role="alert">
              {recognition.error}
            </p>
          ) : null}
          {notice ? <p className="note">{notice}</p> : null}
        </section>

        {!recognition.supported ? (
          <p className="card">
            This browser does not support speech recognition, so voice input is unavailable. You can still type
            questions and have answers read aloud. Chrome, Edge and Safari support voice input.
          </p>
        ) : !voiceConsent ? (
          <div className="card">
            <h2>Before you use your microphone</h2>
            <p>
              Voice input uses your browser&apos;s built-in speech recognition. Depending on the browser, your audio may
              be processed by the browser vendor&apos;s online speech service. The text of what you say is then sent to
              the IdeaLab server, which answers using its configured AI provider. Nothing is recorded by this page.
            </p>
            <button type="button" className="btn" onClick={() => setVoiceConsent(true)}>
              I understand, enable voice input
            </button>
          </div>
        ) : null}

        <section className="log" role="log" aria-live="polite" aria-label="Conversation">
          {turns.length === 0 ? (
            <p className="empty">
              Try: “What is IdeaLab?”, “What events are coming up?” or “Which projects are being built?”
            </p>
          ) : null}
          {turns.map((turn) => (
            <article key={turn.id} className={`turn turn--${turn.role}${turn.isError ? " turn--error" : ""}`}>
              <h2 className="turn__who">{turn.role === "user" ? "You" : "IdeaLab"}</h2>
              <p>{turn.text}</p>
              {turn.sources && turn.sources.length > 0 ? (
                <ul className="sources">
                  {turn.sources.map((s) => (
                    <li key={s.url}>
                      <a href={s.url} target="_blank" rel="noopener noreferrer">
                        {s.title || s.url}
                      </a>
                    </li>
                  ))}
                </ul>
              ) : null}
            </article>
          ))}
          {thinking ? <p className="empty">Thinking…</p> : null}
          <div ref={logEndRef} />
        </section>

        <form className="typed" onSubmit={onTypedSubmit}>
          <label htmlFor="typed-input" className="sr-only">
            Type your question
          </label>
          <input
            id="typed-input"
            type="text"
            value={typed}
            maxLength={2000}
            onChange={(e) => setTyped(e.target.value)}
            placeholder="Or type your question…"
            autoComplete="off"
          />
          <button type="submit" className="btn" disabled={thinking || recognition.listening || !typed.trim()}>
            Send
          </button>
        </form>

        <section className="options" aria-label="Options">
          {synthesis.supported ? (
            <>
              <label className="check">
                <input type="checkbox" checked={readAloud} onChange={(e) => setReadAloud(e.target.checked)} />
                Read answers aloud
              </label>
              {synthesis.voices.length > 0 ? (
                <label className="voice-select">
                  Voice
                  <select value={voiceURI} onChange={(e) => setVoiceURI(e.target.value)}>
                    <option value="">Browser default</option>
                    {synthesis.voices.map((v) => (
                      <option key={v.voiceURI} value={v.voiceURI}>
                        {v.name} ({v.lang})
                      </option>
                    ))}
                  </select>
                </label>
              ) : null}
            </>
          ) : (
            <p className="note">Spoken answers are not supported in this browser.</p>
          )}
        </section>

        <details className="signin">
          <summary>{userName ? `Signed in as ${userName}` : "Sign in (optional)"}</summary>
          {userName ? (
            <button type="button" className="btn btn--ghost" onClick={onSignOut}>
              Sign out
            </button>
          ) : (
            <form onSubmit={onSignIn}>
              <p className="note">
                Visitors can ask public questions. Signing in unlocks what your IdeaLab role allows. Your session is
                kept only while this tab is open.
              </p>
              <label>
                Email
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="username" required />
              </label>
              <label>
                Password
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  required
                />
              </label>
              {signInError ? (
                <p className="alert" role="alert">
                  {signInError}
                </p>
              ) : null}
              <button type="submit" className="btn" disabled={signingIn}>
                {signingIn ? "Signing in…" : "Sign in"}
              </button>
            </form>
          )}
        </details>
      </main>
    </div>
  );
}
