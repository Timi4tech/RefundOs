import { useEffect, useRef, useState } from "react";
import { Bot, MessageCircle, Send, X } from "lucide-react";
import type { ChatMessage } from "../../types";

type SocketMessage =
  | {
      type: "processing";
      message_id: string;
      connection_id: string;
      message: string;
    }
  | {
      type: "assistant_message";
      message_id: string;
      connection_id: string;
      message: string;
    }
  | {
      type: "error";
      message: string;
    };

export function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [connected, setConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hello. I can help you understand refunds, statuses, and next steps.",
    },
  ]);

  function getWebSocketUrl(): string {
    const apiBaseUrl =
      import.meta.env.VITE_API_BASE_URL ??
      `${window.location.origin}/api/v1`;

    const websocketBaseUrl = apiBaseUrl
      .replace(/^https:/, "wss:")
      .replace(/^http:/, "ws:")
      .replace(/\/+$/, "");

    const token = localStorage.getItem("refund_access_token");
    if (!token) {
      throw new Error("Authentication token is missing.");
    }

    return `${websocketBaseUrl}/ws/chat?token=${encodeURIComponent(token)}`;
  }

  useEffect(() => {
    if (!open) return;

    let socket: WebSocket;

    try {
      socket = new WebSocket(getWebSocketUrl());
    } catch {
      setConnected(false);
      setBusy(false);
      return;
    }

    socketRef.current = socket;

    socket.onopen = () => {
      setConnected(true);
    };

    socket.onmessage = (event) => {
      try {
        const data: SocketMessage = JSON.parse(event.data);

        if (data.type === "processing") {
          setBusy(true);
          return;
        }

        if (data.type === "assistant_message") {
          setMessages((current) => [
            ...current,
            { role: "assistant", content: data.message },
          ]);
          setBusy(false);
          return;
        }

        if (data.type === "error") {
          setMessages((current) => [
            ...current,
            { role: "assistant", content: data.message },
          ]);
          setBusy(false);
        }
      } catch {
        setMessages((current) => [
          ...current,
          {
            role: "assistant",
            content: "I received an invalid response from the support service.",
          },
        ]);
        setBusy(false);
      }
    };

    socket.onerror = () => {
      setConnected(false);
      setBusy(false);
    };

    socket.onclose = (event) => {
      setConnected(false);
      setBusy(false);
      socketRef.current = null;

      if (event.code !== 1000 && open) {
        setMessages((current) => [
          ...current,
          {
            role: "assistant",
            content:
              "The support connection was closed. Please reopen the chat and try again.",
          },
        ]);
      }
    };

    return () => {
      socket.close(1000, "Chat closed");
      socketRef.current = null;
    };
  }, [open]);

  function send() {
    const message = input.trim();
    if (!message || busy) return;

    const socket = socketRef.current;
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: "The support service is not connected. Please try again.",
        },
      ]);
      return;
    }

    const history = messages.slice(-8).map((item) => ({
      role: item.role,
      content: item.content,
    }));

    setMessages((current) => [
      ...current,
      { role: "user", content: message },
    ]);
    setInput("");
    setBusy(true);

    socket.send(
      JSON.stringify({
        message,
        message_id: crypto.randomUUID(),
        history,
      })
    );
  }

  function closeChat() {
    setOpen(false);
    setBusy(false);
  }

  return (
    <>
      {open && (
        <div className="fixed bottom-24 right-5 z-50 flex h-[520px] w-[min(390px,calc(100vw-2rem))] flex-col overflow-hidden rounded-3xl border border-slateText-200 bg-white shadow-2xl">
          <div className="flex items-center justify-between bg-navy px-5 py-4 text-white">
            <div className="flex items-center gap-3">
              <div className="grid h-9 w-9 place-items-center rounded-xl bg-white/10">
                <Bot size={19} />
              </div>
              <div>
                <p className="font-semibold">Refund Assistant</p>
                <div className="flex items-center gap-1.5">
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${
                      connected ? "bg-green-400" : "bg-red-400"
                    }`}
                  />
                  <p className="text-xs text-white/60">
                    {connected ? "Secure support chat" : "Connecting..."}
                  </p>
                </div>
              </div>
            </div>
            <button type="button" onClick={closeChat} aria-label="Close chat">
              <X size={19} />
            </button>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto bg-slate-50 p-4">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`flex ${
                  m.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[82%] rounded-2xl px-3.5 py-2.5 text-sm ${
                    m.role === "user"
                      ? "rounded-br-md bg-navy text-white"
                      : "rounded-bl-md bg-white text-slateText-700 shadow-sm"
                  }`}
                >
                  {m.content}
                </div>
              </div>
            ))}

            {busy && (
              <div className="flex justify-start">
                <div className="rounded-2xl rounded-bl-md bg-white px-3.5 py-2.5 text-xs text-slateText-400 shadow-sm">
                  Assistant is thinking…
                </div>
              </div>
            )}
          </div>

          <div className="border-t border-slateText-100 bg-white p-3">
            <div className="flex gap-2">
              <input
                className="input flex-1"
                value={input}
                disabled={!connected || busy}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    send();
                  }
                }}
                placeholder={
                  connected ? "Ask about your refund…" : "Connecting to support…"
                }
              />
              <button
                type="button"
                className="btn-primary px-3"
                onClick={send}
                disabled={!connected || busy || !input.trim()}
                aria-label="Send message"
              >
                <Send size={17} />
              </button>
            </div>
          </div>
        </div>
      )}

      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="fixed bottom-5 right-5 z-50 grid h-14 w-14 place-items-center rounded-2xl bg-navy text-white shadow-xl transition hover:-translate-y-0.5"
        aria-label={open ? "Close chat" : "Open chat"}
      >
        {open ? <X size={22} /> : <MessageCircle size={22} />}
      </button>
    </>
  );
}
