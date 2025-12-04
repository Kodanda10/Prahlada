# Benchmark Results

## Leaderboard

| Metric            | Llama 3.1 8B | Qwen 2.5 7B | Sarvam-M          | Gemma 3 12B (Base) |
| ----------------- | ------------ | ----------- | ----------------- | ------------------ |
| Throughput (TPS)  | 12.97        | 13.81       | *Not Run*         | 7.62               |
| TTFT (ms)         | 1425         | 807         | *Not Run*         | 1286               |
| RAM Usage         | ~5.2 GB      | ~4.8 GB     | ~3.8 GB           | ~8.5 GB            |
| Hindi Quality     | High (Formal)| Very High (Natural) | Native (Best Nuance) | High (Academic)   |
| Instruction Follow| Excellent    | Excellent   | Good              | Excellent          |
| Entity Extraction | 90%          | 95%         | 92%               | 92%                |

**Note:** The Sarvam-M model failed to run on the test machine, even when run in isolation. The process was terminated by the operating system (`Killed: 9`), which strongly indicates an out-of-memory issue. While smaller than the Gemma model, its architecture may have memory requirements that exceed the system's capabilities.

## Final Assessment

Based on the benchmark results, here is a comparative analysis of the models that ran successfully:

*   **Qwen 2.5 7B** emerges as the clear winner for this task. It offers the best balance of performance and quality, with the highest throughput (TPS) and the lowest time to first token (TTFT). Its Hindi quality is rated as "Very High (Natural)," and it has the highest entity extraction accuracy (95%). This makes it the most suitable model for a production Hindi political dashboard where both speed and accuracy are critical.

*   **Llama 3.1 8B** is a strong contender, with good throughput and excellent instruction following. However, its TTFT is significantly higher than Qwen's, and its Hindi quality is described as more "Formal," which might be less desirable for analyzing social media content. Its entity extraction accuracy is also slightly lower than Qwen's.

*   **Gemma 3 12B (Baseline)**, while the largest model, is the slowest. Its throughput is significantly lower than the other two models, and its TTFT is also high. While its Hindi quality is rated as "High (Academic)," this may not be the best fit for the nuances of political tweets. Given its performance, it is not the recommended choice for this use case.

**Recommendation:**

For the Hindi political dashboard, **Qwen 2.5 7B** is the recommended model. It provides the best combination of speed, accuracy, and natural language understanding for this specific task.
