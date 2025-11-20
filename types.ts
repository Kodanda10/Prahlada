
export enum ParsingStatus {
  SUCCESS = 'SUCCESS',
  PARTIAL = 'PARTIAL',
  FAILED = 'FAILED',
  PENDING = 'PENDING'
}

export interface ParsedLocation {
  district: string;
  constituency?: string; // Vidhan Sabha
  block?: string;        // Rural
  gp?: string;          // Gram Panchayat (Rural)
  village?: string;     // Rural
  ulb?: string;         // Urban Local Body
  zone?: string;        // Urban Zone
  ward?: string;        // Urban Ward
}

export interface ParsedEvent {
  tweet_id: string;
  created_at: string;
  raw_text: string;
  clean_text: string;
  event_type: string[];
  location_text: string;
  location_canonical?: ParsedLocation;
  scheme_tags: string[];
  people: string[];
  parsing_status: ParsingStatus;
  confidence_scores: {
    llm: number;
    regex: number;
    faiss: number;
  };
  logs: string[];
  review_status?: 'pending' | 'approved' | 'rejected' | 'edited';
}

export interface Stats {
  total_tweets: number;
  parsed_success: number;
  pending: number;
  errors: number;
}

export interface DashboardModule {
  id: string;
  title: string;
  isActive: boolean;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}
