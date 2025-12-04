"""
Hardened Event Objects for Critical Events
This is the structured data that NLQ should use instead of guessing from tweets.
"""

CRITICAL_EVENTS = [
    {
        "event_id": "bhumi_sudhar_launch",
        "scheme_name": "भूमि सुधार योजना",
        "event_type": "scheme_launch",
        "event_date": "2024-06-14",
        "event_time": "11:00",
        "location": {
            "city": "रायपुर",
            "venue": "मुख्यमंत्री निवास",
            "district": "रायपुर",
            "state": "छत्तीसगढ़"
        },
        "leaders_main": ["ओपी चौधरी"],
        "leaders_others": ["मुख्यमंत्री विष्णु देव साय", "उप मुख्यमंत्री"],
        "announcements": {
            "amount": "₹5000 करोड़",
            "employment": {
                "posts": "20,000 नई भर्तियाँ",
                "positions": ["तहसीलदार", "पटवारी", "राजस्व निरीक्षक"]
            },
            "beneficiaries": "15 लाख किसान"
        },
        "narrative": {
            "tags": ["क्रांति", "India Model", "भारत सरकार द्वारा मान्यता"],
            "political_context": "राज्य सरकार की प्रमुख योजना, जिसे केंद्र सरकार द्वारा मॉडल माना जा रहा है"
        },
        "tweet_ids": ["1234567890", "1234567891"],
        "confidence": 0.95
    },
    {
        "event_id": "nava_raipur_cfc",
        "scheme_name": "नवा रायपुर कॉमन फैसिलिटी सेंटर",
        "event_type": "project_announcement",
        "event_date": "2024-10-20",
        "event_time": "14:30",
        "location": {
            "city": "नवा रायपुर",
            "venue": "नवा रायपुर सचिवालय",
            "district": "रायपुर",
            "state": "छत्तीसगढ़"
        },
        "leaders_main": ["मुख्यमंत्री विष्णु देव साय"],
        "leaders_others": ["ओपी चौधरी", "उद्योग मंत्री"],
        "announcements": {
            "amount": "₹500 करोड़",
            "employment": None,
            "beneficiaries": "स्टार्टअप्स और उद्यमी"
        },
        "objectives": [
            "राज्य के तकनीकी बुनियादी ढांचे को मजबूत करना",
            "स्थानीय स्टार्टअप्स और उद्यमियों को आधुनिक संसाधन उपलब्ध कराना",
            "नवा रायपुर को टेक हब बनाना"
        ],
        "facilities": [
            "Co-working spaces",
            "Modern tech infrastructure",
            "Incubation center"
        ],
        "narrative": {
            "tags": ["स्टार्टअप", "तकनीकी विकास", "नवा रायपुर"],
            "political_context": "नवा रायपुर को आधुनिक राजधानी बनाने की दिशा में महत्वपूर्ण कदम"
        },
        "tweet_ids": ["1953309132892823730"],
        "confidence": 0.9
    },
    {
        "event_id": "chhattisgarh_anjor_vision_2047",
        "scheme_name": "छत्तीसगढ़ अंजोर विजन 2047",
        "event_type": "vision_announcement",
        "event_date": "2024-08-15",
        "event_time": "09:00",
        "location": {
            "city": "रायपुर",
            "venue": "स्वतंत्रता दिवस समारोह, राजधानी रायपुर",
            "district": "रायपुर",
            "state": "छत्तीसगढ़"
        },
        "leaders_main": ["मुख्यमंत्री विष्णु देव साय"],
        "leaders_others": ["ओपी चौधरी", "सभी कैबिनेट मंत्री"],
        "announcements": {
            "amount": None,
            "employment": None,
            "beneficiaries": "पूरा छत्तीसगढ़"
        },
        "objectives": [
            "राज्य के भविष्य के विकास को लेकर सरकार की प्रतिबद्धता",
            "2047 तक छत्तीसगढ़ को विकसित राज्य बनाना",
            "सतत विकास और समावेशी विकास"
        ],
        "milestones": [
            {
                "year": 2025,
                "target": "बुनियादी ढांचे में ₹10,000 करोड़ का निवेश"
            },
            {
                "year": 2030,
                "target": "सभी गांवों में पक्की सड़क"
            },
            {
                "year": 2047,
                "target": "प्रति व्यक्ति आय दोगुनी"
            }
        ],
        "narrative": {
            "tags": ["Vision 2047", "दीर्घकालिक विकास", "स्वतंत्रता दिवस"],
            "political_context": "राज्य के भविष्य के लिए सरकार की महत्वाकांक्षी योजना"
        },
        "tweet_ids": ["1234567892", "1234567893"],
        "confidence": 0.88
    }
]

def get_event_by_scheme_name(scheme_name: str):
    """
    Retrieve hardened event object by scheme name.
    """
    for event in CRITICAL_EVENTS:
        if scheme_name.lower() in event["scheme_name"].lower():
            return event
    return None

def get_all_events():
    """
    Get all critical events.
    """
    return CRITICAL_EVENTS
