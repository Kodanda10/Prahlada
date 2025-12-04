import mlx_lm
from mlx_lm import load, generate
import time
import statistics
import gc

# 1. Define Hindi Political Tweets (Raw Data)
tweets = [
    "छत्तीसगढ़ के रायगढ़ में जल संसाधन विभाग की नई परियोजना पर सवाल उठ रहे हैं। क्या इससे किसानों को सच में फायदा होगा या यह सिर्फ चुनावी वादा है? #Chhattisgarh #Politics",
    "यूपी के हरदोई में विपक्ष ने सरकार की नीतियों के खिलाफ मोर्चा खोला। बेरोजगारी और महंगाई पर तीखे प्रहार किए। आगामी चुनाव में इसका क्या असर होगा?",
    "मड़ियाहू विधानसभा में सड़क निर्माण कार्य रुका पड़ा है। स्थानीय विधायक की चुप्पी पर जनता में आक्रोश है। विकास के दावों की पोल खुल रही है।",
    "ओडिशा के धर्मशाला में BJD और BJP के बीच कड़ी टक्कर। सोशल मीडिया पर वार-पलटवार जारी। युवा मतदाता किस ओर जाएंगे?",
    "Breaking: केंद्र सरकार ने किसानों के लिए नई सब्सिडी योजना का ऐलान किया। विपक्ष ने इसे 'लॉलीपॉप' बताया। #Politics #India"
]

# 2. Define the System Prompt for Enrichment
system_instruction = "नीचे दिए गए ट्वीट का विश्लेषण करें। इसमें से 'Entity' (नेता/पार्टी/स्थान) निकालें और 'Sentiment' (सकारात्मक/नकारात्मक/तटस्थ) बताएं। JSON format."

# Prepare Prompts (Chat Template Format)
def apply_template(tokenizer, tweet):
    if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template:
        messages = [{"role": "user", "content": f"{system_instruction}\n\nTweet: {tweet}"}]
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return f"{system_instruction}\n\nTweet: {tweet}\nAnswer:"

# 3. Models Config

models = [
    {"name": "Llama-3.1-8B", "path": "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"},
]

print(f"{'Model':<20} | {'Load Time':<10} | {'TPS':<10} | {'TTFT (ms)':<10}")
print("-" * 60)

for m in models:
    try:
        # Load Model
        start_load = time.time()
        model, tokenizer = load(m["path"])
        load_time = time.time() - start_load
        
        # Prepare Batch Prompts
        batch_prompts = [apply_template(tokenizer, t) for t in tweets]
        
        # WARMUP (Crucial for M4 to wake up the NPU)
        _ = generate(model, tokenizer, prompt=batch_prompts[0], max_tokens=10, verbose=False)
        
        # BATCH GENERATION (The New Feature: Passing a List)
        # Note: If installed mlx-lm version supports list input directly in generate(), this works.
        # Otherwise, we iterate. We simulate the batch call for timing purposes if API differs.
        
        start_gen = time.time()
        
        # We process one by one to get strict per-request metrics, 
        # or use batch if mlx_textgen is available. 
        # For standard mlx_lm, we loop but keep model loaded (High Throughput).
        
        token_counts = []
        gen_times = []
        
        print(f"\nTesting {m['name']}...")
        
        for i, prompt in enumerate(batch_prompts):
            t0 = time.time()
            response = generate(model, tokenizer, prompt=prompt, max_tokens=200, verbose=False)
            t1 = time.time()
            
            gen_time = t1 - t0
            tokens = len(tokenizer.encode(response))
            token_counts.append(tokens)
            gen_times.append(gen_time)
            
            # Print full result sample for quality check
            if i == 0:
                print(f"Sample Output ({m['name']}): {response}")

        avg_tps = sum(token_counts) / sum(gen_times)
        avg_ttft = (sum(gen_times) / len(gen_times)) * 1000 / 10 # Approx approximation without stream
        
        print(f"{m['name']:<20} | {load_time:.2f}s     | {avg_tps:.2f}      | {avg_ttft:.0f}")

        # Clean up memory
        del model
        del tokenizer
        gc.collect()
        
    except Exception as e:
        print(f"Error testing {m['name']}: {e}")
