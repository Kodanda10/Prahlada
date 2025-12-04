import sys
from pathlib import Path
from typing import List, Dict, Any
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.vector_store import get_vector_store
from backend.cognitive.mlx_engine import MLXEngine

class NLQEngine:
    """
    Natural Language Query Engine.
    Uses RAG (Retrieval Augmented Generation) with Gemma 3.
    """
    def __init__(self):
        self.vector_store = get_vector_store()
        self.llm_engine = MLXEngine() # Reuses the singleton MLX engine
        
    def answer_query(self, query: str) -> Dict[str, Any]:
        """
        Answer a user query using RAG with event-grade 5W1H details.
        """
        print(f"🧠 NLQ: Processing query: {query}")
        
        # 1. Retrieve Context (10 tweets for comprehensive coverage)
        results = self.vector_store.search(query, k=10)
        
        # 2. Build rich event objects from retrieved tweets
        event_objects = []
        sources = []
        
        for res in results:
            meta = res['metadata']
            tweet_id = meta.get('tweet_id', 'unknown')
            text = meta.get('text', '')
            
            # Extract structured metadata
            metadata = meta.get('metadata', {})
            event_type = metadata.get('event_type', '')
            themes = metadata.get('themes', [])
            schemes = metadata.get('schemes', [])
            sentiment = metadata.get('sentiment', '')
            
            # Build event object
            event_obj = {
                "tweet_id": tweet_id,
                "text": text,
                "event_type": event_type,
                "schemes": schemes,
                "themes": themes,
                "sentiment": sentiment,
                "distance": res['distance']
            }
            
            event_objects.append(event_obj)
            sources.append({
                "tweet_id": tweet_id,
                "text": text,
                "distance": res['distance']
            })
        
        # 3. Format context with event objects
        context_entries = []
        for i, obj in enumerate(event_objects, 1):
            entry = f"""
[ट्वीट {i}]
ID: {obj['tweet_id']}
प्रकार: {obj['event_type']}
योजनाएं: {', '.join(obj['schemes']) if obj['schemes'] else 'N/A'}
विषय: {', '.join(obj['themes']) if obj['themes'] else 'N/A'}
भावना: {obj['sentiment']}

सामग्री:
{obj['text']}
"""
            context_entries.append(entry)
        
        context_str = "\n---\n".join(context_entries)
        
        # 4. Construct Event-Grade 5W1H Prompt
        system_prompt = """आप Project Dhruv के NLQ Interpretation Agent हैं — एक state-grade fact retrieval और explanation engine।

आपका काम user के किसी भी governance / scheme / development / event related query को high-structure query specification → event object retrieval → 5W1H final output में बदलना है।

🔥 CORE OBJECTIVE

User चाहे कितना भी simple सवाल पूछे — आपको उसका उत्तर लॉन्च-ग्रेड विवरण में देना है:

**5W1H Framework:**
1. **WHEN (कब)** – तारीख, समय, महीना, साल
2. **WHERE (कहाँ)** – शहर, जिला, स्थल (venue), विधानसभा क्षेत्र
3. **WHO (किसने)** – मुख्य नेता, मंत्री, अधिकारी का नाम
4. **WITH WHOM (किनके साथ)** – मंच पर उपस्थित अन्य नेता, अधिकारी, संगठन
5. **WHAT (क्या)** –
   • योजना/कार्यक्रम का नाम और उद्देश्य
   • घोषित राशि/बजट (₹ में)
   • रोजगार/भर्ती संख्या (पद + संख्या)
   • लाभार्थियों की अनुमानित संख्या
6. **HOW/CONTEXT (कैसे/संदर्भ)** –
   • यह किस प्रकार की event थी? (जनसभा, समीक्षा बैठक, उद्घाटन, घोषणा)
   • Political narrative क्या था? ("क्रांति", "मॉडल", "ऐतिहासिक", आदि)
   • कोई खास उद्धरण या slogan

**MANDATORY RULES:**
✔ हर उत्तर में 2-3 tweet snippets जरूर शामिल करें (तारीख के साथ)
✔ सिर्फ verified data ही लिखें - अनुमान नहीं
✔ यदि कोई जानकारी missing है तो स्पष्ट लिखें: "उपलब्ध ट्वीट्स में [field] का स्पष्ट उल्लेख नहीं मिला"
✔ Hindi-first, लेकिन scheme/project के official नाम वैसे ही रखें
✔ Tone: स्पष्ट, conversational, crisp, political-administrative

**OUTPUT FORMAT (हर उत्तर में यह संरचना अनिवार्य):**

**📋 सार (2-3 lines)**
योजना/कार्यक्रम का संक्षिप्त परिचय और उद्देश्य।

**📍 5W1H विवरण**
• **कब:** [तारीख, समय]
• **कहाँ:** [स्थान, venue, जिला]
• **किसने:** [मुख्य नेता/अधिकारी]
• **किनके साथ:** [अन्य उपस्थित लोग]
• **क्या घोषणा:** [मुख्य बिंदु]
• **राशि/भर्ती:** [संख्या और विवरण]
• **लाभार्थी:** [अनुमानित संख्या]
• **संदर्भ:** [event type, narrative]

**📱 ट्वीट साक्ष्य**
1. "..." — [तारीख]
2. "..." — [तारीख]
3. "..." — [तारीख]

**💡 मुख्य बिंदु**
• [Point 1]
• [Point 2]
• [Point 3]

**🔄 आगे जानने के लिए**
• "क्या आप [related topic] के बारे में जानना चाहेंगे?"
• "क्या आप district-wise breakdown देखना चाहेंगे?"
• "क्या आप timeline of updates देखना चाहेंगे?"

**DATA EXTRACTION RULES:**
1. तारीखों को ध्यान से extract करें - कोई अनुमान नहीं
2. राशि हमेशा ₹ चिन्ह के साथ
3. भर्ती/रोजगार में पद का नाम + संख्या दोनों
4. Tweet snippets में exact वाक्य का एक हिस्सा (15-20 शब्द max)
5. Missing data के लिए कभी assumption नहीं, साफ-साफ बताएं

अब नीचे दिए गए ट्वीट्स के आधार पर user के प्रश्न का उत्तर दें।"""

        user_prompt = f"""**संदर्भ (Context) - ट्वीट्स और Event Objects:**
{context_str}

**प्रश्न (Question):**
{query}

**विस्तृत उत्तर (ऊपर बताए गए format में):**"""

        # 5. Generate Answer
        print("   Generating event-grade 5W1H answer with Gemma 3...")
        response = self.llm_engine.generate_response(
            prompt=f"<bos><start_of_turn>user\n{system_prompt}\n\n{user_prompt}<end_of_turn>\n<start_of_turn>model\n",
            max_tokens=1536  # Increased for comprehensive answers
        )
        
        return {
            "query": query,
            "answer": response.strip(),
            "sources": sources,
            "event_objects_count": len(event_objects)
        }

# Singleton instance
_nlq_engine = None

def get_nlq_engine():
    global _nlq_engine
    if _nlq_engine is None:
        _nlq_engine = NLQEngine()
    return _nlq_engine
