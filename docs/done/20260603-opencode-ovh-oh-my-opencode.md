# OVHcloud AI Endpoints - Model Selection Guide

**Last Updated:** 2026-06-03
**Context:** OpenCode with OVHcloud AI Endpoints integration

## Getting Started with OpenCode

1. **Connect OpenCode to OVH**
   Run the connect command inside OpenCode:

   ```bash
   /connect
   ```

   Search for “OVHcloud AI Endpoints” and enter your API key when prompted.

2. **Select a model**
   List available models with `/models` and choose the **gpt-oss-120b** model (`ovhcloud/gpt-oss-120b`). This model offers strong reasoning capabilities at a low cost.

3. **Test the setup**
   Try a simple query, e.g., “What is 2+2?” or ask OpenCode to generate a small code snippet.

### Quick Recommendations

- **Best value:** `gpt-oss-120b` – 117B parameters, fp4 quantization, excellent reasoning and responsiveness.
- **Fast & cheap alternative:** `gpt-oss-20b` – 21B parameters, very low latency.
- **High‑performance option:** `qwen3.6-27b` – 35B parameters, multimodal support.

## Models Comparable to Claude Sonnet for Interactive Chat

Based on the [OVHcloud catalog](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/catalog/), here are the models suitable for **interactive chat** that are comparable to Claude Sonnet.

### Top Recommendations (Most Comparable to Claude Sonnet)

#### 1. **Qwen3.6-27B** (Visual LLM) ⭐ NEW

- **Parameters:** 35B (fp8 quantization)
- **Context:** 262K tokens
- **Capabilities:** Function calling, Multimodal, Reasoning
- **Pricing:** €0.4/Mtoken input, €2.7/Mtoken output
- **Model ID:** `ovhcloud/qwen3.6-27b`
- **Responsiveness:** ⚡⚡⚡⚡ Excellent (27B model with fp8 quantization provides fast inference)
- **Best For:** General interactive chat, coding assistance, multimodal tasks with good speed/quality balance

#### 2. **Qwen3.5-397B-A17B** (Visual LLM) ⭐ NEW - MOST POWERFUL

- **Parameters:** 397B (fp8 quantization)
- **Context:** 262K tokens
- **Capabilities:** Function calling, Multimodal, Reasoning
- **Pricing:** €0.6/Mtoken input, €3.6/Mtoken output
- **Model ID:** `ovhcloud/qwen3.5-397b-a17b`
- **Responsiveness:** ⚡⚡⚡ Good (larger model, slightly slower but still production-ready)
- **Best For:** Complex reasoning tasks, multi-file refactoring, architectural decisions

#### 3. **gpt-oss-120b** (Reasoning LLM) 💰 BEST VALUE

- **Parameters:** 117B (fp4 quantization)
- **Context:** 131K tokens
- **Capabilities:** Function calling, Reasoning
- **Pricing:** €0.08/Mtoken input, €0.4/Mtoken output
- **Model ID:** `ovhcloud/gpt-oss-120b`
- **Responsiveness:** ⚡⚡⚡⚡ Excellent (fp4 quantization speeds up inference significantly)
- **Best For:** Cost-effective coding assistance with strong reasoning capabilities

### Good Alternatives

#### 4. **Qwen3-32B** (Reasoning LLM)

- **Parameters:** 32.8B (fp8 quantization)
- **Context:** 32K tokens
- **Capabilities:** Function calling, Reasoning
- **Pricing:** €0.08/Mtoken input, €0.23/Mtoken output
- **Model ID:** `ovhcloud/qwen3-32b`
- **Responsiveness:** ⚡⚡⚡⚡⚡ Very Fast (smaller model, fp8 quantization)
- **Best For:** Quick iterations, fast responses for simple to medium complexity tasks

#### 5. **Meta-Llama-3.3-70B-Instruct** (LLM)

- **Parameters:** 70B (fp8 quantization)
- **Context:** 131K tokens
- **Capabilities:** Function calling
- **Pricing:** €0.67/Mtoken input, €0.67/Mtoken output
- **Model ID:** `ovhcloud/meta-llama-3_3-70b-instruct`
- **Responsiveness:** ⚡⚡⚡⚡ Excellent (well-optimized, balanced performance)
- **Best For:** General-purpose coding, documentation, established Llama ecosystem familiarity

#### 6. **Mistral-Small-3.2-24B-Instruct-2506** (Visual LLM)

- **Parameters:** 24B (bf16 quantization)
- **Context:** 128K tokens
- **Capabilities:** Function calling, Multimodal
- **Pricing:** €0.09/Mtoken input, €0.28/Mtoken output
- **Model ID:** `ovhcloud/mistral-small-3.2-24b-instruct-2506`
- **Responsiveness:** ⚡⚡⚡⚡ Excellent (smaller size, good optimization)
- **Best For:** European data sovereignty preference, Mistral ecosystem users

### Budget-Friendly Options

#### 7. **Qwen3.5-9B** ⭐ NEW - FASTEST

- **Parameters:** 9.7B (bf16 quantization)
- **Context:** 262K tokens
- **Capabilities:** Function calling, Multimodal, Reasoning
- **Pricing:** €0.1/Mtoken input, €0.15/Mtoken output
- **Model ID:** `ovhcloud/qwen3.5-9b`
- **Responsiveness:** ⚡⚡⚡⚡⚡ Very Fast (small model size = near-instant responses)
- **Best For:** Rapid prototyping, simple edits, learning, budget-conscious development

#### 8. **gpt-oss-20b** (Reasoning LLM) 💰 CHEAPEST

