
// Basic dictionary for common terms
const ENGLISH_TO_HINDI: Record<string, string> = {
    // Event Types
    "meeting": "बैठक",
    "visit": "दौरा",
    "inauguration": "उद्घाटन",
    "public_meeting": "जनसभा",
    "rally": "रैली",
    "inspection": "निरीक्षण",
    "review": "समीक्षा",
    "scheme distribution": "योजना वितरण",
    "scheme_distribution": "योजना वितरण",
    "felicitation": "सम्मान",
    "press_conference": "प्रेस वार्ता",
    "other": "अन्य",

    // Locations (Common)
    "raipur": "रायपुर",
    "bilaspur": "बिलासपुर",
    "durg": "दुर्ग",
    "bhilai": "भिलाई",
    "korba": "कोरबा",
    "raigarh": "रायगढ़",
    "janjgir": "जांजगीर",
    "champa": "चांपा",
    "ambikapur": "अंबिकापुर",
    "jagdalpur": "जगदलपुर",
    "bastar": "बस्तर",
    "dantewada": "दंतेवाड़ा",
    "sukma": "सुकमा",
    "bijapur": "बीजापुर",
    "narayanpur": "नारायणपुर",
    "kanker": "कांकेर",
    "kondagaon": "कोंडागांव",
    "mahasamund": "महासमुंद",
    "dhamtari": "धमतरी",
    "balod": "बालोद",
    "bemetara": "बेमेतरा",
    "kabirdham": "कबीरधाम",
    "kawardha": "कवर्धा",
    "mungeli": "मुंगेली",
    "gaurela": "गौरेला",
    "pendra": "पेंड्रा",
    "marwahi": "मरवाही",
    "surajpur": "सूरजपुर",
    "balrampur": "बलरामपुर",
    "korea": "कोरिया",
    "manendragarh": "मनेंद्रगढ़",
    "chirmiri": "चिरमिरी",
    "bharatpur": "भरतपुर",
    "sakti": "सक्ती",
    "sarangarh": "सारंगढ़",
    "bilaigarh": "बिलाईगढ़",
    "khairagarh": "खैरागढ़",
    "chuikhadan": "छुईखदान",
    "gandai": "गंडई",
    "mohla": "मोहला",
    "manpur": "मानपुर",
    "ambagarh": "अंबागढ़",
    "chowki": "चौकी",

    // People
    "narendra modi": "नरेंद्र मोदी",
    "modi": "मोदी",
    "amit shah": "अमित शाह",
    "vishnu deo sai": "विष्णु देव साय",
    "bhupesh baghel": "भूपेश बघेल",
    "ts singh deo": "टी एस सिंह देव",
    "raman singh": "रमन सिंह",
    "arun sao": "अरुण साव",
    "vijay sharma": "विजय शर्मा",
    "brijmohan agrawal": "बृजमोहन अग्रवाल",
    "op choudhary": "ओ पी चौधरी",

    // Titles / Roles
    "chief minister": "मुख्यमंत्री",
    "cm": "मुख्यमंत्री",
    "deputy chief minister": "उप मुख्यमंत्री",
    "dy cm": "उप मुख्यमंत्री",
    "minister": "मंत्री",
    "mla": "विधायक",
    "mp": "सांसद",
    "collector": "कलेक्टर",
    "sp": "पुलिस अधीक्षक",
    "commissioner": "आयुक्त",
    "secretary": "सचिव",
    "president": "अध्यक्ष",
    "vice president": "उपाध्यक्ष",
    "director": "निदेशक",
    "officer": "अधिकारी",
    "incharge": "प्रभारी",
};

// Reverse mapping for search
const HINDI_TO_ENGLISH: Record<string, string> = Object.entries(ENGLISH_TO_HINDI).reduce((acc, [eng, hi]) => {
    acc[hi] = eng;
    return acc;
}, {} as Record<string, string>);

export const translateToHindi = (text: string | null | undefined): string => {
    if (!text) return "";
    const lower = text.toLowerCase().trim();
    return ENGLISH_TO_HINDI[lower] || text;
};

export const transliterateToHindi = (text: string): string => {
    // This is a placeholder for a real transliteration library.
    // For now, we use the dictionary.
    return translateToHindi(text);
};

export const matchesSearch = (text: string | null | undefined, query: string): boolean => {
    if (!text || !query) return false;
    const t = text.toLowerCase();
    const q = query.toLowerCase();

    // Direct match
    if (t.includes(q)) return true;

    // Transliterated match (English Query -> Hindi Text)
    const hindiQuery = ENGLISH_TO_HINDI[q];
    if (hindiQuery && t.includes(hindiQuery)) return true;

    // Transliterated match (Hindi Query -> English Text)
    const englishQuery = HINDI_TO_ENGLISH[q];
    if (englishQuery && t.includes(englishQuery)) return true;

    return false;
};
