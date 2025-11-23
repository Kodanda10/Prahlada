
export enum ParsingStatus {
  SUCCESS = 'SUCCESS',
  PARTIAL = 'PARTIAL',
  FAILED = 'FAILED',
  PENDING = 'PENDING'
}

export interface ParsedLocation {
  canonical?: string;
  district?: string;
  location_type?: 'rural' | 'urban' | 'district' | '';
  hierarchy_path?: string[];
  assembly?: string | null;
  block?: string | null;
  gp?: string | null;          // Gram Panchayat (Rural)
  village?: string | null;     // Rural
  ulb?: string | null;         // Urban Local Body
  ward?: string | null;        // Urban Ward
  zone?: string | null;        // Urban Zone
  canonical_key?: string;
  source?: string;
  visit_count?: number;
  lat?: number;
  lng?: number;
}

export interface ParsedDataV8 {
  event_type: string;
  event_type_secondary: string[];
  event_date: string;
  location: ParsedLocation;
  people_mentioned: string[];
  people_canonical: string[];
  schemes_mentioned: string[];
  word_buckets: string[];
  target_groups: string[];
  communities: string[];
  organizations: string[];
  hierarchy_path: string[];
  visit_count: number;
  vector_embedding_id: string | null;
  confidence: number;
  review_status: 'pending' | 'approved' | 'rejected' | 'edited';
  needs_review: boolean;
  content_mode: string;
  is_other_original: boolean;
  is_rescued_other: boolean;
  rescue_tag: string | null;
  rescue_confidence_bonus: number;
  semantic_location_used: boolean;
  location_type: string;
}

export interface MetadataV8 {
  model: string;
  processing_time_ms: number;
  version: string;
}

export interface ParsedEvent {
  tweet_id: string;
  author_handle: string;
  text?: string;
  raw_text: string;
  created_at: string;
  processing_status: string;
  fetched_at: string;
  processed_at: string | null;
  is_parsed: boolean;
  parsed_event_id: string | null;
  review_status: 'pending' | 'approved' | 'rejected' | 'edited' | null;
  export_timestamp: string;
  export_version: string;
  is_clean: boolean;
  parsed_data_v8: ParsedDataV8;
  metadata_v8: MetadataV8;
  // Human-in-the-loop fields
  approved_by_human?: boolean;
  corrected_fields?: Record<string, any>;
  feedback_log?: {
    original_value: any;
    corrected_value: any;
    field_name: string;
    timestamp: string;
  }[];
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