- **Parameters:** 21B (fp4 quantization)
- **Context:** 131K tokens
- **Capabilities:** Function calling, Reasoning
- **Pricing:** €0.04/Mtoken input, €0.15/Mtoken output
- **Model ID:** `ovhcloud/gpt-oss-20b`
- **Responsiveness:** ⚡⚡⚡⚡⚡ Very Fast (fp4 quantization, small model)
- **Best For:** High-volume tasks, experimentation, CI/CD integration

#### 9. **Qwen3-Coder-30B-A3B-Instruct** (Code LLM) 🔧 CODE SPECIALIST

- **Parameters:** 30B (fp8 quantization)
- **Context:** 256K tokens
- **Capabilities:** Function calling, Code Assistant
- **Pricing:** €0.06/Mtoken input, €0.22/Mtoken output
- **Model ID:** `ovhcloud/qwen3-coder-30b-a3b-instruct`
- **Responsiveness:** ⚡⚡⚡⚡ Excellent (optimized specifically for code generation)
- **Best For:** Pure coding tasks, code completion, refactoring, bug fixes

### Responsiveness Comparison Table

| Model | Size | Quantization | Speed Rating | Latency (Est.)* | Use Case |
|-||--|--|--|-|
| **Qwen3.5-9B** | 9.7B | bf16 | ⚡⚡⚡⚡⚡ | ~100-200ms | Fastest responses |
| **gpt-oss-20b** | 21B | fp4 | ⚡⚡⚡⚡⚡ | ~150-250ms | Fast & cheap |
| **Qwen3.6-27B** | 35B | fp8 | ⚡⚡⚡⚡ | ~200-400ms | Balanced choice |
| **Qwen3-Coder-30B** | 30B | fp8 | ⚡⚡⚡⚡ | ~200-400ms | Code-focused |
| **Qwen3-32B** | 32.8B | fp8 | ⚡⚡⚡⚡ | ~250-450ms | Quick reasoning |
| **Meta-Llama-3.3-70B** | 70B | fp8 | ⚡⚡⚡⚡ | ~300-600ms | Reliable workhorse |
| **gpt-oss-120b** | 117B | fp4 | ⚡⚡⚡⚡ | ~400-700ms | Strong reasoning |
| **Qwen3.5-397B** | 397B | fp8 | ⚡⚡⚡ | ~800-1500ms | Most powerful |

*Estimated latency for typical prompt (500 input tokens, 100 output tokens) on OVH EU infrastructure. Actual latency depends on server load, network conditions, and prompt complexity.

### Key Capabilities Comparison

| Feature | Claude Sonnet 4.5 | OVH Top Models | Notes |
|||-|-|
| **Function Calling** | ✅ Yes | ✅ Yes (all recommended) | Essential for OpenCode tool use |
| **Extended Thinking** | ✅ Yes | ✅ Yes (Qwen/gpt-oss series) | Advanced reasoning capabilities |
| **Multimodal (Vision)** | ✅ Yes | ✅ Yes (Qwen 3.5/3.6, Mistral-Small) | Image understanding |
| **Context Length** | 200K | 🏆 Up to 262K (Qwen3.5/3.6) | OVH wins on context |
| **Parameters** | ~200B+ | 🏆 Up to 397B (Qwen3.5-397B) | Comparable scale |
| **Responsiveness** | ⚡⚡⚡⚡⚡ | ⚡⚡⚡⚡ to ⚡⚡⚡⚡⚡ | Varies by model size |
| **Data Sovereignty** | ❌ US-based | ✅ European (OVH) | GDPR compliance |
| **Pricing** | $$$ Premium | $ to $$ Competitive | Significant cost savings |

### Quantization Impact on Responsiveness

Understanding quantization helps predict model responsiveness:

- **fp4 (4-bit):** 🚀 Fastest inference, slight quality trade-off
  - Examples: gpt-oss-120b, gpt-oss-20b
  - ~4x faster than fp16, ~2x faster than fp8

- **fp8 (8-bit):** ⚡ Fast inference, minimal quality loss
  - Examples: Qwen3.6-27B, Qwen3.5-397B, Meta-Llama-3.3-70B
  - ~2x faster than fp16, excellent quality/speed balance

- **bf16 (16-bit):** 💎 Full quality, slower inference
  - Examples: Qwen3.5-9B, Mistral-Small-3.2-24B
  - Best quality but needs smaller models for good responsiveness

## Recommendations by Use Case

### **Best Overall for Interactive Chat** 🏆

**Qwen3.6-27B** - Perfect balance of speed, quality, and features

- Fast enough for interactive use (⚡⚡⚡⚡)
- Strong reasoning and multimodal capabilities
- Large context window (262K)
- Reasonable pricing

### **Best for Speed & Cost** 💰

**gpt-oss-120b** - Excellent value proposition

- Very responsive (fp4 quantization)
- Strong reasoning capabilities
- Cheapest powerful model (€0.08/€0.4 per Mtoken)

### **Best for Quick Iterations** ⚡

**Qwen3.5-9B** - Near-instant responses

- Fastest model in catalog
- Still capable of complex tasks
- Huge context window (262K)
- Ultra-cheap (€0.1/€0.15)

### **Best for Code-Specific Tasks** 🔧

**Qwen3-Coder-30B-A3B-Instruct** - Purpose-built for coding

- Specialized code understanding
- Fast inference (30B fp8)
- Excellent code completion
- Good pricing (€0.06/€0.22)

### **Best for Complex Reasoning** 🧠

**Qwen3.5-397B-A17B** - Most powerful option

- Handles complex architectural decisions
- Multimodal + reasoning + function calling
- Accept slower responses for maximum capability
- Use for critical decisions, not routine edits
