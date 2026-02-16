"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { searchVetInfo } from "@/utils/api";
import { normalizeResponse } from "@/utils/normalizeResponse";

type MessageRole = "user" | "assistant";

type Message = {
  id: string;
  role: MessageRole;
  content: string;
  created_at: number;
};

type ChatStorage = {
  meta: {
    session_id: string;
    updated_at: number;
  };
  messages: Message[];
};

const STORAGE_KEY = "vethipocratus_chat_v1";

function createId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function loadChatState(): ChatStorage {
  const fallback: ChatStorage = {
    meta: { session_id: createId(), updated_at: Date.now() },
    messages: [],
  };

  if (typeof window === "undefined") {
    return fallback;
  }

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);

    if (!raw) {
      return fallback;
    }

    const parsed = JSON.parse(raw) as ChatStorage;

    if (!parsed?.meta?.session_id || !Array.isArray(parsed?.messages)) {
      return fallback;
    }

    return parsed;
  } catch {
    return fallback;
  }
}

function saveChatState(sessionId: string, messages: Message[]): void {
  if (typeof window === "undefined") {
    return;
  }

  const payload: ChatStorage = {
    meta: {
      session_id: sessionId,
      updated_at: Date.now(),
    },
    messages,
  };

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
}

function AssistantContent({ content }: { content: string }) {
  return <p className="whitespace-pre-wrap text-gray-800">{content}</p>;
}

export default function ChatWidget() {
  const [sessionId, setSessionId] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastFailedUserId, setLastFailedUserId] = useState<string | null>(null);

  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const chat = loadChatState();
    setSessionId(chat.meta.session_id);
    setMessages(chat.messages);
  }, []);

  useEffect(() => {
    if (!sessionId) {
      return;
    }

    saveChatState(sessionId, messages);
  }, [messages, sessionId]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, error]);

  const lastAssistantAnswer = useMemo(() => {
    for (let i = messages.length - 1; i >= 0; i -= 1) {
      if (messages[i].role === "assistant") {
        return messages[i].content;
      }
    }

    return "";
  }, [messages]);

  const runRequest = async (userText: string) => {
    setLoading(true);
    setError("");

    try {
      const rawResult = await searchVetInfo(userText);
      const normalized = normalizeResponse(rawResult);

      const assistantMessage: Message = {
        id: createId(),
        role: "assistant",
        content: normalized.answerMarkdown || "(empty response)",
        created_at: Date.now(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setLastFailedUserId(null);
    } catch (requestError) {
      console.error("Error fetching data:", requestError);
      setError("Failed to retrieve data. Please try again.");
      setLastFailedUserId((prev) => prev ?? null);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async () => {
    const trimmed = query.trim();

    if (!trimmed || loading) {
      return;
    }

    const userMessage: Message = {
      id: createId(),
      role: "user",
      content: trimmed,
      created_at: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setLastFailedUserId(userMessage.id);
    setQuery("");

    await runRequest(trimmed);
  };

  const handleRetry = async () => {
    if (loading) {
      return;
    }

    const failedId = lastFailedUserId;
    if (!failedId) {
      return;
    }

    const targetMessage = messages.find(
      (msg) => msg.id === failedId && msg.role === "user"
    );
    if (!targetMessage) {
      return;
    }

    await runRequest(targetMessage.content);
  };

  const handleNewChat = () => {
    const nextSessionId = createId();
    setSessionId(nextSessionId);
    setMessages([]);
    setQuery("");
    setError("");
    setLastFailedUserId(null);

    if (typeof window !== "undefined") {
      window.localStorage.removeItem(STORAGE_KEY);
    }
  };

  const handleCopyLastAnswer = async () => {
    if (!lastAssistantAnswer || typeof navigator === "undefined" || !navigator.clipboard) {
      return;
    }

    try {
      await navigator.clipboard.writeText(lastAssistantAnswer);
    } catch (copyError) {
      console.error("Clipboard copy failed:", copyError);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-200 via-blue-200 to-purple-200 p-3 sm:p-4">
      <div className="mx-auto flex min-h-[calc(100vh-1.5rem)] max-w-2xl flex-col rounded-3xl bg-white shadow-xl sm:min-h-[calc(100vh-2rem)]">
        <header className="flex items-center justify-between gap-3 border-b border-gray-100 p-4 sm:p-5">
          <div>
            <h1 className="text-lg font-bold text-gray-900 sm:text-xl">Veterinary Chat</h1>
            <p className="text-xs text-gray-500 sm:text-sm">Session: {sessionId.slice(0, 8)}</p>
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleCopyLastAnswer}
              className="rounded-full border border-gray-200 px-3 py-2 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
              disabled={!lastAssistantAnswer}
            >
              Copy last answer
            </button>
            <button
              type="button"
              onClick={handleNewChat}
              className="rounded-full border border-gray-200 px-3 py-2 text-xs font-medium text-gray-700 hover:bg-gray-50"
            >
              New chat
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-4 sm:p-5">
          {messages.length === 0 ? (
            <p className="text-sm text-gray-500">Start the conversation by sending a question.</p>
          ) : (
            <div className="space-y-3">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`max-w-[92%] rounded-2xl px-4 py-3 text-sm ${
                    message.role === "user"
                      ? "ml-auto bg-blue-600 text-white"
                      : "mr-auto bg-gray-100 text-gray-900"
                  }`}
                >
                  {message.role === "assistant" ? (
                    <AssistantContent content={message.content} />
                  ) : (
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  )}
                </div>
              ))}
            </div>
          )}

          {loading && (
            <div className="mt-3 mr-auto inline-flex items-center gap-2 rounded-2xl bg-gray-100 px-4 py-3 text-sm text-gray-700">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-gray-400 border-t-transparent" />
              Assistant is typing...
            </div>
          )}

          {error && (
            <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              <p>{error}</p>
              <button
                type="button"
                onClick={handleRetry}
                className="mt-2 rounded-full bg-red-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
                disabled={loading || !lastFailedUserId}
              >
                Retry
              </button>
            </div>
          )}

          <div ref={endRef} />
        </div>

        <div className="border-t border-gray-100 p-4 sm:p-5">
          <div className="flex items-end gap-2">
            <textarea
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  void handleSend();
                }
              }}
              placeholder="Enter your query..."
              rows={2}
              className="min-h-[48px] flex-1 resize-none rounded-2xl border border-gray-300 px-4 py-3 text-sm text-gray-900 focus:outline-none focus:ring-4 focus:ring-blue-300"
            />
            <button
              type="button"
              onClick={() => void handleSend()}
              disabled={loading || !query.trim()}
              className="rounded-2xl bg-gradient-to-r from-blue-500 to-purple-500 px-4 py-3 text-sm font-medium text-white shadow-md transition hover:from-blue-600 hover:to-purple-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

