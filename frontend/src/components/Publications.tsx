"use client";

import { useState } from "react";
import {
  Search,
  Calendar,
  Tag,
  ExternalLink,
  Volume2,
  Filter,
} from "lucide-react";
import { LegislativeProject } from "@/types";

export default function Publications() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [speakingId, setSpeakingId] = useState<string | null>(null);

  const mockProjects: LegislativeProject[] = [
    {
      id: "1",
      title: "PL 1234/2024 - Programa de Internet Gratuita em Escolas Públicas",
      original_number: "PL 1234/2024",
      summary:
        "Institui programa nacional de acesso gratuito à internet em todas as escolas públicas do Brasil",
      simplified_summary:
        "Este projeto quer levar internet de graça para todas as escolas públicas do país. A ideia é que todos os alunos possam estudar online, fazer pesquisas e ter as mesmas chances de aprender, não importa se moram na cidade ou no interior.",
      status: "Em tramitação",
      category: "Educação",
      published_at: "2024-03-15",
      impacts: [
        "Mais de 150 mil escolas receberiam internet",
        "Beneficia cerca de 40 milhões de estudantes",
        "Ajuda a reduzir desigualdade digital",
      ],
    },
    {
      id: "2",
      title: "PL 2456/2024 - Redução de Tarifas no Transporte Público",
      original_number: "PL 2456/2024",
      summary:
        "Estabelece critérios para redução de tarifas de transporte público em horários de menor movimento",
      simplified_summary:
        "Quer baratear o preço do ônibus, metrô e trem fora dos horários de pico. Por exemplo, quem pega transporte depois das 20h ou antes das 6h da manhã pagaria menos. O objetivo é ajudar trabalhadores noturnos e quem tem horário diferente.",
      status: "Aprovado na Câmara",
      category: "Transporte",
      published_at: "2024-02-20",
      impacts: [
        "Cerca de 15 milhões de trabalhadores podem economizar",
        "Tarifa pode ficar até 30% mais barata fora do horário de pico",
        "Estimula o uso do transporte público",
      ],
    },
    {
      id: "3",
      title: "PL 3789/2024 - Licença Maternidade para Mães de Prematuros",
      original_number: "PL 3789/2024",
      summary:
        "Estende o período de licença-maternidade para mães de bebês prematuros",
      simplified_summary:
        "As mães de bebês que nascem antes do tempo (prematuros) teriam mais dias de licença-maternidade. O tempo extra seria o mesmo que o bebê ficou internado no hospital. Assim, a mãe pode cuidar melhor da criança quando chegar em casa.",
      status: "Em análise no Senado",
      category: "Saúde",
      published_at: "2024-01-10",
      impacts: [
        "Beneficia cerca de 340 mil mães por ano",
        "Melhora saúde e vínculo entre mãe e bebê",
        "Reduz readmissões hospitalares de prematuros",
      ],
    },
    {
      id: "4",
      title: "PL 4521/2024 - Isenção de IPTU para Baixa Renda",
      original_number: "PL 4521/2024",
      summary:
        "Cria critérios nacionais para isenção de IPTU de famílias de baixa renda",
      simplified_summary:
        "Famílias que ganham até 2 salários mínimos não precisariam pagar IPTU (imposto da casa). O projeto define regras iguais para todo o Brasil, mas cada cidade ainda pode ajustar os valores. A ideia é aliviar o bolso de quem mais precisa.",
      status: "Em tramitação",
      category: "Economia",
      published_at: "2024-04-05",
      impacts: [
        "Mais de 8 milhões de famílias podem ser beneficiadas",
        "Economia média de R$ 800 por ano por família",
        "Ajuda a manter famílias em suas casas",
      ],
    },
  ];

  const categories = [
    "all",
    "Educação",
    "Saúde",
    "Transporte",
    "Economia",
    "Segurança",
  ];

  const filteredProjects = mockProjects.filter((project) => {
    const matchesSearch =
      project.simplified_summary
        .toLowerCase()
        .includes(searchTerm.toLowerCase()) ||
      project.title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory =
      selectedCategory === "all" || project.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const speakText = (text: string, id: string) => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "pt-BR";
      utterance.rate = 0.9;
      utterance.onstart = () => setSpeakingId(id);
      utterance.onend = () => setSpeakingId(null);
      window.speechSynthesis.speak(utterance);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Aprovado na Câmara":
        return "bg-green-100 text-green-800";
      case "Em análise no Senado":
        return "bg-blue-100 text-blue-800";
      default:
        return "bg-yellow-100 text-yellow-800";
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Projetos de Lei Explicados
          </h1>
          <p className="text-lg text-gray-600">
            Entenda as leis que estão sendo discutidas agora, em linguagem clara
            e simples
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <input
                  type="text"
                  placeholder="Buscar por assunto, palavra-chave..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Filter className="h-5 w-5 text-gray-400" />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat === "all" ? "Todas as áreas" : cat}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="grid gap-6">
          {filteredProjects.map((project) => (
            <div
              key={project.id}
              className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow overflow-hidden"
            >
              <div className="p-6">
                <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
                          project.status
                        )}`}
                      >
                        {project.status}
                      </span>
                      <span className="flex items-center text-sm text-gray-500">
                        <Tag className="h-4 w-4 mr-1" />
                        {project.category}
                      </span>
                      <span className="flex items-center text-sm text-gray-500">
                        <Calendar className="h-4 w-4 mr-1" />
                        {new Date(project.published_at).toLocaleDateString(
                          "pt-BR"
                        )}
                      </span>
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-3">
                      {project.title}
                    </h2>
                  </div>
                </div>

                <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4 rounded">
                  <p className="text-gray-700 font-medium mb-2">
                    Em palavras simples:
                  </p>
                  <p className="text-gray-800 leading-relaxed">
                    {project.simplified_summary}
                  </p>
                  <button
                    onClick={() =>
                      speakText(project.simplified_summary, project.id)
                    }
                    className="mt-3 flex items-center space-x-2 text-blue-700 hover:text-blue-800 font-medium"
                  >
                    <Volume2 className="h-5 w-5" />
                    <span>
                      {speakingId === project.id
                        ? "Falando..."
                        : "Ouvir explicação"}
                    </span>
                  </button>
                </div>

                <div className="mb-4">
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Como isso afeta você:
                  </h3>
                  <ul className="space-y-2">
                    {project.impacts.map((impact, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-blue-600 mr-2">•</span>
                        <span className="text-gray-700">{impact}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <details className="group">
                    <summary className="cursor-pointer text-blue-700 hover:text-blue-800 font-medium flex items-center">
                      <span>Ver texto oficial completo</span>
                      <ExternalLink className="h-4 w-4 ml-1" />
                    </summary>
                    <p className="mt-3 text-sm text-gray-600 bg-gray-50 p-4 rounded">
                      {project.summary}
                    </p>
                  </details>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredProjects.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">
              Nenhum projeto encontrado com os filtros selecionados.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
