"use client";

import { useState } from "react";
import {
  FileText,
  Sparkles,
  Loader2,
  Copy,
  Check,
  Volume2,
  VolumeX,
} from "lucide-react";
import Navigation from "@/components/Navigation";
import { simplificationApi } from "@/services/api";

type SimplificationLevel = "simple" | "moderate" | "technical";

export default function SimplifyPage() {
  const [text, setText] = useState("");
  const [simplifiedText, setSimplifiedText] = useState("");
  const [level, setLevel] = useState<SimplificationLevel>("simple");
  const [isLoading, setIsLoading] = useState(false);
  const [readingTime, setReadingTime] = useState<number | null>(null);
  const [copied, setCopied] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const handleSimplify = async () => {
    const trimmedText = text.trim();

    if (!trimmedText) {
      alert("Por favor, digite um texto para simplificar.");
      return;
    }

    if (trimmedText.length < 10) {
      alert("O texto deve ter pelo menos 10 caracteres para ser simplificado.");
      return;
    }

    setIsLoading(true);
    setSimplifiedText("");
    setReadingTime(null);

    try {
      const requestData = {
        text: trimmedText,
        target_level: level,
        include_audio: false,
      };

      console.log("Enviando requisição de simplificação:", requestData);

      const result = await simplificationApi.simplify(requestData);

      setSimplifiedText(result.simplified_text);
      setReadingTime(result.reading_time_minutes);
    } catch (error: any) {
      console.error("Erro ao simplificar:", error);

      let errorMessage =
        "Erro ao simplificar texto. Verifique sua conexão e tente novamente.";

      if (error?.response?.status === 422) {
        const detail = error?.response?.data?.detail;
        if (Array.isArray(detail)) {
          // Erros de validação do Pydantic
          const validationErrors = detail
            .map((err: any) => {
              const field = err.loc?.join(".") || "campo";
              const msg = err.msg || "erro de validação";
              return `${field}: ${msg}`;
            })
            .join("\n");
          errorMessage = `Erro de validação:\n${validationErrors}`;
        } else if (typeof detail === "string") {
          errorMessage = detail;
        } else {
          errorMessage =
            "O texto enviado não está no formato correto. Verifique se tem pelo menos 10 caracteres.";
        }
      } else if (error?.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error?.message) {
        errorMessage = error.message;
      }

      alert(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    if (simplifiedText) {
      navigator.clipboard.writeText(simplifiedText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const speakText = (textToSpeak: string) => {
    if ("speechSynthesis" in window) {
      // Se já está falando, parar
      if (isSpeaking) {
        window.speechSynthesis.cancel();
        setIsSpeaking(false);
        return;
      }

      // Parar qualquer fala anterior
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(textToSpeak);
      utterance.lang = "pt-BR";
      utterance.rate = 0.9;
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utterance);
    } else {
      console.warn("Seu navegador não suporta síntese de voz");
    }
  };

  const exampleTexts = [
    {
      title: "Artigo de Lei",
      text: "Art. 1º Esta Lei institui o Programa Nacional de Acesso à Internet Gratuita em estabelecimentos de ensino público, com o objetivo de promover a inclusão digital e o acesso à informação educacional.",
    },
    {
      title: "Parágrafo Jurídico",
      text: "Parágrafo único. O disposto no caput deste artigo não se aplica aos casos em que a parte interessada comprove, mediante documentação hábil, a impossibilidade de cumprimento do prazo estabelecido, desde que a solicitação de prorrogação seja apresentada com antecedência mínima de 30 (trinta) dias da data limite.",
    },
    {
      title: "Ementa de Projeto",
      text: "Altera a Lei nº 9.394, de 20 de dezembro de 1996, que estabelece as diretrizes e bases da educação nacional, para dispor sobre a obrigatoriedade da oferta de educação em tempo integral nos estabelecimentos de ensino público de educação básica.",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-sky-50">
      <Navigation />

      <main className="max-w-6xl mx-auto px-4 py-8 sm:py-12 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <div className="inline-block bg-gradient-to-br from-blue-500 to-blue-600 p-3 rounded-2xl mb-4 shadow-lg">
            <FileText className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
            Simplificação de Textos Jurídicos
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Transforme linguagem jurídica complexa em texto claro e acessível
            que todos podem entender
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-6 mb-6">
          {/* Painel Esquerdo - Entrada */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">
                Texto Original
              </h2>
              <span
                className={`text-sm ${
                  text.trim().length < 10 && text.trim().length > 0
                    ? "text-red-600 font-medium"
                    : text.trim().length >= 10
                    ? "text-green-600"
                    : "text-gray-500"
                }`}
              >
                {text.length} caracteres
                {text.trim().length > 0 && text.trim().length < 10 && (
                  <span className="ml-1">(mínimo 10)</span>
                )}
              </span>
            </div>

            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Cole aqui o texto jurídico que deseja simplificar..."
              className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none text-gray-900"
            />

            <div className="mt-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nível de Simplificação
                </label>
                <select
                  value={level}
                  onChange={(e) =>
                    setLevel(e.target.value as SimplificationLevel)
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="simple">Simples (Linguagem Cidadã)</option>
                  <option value="moderate">
                    Moderado (Linguagem Acessível)
                  </option>
                  <option value="technical">
                    Técnico (Mantém Termos Jurídicos)
                  </option>
                </select>
              </div>

              <button
                onClick={handleSimplify}
                disabled={!text.trim() || text.trim().length < 10 || isLoading}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-blue-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Simplificando...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Simplificar Texto
                  </>
                )}
              </button>
            </div>

            {/* Exemplos */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-sm font-medium text-gray-700 mb-3">
                Exemplos para testar:
              </p>
              <div className="space-y-2">
                {exampleTexts.map((example, index) => (
                  <button
                    key={index}
                    onClick={() => setText(example.text)}
                    className="w-full text-left text-sm bg-gray-50 hover:bg-gray-100 text-gray-700 px-3 py-2 rounded-lg transition-colors"
                  >
                    {example.title}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Painel Direito - Resultado */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">
                Texto Simplificado
              </h2>
              {simplifiedText && (
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleCopy}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    title="Copiar texto"
                  >
                    {copied ? (
                      <Check className="w-5 h-5 text-green-600" />
                    ) : (
                      <Copy className="w-5 h-5 text-gray-600" />
                    )}
                  </button>
                  {isSpeaking ? (
                    <button
                      onClick={() => {
                        if ("speechSynthesis" in window) {
                          window.speechSynthesis.cancel();
                        }
                        setIsSpeaking(false);
                      }}
                      className="p-2 rounded-lg bg-red-50 hover:bg-red-100 transition-colors flex items-center gap-2 text-sm text-red-700 border border-red-200"
                      title="Parar áudio"
                    >
                      <VolumeX className="w-5 h-5 text-red-600" />
                      <span className="font-medium">Parar</span>
                    </button>
                  ) : (
                    <button
                      onClick={() => speakText(simplifiedText)}
                      className="p-2 rounded-lg bg-blue-50 hover:bg-blue-100 transition-colors flex items-center gap-2 text-sm text-blue-700"
                      title="Ouvir texto"
                    >
                      <Volume2 className="w-5 h-5" />
                      <span>Ouvir</span>
                    </button>
                  )}
                </div>
              )}
            </div>

            {simplifiedText ? (
              <div className="space-y-4">
                <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
                  <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">
                    {simplifiedText}
                  </p>
                </div>

                {readingTime && (
                  <div className="text-sm text-gray-600">
                    ⏱️ Tempo estimado de leitura: {readingTime.toFixed(1)}{" "}
                    minutos
                  </div>
                )}
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center border-2 border-dashed border-gray-300 rounded-lg">
                <div className="text-center text-gray-400">
                  <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>O texto simplificado aparecerá aqui</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Informações */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">
            Como funciona?
          </h3>
          <div className="grid md:grid-cols-3 gap-4 text-sm text-gray-600">
            <div>
              <div className="font-semibold text-gray-900 mb-1">
                1. Cole o texto
              </div>
              <p>Cole qualquer texto jurídico que deseja simplificar</p>
            </div>
            <div>
              <div className="font-semibold text-gray-900 mb-1">
                2. Escolha o nível
              </div>
              <p>Selecione o nível de simplificação adequado ao seu público</p>
            </div>
            <div>
              <div className="font-semibold text-gray-900 mb-1">
                3. Obtenha o resultado
              </div>
              <p>
                Receba o texto em linguagem clara e acessível, pronto para
                compartilhar
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
