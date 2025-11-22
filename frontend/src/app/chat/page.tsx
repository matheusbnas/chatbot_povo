"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Volume2, Mic, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { chatApi, ChatMessage } from "@/services/api";

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Load suggestions on mount
    chatApi.getSuggestions().then(setSuggestions).catch(console.error);
  }, []);

  const sendMessage = async (text?: string) => {
    const messageText = text || input;
    if (!messageText.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: messageText,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        message: messageText,
        conversation_history: messages,
        use_audio: false,
      });

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: response.message,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (response.suggestions) {
        setSuggestions(response.suggestions);
      }
    } catch (error: any) {
      console.error("Error sending message:", error);
      let errorContent = "Desculpe, ocorreu um erro ao processar sua mensagem.";

      // Try to get a user-friendly error message
      if (error?.formattedMessage) {
        errorContent = error.formattedMessage;
      } else if (error?.response?.data?.detail) {
        errorContent = error.response.data.detail;
      } else if (error?.response?.data?.message) {
        errorContent = error.response.data.message;
      } else if (error?.message) {
        errorContent = error.message;
      } else if (typeof error === "string") {
        errorContent = error;
      }

      // Format authentication errors more clearly
      if (
        errorContent.includes("401") ||
        errorContent.includes("authentication_error") ||
        errorContent.includes("x-api-key")
      ) {
        errorContent =
          "Erro de autenticação: Verifique se as chaves de API estão configuradas corretamente no servidor.";
      }

      const errorMessage: ChatMessage = {
        role: "assistant",
        content: errorContent,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
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
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm p-4 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition text-gray-700 hover:text-primary-600 font-medium"
              title="Voltar para página inicial"
            >
              <ArrowLeft className="w-5 h-5" />
              <span className="hidden sm:inline">Voltar</span>
            </Link>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-primary-600">
                Voz da Lei - Chat
              </h1>
              <p className="text-gray-600 text-sm">
                Pergunte sobre qualquer lei ou projeto
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <h2 className="text-2xl font-semibold text-gray-700 mb-4">
                Como posso ajudar?
              </h2>
              <p className="text-gray-500 mb-8">
                Faça uma pergunta sobre legislação brasileira
              </p>
              <div className="grid gap-3">
                {suggestions.slice(0, 4).map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => sendMessage(suggestion)}
                    className="p-3 bg-white rounded-lg shadow hover:shadow-md transition text-left"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message, idx) => (
            <div
              key={idx}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-2xl p-4 rounded-lg ${
                  message.role === "user"
                    ? "bg-primary-600 text-white"
                    : "bg-white shadow"
                }`}
              >
                <div className="break-words overflow-wrap-anywhere min-w-0">
                  {message.content.includes("Error") ||
                  message.content.includes("erro") ||
                  message.content.includes("401") ||
                  message.content.includes("authentication_error") ? (
                    <div className="space-y-2">
                      <p className="font-semibold mb-2">
                        {message.role === "assistant"
                          ? "Erro ao processar mensagem:"
                          : "Erro:"}
                      </p>
                      <div className="text-sm bg-red-50 border border-red-200 p-3 rounded overflow-x-auto max-w-full">
                        <pre className="whitespace-pre-wrap break-all text-red-800 font-mono text-xs">
                          {message.content}
                        </pre>
                      </div>
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap break-words overflow-wrap-anywhere leading-relaxed text-sm">
                      {message.content}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white shadow p-4 rounded-lg">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Suggestions */}
      {messages.length > 0 && suggestions.length > 0 && (
        <div className="border-t border-gray-200 p-4 bg-white">
          <div className="max-w-4xl mx-auto">
            <p className="text-sm text-gray-600 mb-2">Sugestões:</p>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => sendMessage(suggestion)}
                  className="px-3 py-1 bg-gray-100 rounded-full text-sm hover:bg-gray-200 transition"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Input */}
      <div className="border-t border-gray-200 p-4 bg-white">
        <div className="max-w-4xl mx-auto flex gap-2">
          <button className="p-3 rounded-lg bg-gray-100 hover:bg-gray-200 transition">
            <Mic className="w-5 h-5" />
          </button>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Digite sua pergunta..."
            className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            disabled={isLoading}
          />
          <button
            onClick={() => sendMessage()}
            disabled={isLoading || !input.trim()}
            className="p-3 rounded-lg bg-primary-600 text-white hover:bg-primary-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
