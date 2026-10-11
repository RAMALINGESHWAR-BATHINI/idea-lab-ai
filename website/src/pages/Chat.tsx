import { useState, useEffect, useRef } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { api } from "@/api/client";

interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system" | "tool";
  content: string | null;
  tool_name: string | null;
  tool_args: Record<string, any> | null;
  tool_result: Record<string, any> | null;
  sources: any[] | null;
  tokens: number | null;
  created_at: string;
}

interface ChatResponse {
  content: string;
  sources: Array<{ url: string; title: string | null }>;
  tool_calls: Array<{ name: string; arguments: Record<string, any> }>;
  conversation_id: string | null;
  ai_available: boolean;
}

export function Chat() {
  const { token } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [aiAvailable, setAiAvailable] = useState<boolean | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: "user-" + Date.now(),
      role: "user",
      content: input,
      tool_name: null,
      tool_args: null,
      tool_result: null,
      sources: null,
      tokens: null,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await api.post<ChatResponse>(
        "/ai/chat",
        {
          message: input,
          conversation_id: conversationId,
          use_search: true,
        },
        token || undefined,
      );

      setAiAvailable(response.ai_available);
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      const assistantMessage: ChatMessage = {
        id: "assistant-" + Date.now(),
        role: "assistant",
        content: response.content,
        tool_name: null,
        tool_args: response.tool_calls.length > 0 ? response.tool_calls[0].arguments : null,
        tool_result: null,
        sources: response.sources,
        tokens: null,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      const errorMessage: ChatMessage = {
        id: "error-" + Date.now(),
        role: "assistant",
        content:
          err.body?.error?.message ||
          "Failed to get response. The AI may be unavailable.",
        tool_name: null,
        tool_args: null,
        tool_result: null,
        sources: null,
        tokens: null,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      setAiAvailable(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <div className="max-w-4xl mx-auto w-full flex-1 flex flex-col">
        <div className="border-b bg-white px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-900">IdeaLab AI Assistant</h1>
          {aiAvailable === false && (
            <p className="text-sm text-yellow-600 mt-1">
              AI is currently unavailable. The website remains functional.
            </p>
          )}
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <div className="text-4xl mb-4">🤖</div>
              <p className="mb-2">
                Hello! I'm the IdeaLab AI assistant. How can I help you today?
              </p>
              <p className="text-sm">
                Ask me about projects, events, people, or general questions.
              </p>
            </div>
          ) : (
            messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))
          )}
          {isLoading && (
            <div className="flex justify-center py-6">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="border-t bg-white p-4">
          <div className="flex items-end space-x-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Type a message..."
              rows={1}
              className="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !input.trim()}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 transition-colors"
            >
              Send
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-2">
            Press Enter to send, Shift+Enter for new line.
          </p>
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 ${
          isUser
            ? "bg-primary-600 text-white"
            : "bg-white border border-gray-200 text-gray-900"
        }`}
      >
        {message.content && <p className="whitespace-pre-wrap">{message.content}</p>}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-200">
            <p className="text-xs font-medium">Sources:</p>
            {message.sources.map((s, i) => (
              <div key={i} className="text-xs mt-1">
                <a
                  href={s.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={isUser ? "text-blue-200" : "text-primary-600"}
                >
                  {s.title || s.url}
                </a>
              </div>
            ))}
          </div>
        )}
        {message.tool_name && (
          <div className="mt-2 pt-2 border-t border-gray-200">
            <p className="text-xs">
              Tool: <strong>{message.tool_name}</strong>
            </p>
          </div>
        )}
        <p className="text-xs opacity-50 mt-1">
          {new Date(message.created_at).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
    </div>
  );
}
