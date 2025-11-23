# Cognitive Reasoning Engine Architecture

## Overview
The Cognitive Reasoning Engine transforms the parser into a self-correcting system. It uses local LLMs (Ollama) to analyze human corrections, deduce new logic rules, simulate them in a sandbox, and auto-deploy if safe.

## Pipeline
1.  **Human Correction**: User corrects a tweet in the Review UI (e.g., changes Event Type from "Meeting" to "Rally").
2.  **Trigger**: The correction event triggers the `CognitiveEngine`.
3.  **Ollama Auditor**:
    *   **Input**: Original Tweet, Old Rule (why it failed), Human Correction.
    *   **Process**: Uses `phi3.5` (or `gemma2`) to perform Root Cause Analysis (RCA).
    *   **Output**: Structured reasoning and a proposed logic fix (e.g., "Add 'massive gathering' to Rally keywords").
4.  **Rule Synthesizer**: Converts the LLM's text output into executable Python code (e.g., regex update).
5.  **Safety Sandbox**:
    *   **Simulation**: Runs the new logic on a random sample (5%) + Golden Dataset.
    *   **Analysis**: Calculates "Blast Radius" (collateral damage).
6.  **Gatekeeper**:
    *   **Decision**:
        *   **AUTO-DEPLOY**: If `Collateral Damage == 0` AND `Target Fixed`.
        *   **BLOCK**: If `Collateral Damage > 0`.
7.  **Production**: Updates the live parser logic (if approved).

## Schemas

### Reasoning Log
Stored in `data/reasoning_logs.jsonl`.

```typescript
interface ReasoningLog {
  id: string;
  timestamp: string;
  tweet_id: string;
  human_correction: {
    field: string;
    old_value: any;
    new_value: any;
  };
  analysis: {
    root_cause: string;
    missed_features: string[];
    llm_model: string;
    prompt_used: string;
  };
  proposal: {
    type: 'keyword_add' | 'regex_update' | 'weight_adjustment';
    target_component: string; // e.g., 'event_type_classifier'
    code_snippet: string;
  };
  simulation: {
    sample_size: number;
    target_fixed: boolean;
    collateral_damage_count: number;
    affected_tweets: string[]; // IDs
  };
  outcome: 'deployed' | 'blocked' | 'pending_review';
}
```

### Diff Report
Returned by the Sandbox.

```typescript
interface DiffReport {
  total_tested: number;
  changes: {
    tweet_id: string;
    old_result: any;
    new_result: any;
    is_improvement: boolean; // True if matches human label or improves confidence
    is_regression: boolean; // True if flips a previously correct result
  }[];
  metrics: {
    accuracy_delta: number;
    confidence_delta: number;
  };
}
```
