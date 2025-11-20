
import { ParsedEvent, ParsingStatus } from '../types';

export const MOCK_STATS = {
  total_tweets: 12450,
  parsed_success: 11200,
  pending: 840,
  errors: 410,
};

export const MOCK_EVENTS: ParsedEvent[] = [
  {
    tweet_id: '1765432109',
    created_at: '2023-10-24T10:30:00Z',
    raw_text: 'आज रायगढ़ जिले के खरसिया ब्लॉक में प्रधानमंत्री आवास योजना के लाभार्थियों के साथ समीक्षा बैठक की। #PMHousing',
    clean_text: 'आज रायगढ़ जिले के खरसिया ब्लॉक में प्रधानमंत्री आवास योजना के लाभार्थियों के साथ समीक्षा बैठक की।',
    event_type: ['समीक्षा बैठक'],
    location_text: 'खरसिया, जिला रायगढ़',
    location_canonical: {
      district: 'रायगढ़',
      constituency: 'खरसिया',
      block: 'खरसिया',
      gp: 'तियूर',
      village: 'तियूर'
    },
    scheme_tags: ['PMAY-G', 'आवास योजना'],
    people: ['जिला कलेक्टर'],
    parsing_status: ParsingStatus.SUCCESS,
    confidence_scores: { llm: 0.95, regex: 1.0, faiss: 0.98 },
    logs: ['LLM identified event: Review Meeting', 'FAISS matched Kharsia -> Raigarh']
  }
];

// UPDATED: Hindi locations for Review Queue Breadcrumbs
export const MOCK_REVIEW_QUEUE: ParsedEvent[] = [
  {
    tweet_id: '1001',
    created_at: '2024-03-10T09:00:00Z',
    raw_text: 'Visited Gram Panchayat Jobi today. Reviewed the progress of PMAY houses.',
    clean_text: 'आज ग्राम पंचायत जोबी का दौरा किया। प्रधानमंत्री आवास योजना के घरों की प्रगति की समीक्षा की।',
    event_type: ['दौरा', 'निरीक्षण'],
    location_text: 'जोबी, खरसिया',
    location_canonical: {
      district: 'रायगढ़',
      constituency: 'खरसिया',
      block: 'खरसिया ब्लॉक',
      gp: 'जोबी',
      village: 'जोबी'
    },
    scheme_tags: ['पीएम आवास'],
    people: [],
    parsing_status: ParsingStatus.SUCCESS,
    confidence_scores: { llm: 0.9, regex: 1.0, faiss: 0.92 },
    logs: [],
    review_status: 'pending'
  },
  {
    tweet_id: '1002',
    created_at: '2024-03-10T11:30:00Z',
    raw_text: 'Inaugurated the new Community Hall in Ward 4, Gandhi Nagar zone.',
    clean_text: 'वार्ड 4, गांधी नगर जोन में नए सामुदायिक भवन का उद्घाटन किया।',
    event_type: ['उद्घाटन'],
    location_text: 'वार्ड 4, गांधी नगर',
    location_canonical: {
      district: 'रायगढ़',
      constituency: 'रायगढ़ शहर',
      ulb: 'रायगढ़ नगर निगम',
      zone: 'गांधी नगर',
      ward: 'वार्ड 04'
    },
    scheme_tags: ['इंफ्रा'],
    people: [],
    parsing_status: ParsingStatus.SUCCESS,
    confidence_scores: { llm: 0.85, regex: 0.8, faiss: 0.78 },
    logs: [],
    review_status: 'pending'
  }
];

export const DISTRICT_DATA = [
  { name: 'रायगढ़', value: 450 },
  { name: 'जशपुर', value: 320 },
  { name: 'सरगुजा', value: 210 },
  { name: 'बिलासपुर', value: 180 },
  { name: 'कोरबा', value: 150 },
];

export const EVENT_TYPE_DATA = [
  { name: 'जनसम्पर्क', value: 400, fill: '#06b6d4' },
  { name: 'सभा', value: 300, fill: '#3b82f6' },
  { name: 'समीक्षा बैठक', value: 200, fill: '#8b5cf6' },
  { name: 'उद्घाटन', value: 150, fill: '#ec4899' },
  { name: 'अन्य', value: 100, fill: '#64748b' },
];
