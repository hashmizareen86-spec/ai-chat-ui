"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Sparkles } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    // Placeholder for streaming bot response
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: userMessage }),
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          if (lastMessage && lastMessage.role === "assistant") {
            lastMessage.content += chunk;
          }
          return newMessages;
        });
      }
    } catch (error) {
      console.error("Error streaming chat:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error: Unable to fetch response from backend." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex h-screen flex-col bg-slate-900 text-slate-100">
      {/* Header */}
      <header className="flex items-center gap-2 border-b border-slate-800 p-4">
        <Sparkles className="h-6 w-6 text-purple-400" />
        <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
          Gemini AI Studio
        </h1>
      </header>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center text-slate-500">
            <Bot className="h-12 w-12 mb-2 stroke-1" />
            <p>Start a conversation with Gemini AI...</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`flex items-start gap-3 ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {msg.role === "assistant" && (
                <div className="p-2 rounded-lg bg-purple-600/20 text-purple-400 border border-purple-500/30">
                  <Bot className="h-5 w-5" />
                </div>
              )}
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  msg.role === "user"
                    ? "bg-purple-600 text-white rounded-tr-none"
                    : "bg-slate-800 text-slate-200 border border-slate-700 rounded-tl-none whitespace-pre-wrap"
                }`}
              >
                {msg.content || (isLoading && index === messages.length - 1 ? "..." : "")}
              </div>
              {msg.role === "user" && (
                <div className="p-2 rounded-lg bg-slate-700 text-slate-300">
                  <User className="h-5 w-5" />
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-slate-800 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Gemini anything..."
          className="flex-1 rounded-xl bg-slate-800 border border-slate-700 px-4 py-3 text-slate-100 focus:outline-none focus:border-purple-500 transition-colors"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="rounded-xl bg-purple-600 px-5 py-3 font-semibold text-white hover:bg-purple-500 disabled:opacity-50 transition-colors flex items-center justify-center"
        >
          <Send className="h-5 w-5" />
        </button>
      </form>
    </main>
  );
}