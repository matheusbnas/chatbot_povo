export interface NavigationProps {
  currentPage?: string;
  onNavigate?: (page: string) => void;
}

export interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string | Date;
  audio_url?: string;
}

export interface LegislativeProject {
  id: string;
  title: string;
  original_number: string;
  summary: string;
  simplified_summary: string;
  status: string;
  category: string;
  published_at: string;
  impacts: string[];
}

