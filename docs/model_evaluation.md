# Model Evaluation: Phi-3.5 vs Gemma 2

## Context
The Cognitive Reasoning Engine requires a local LLM to perform two key tasks:
1.  **Auditor**: Root Cause Analysis (RCA) of parsing errors (Reasoning heavy).
2.  **Synthesizer**: Generating Python code fixes (Coding heavy).

## Comparison

| Feature | Phi-3.5 Mini (3.8B) | Gemma 2 (9B) |
| :--- | :--- | :--- |
| **Parameters** | 3.8 Billion | 9 Billion |
| **Reasoning** | Excellent (Textbook quality) | Strong (General purpose) |
| **Coding (HumanEval)** | ~62.8% | ~40.2% |
| **Context Window** | 128K Tokens | 8K Tokens |
| **Availability** | Needs Install | **Installed** |

## Analysis

### Reasoning (Auditor Role)
*   **Phi-3.5**: punched above its weight in reasoning benchmarks (GSM8K, ARC), often beating larger models. It is optimized for logical deduction.
*   **Gemma 2**: Being a 9B model, it has a broader world knowledge base, which is crucial for understanding the *semantic context* of tweets (e.g., political nuances, Hindi slang) that a smaller model might miss.

### Coding (Synthesizer Role)
*   **Phi-3.5**: Significantly outperforms Gemma 2 in standard coding benchmarks.
*   **Gemma 2**: While scoring lower on complex coding tasks, the specific requirement here is generating *simple* Python snippets (list appends, regex). A 9B model is generally sufficient for this with proper prompting.

### Resource & Efficiency
*   **Phi-3.5**: Extremely lightweight/fast.
*   **Gemma 2**: Heavier but fits in standard Mac memory (unified memory).

## Decision
**Selected Model: `phi3.5` (Primary) with `gemma2:latest` (Backup)**

**Rationale:**
1.  **Reasoning**: Phi-3.5's superior reasoning benchmarks make it the better choice for the Auditor role (RCA).
2.  **Reliability**: We implement a fallback mechanism. If `phi3.5` fails, the system automatically switches to `gemma2:latest`.
3.  **User Preference**: Explicit request to prioritize reasoning capability.

## Future Action
Monitor the fallback rate. If `phi3.5` proves unstable, investigate local resource constraints.
