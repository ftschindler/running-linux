# OVHcloud AI Endpoints - Model Selection Guide

**Last Updated:** 2026-06-03
**Context:** OpenCode with OVHcloud AI Endpoints integration

---

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

---

## Top Recommendations (Most Comparable to Claude Sonnet)

### 1. **Qwen3.6-27B** (Visual LLM) ⭐ NEW

- **Parameters:** 35B (fp8 quantization)
- **Context:** 262K tokens
- **Capabilities:** Function calling, Multimodal, Reasoning
- **Pricing:** €0.4/Mtoken input, €2.7/Mtoken output
- **Model ID:** `ovhcloud/qwen3.6-27b`
- **Responsiveness:** ⚡⚡⚡⚡ Excellent (27B model with fp8 quantization provides fast inference)
- **Best For:** General interactive chat, coding assistance, multimodal tasks with good speed/quality balance

### 2. **Qwen3.5-397B-A17B** (Visual LLM) ⭐ NEW - MOST POWERFUL

- **Parameters:** 397B (fp8 quantization)
- **Context:** 262K tokens
- **Capabilities:** Function calling, Multimodal, Reasoning
- **Pricing:** €0.6/Mtoken input, €3.6/Mtoken output
- **Model ID:** `ovhcloud/qwen3.5-397b-a17b`
- **Responsiveness:** ⚡⚡⚡ Good (larger model, slightly slower but still production-ready)
- **Best For:** Complex reasoning tasks, multi-file refactoring, architectural decisions

### 3. **gpt-oss-120b** (Reasoning LLM) 💰 BEST VALUE

- **Parameters:** 117B (fp4 quantization)
- **Context:** 131K tokens
- **Capabilities:** Function calling, Reasoning
- **Pricing:** €0.08/Mtoken input, €0.4/Mtoken output
- **Model ID:** `ovhcloud/gpt-oss-120b`
- **Responsiveness:** ⚡⚡⚡⚡ Excellent (fp4 quantization speeds up inference significantly)
- **Best For:** Cost-effective coding assistance with strong reasoning capabilities

---

## Good Alternatives

### 4. **Qwen3-32B** (Reasoning LLM)

- **Parameters:** 32.8B (fp8 quantization)
- **Context:** 32K tokens
- **Capabilities:** Function calling, Reasoning
- **Pricing:** €0.08/Mtoken input, €0.23/Mtoken output
- **Model ID:** `ovhcloud/qwen3-32b`
- **Responsiveness:** ⚡⚡⚡⚡⚡ Very Fast (smaller model, fp8 quantization)
- **Best For:** Quick iterations, fast responses for simple to medium complexity tasks

### 5. **Meta-Llama-3.3-70B-Instruct** (LLM)

- **Parameters:** 70B (fp8 quantization)
- **Context:** 131K tokens
- **Capabilities:** Function calling
- **Pricing:** €0.67/Mtoken input, €0.67/Mtoken output
- **Model ID:** `ovhcloud/meta-llama-3_3-70b-instruct`
- **Responsiveness:** ⚡⚡⚡⚡ Excellent (well-optimized, balanced performance)
- **Best For:** General-purpose coding, documentation, established Llama ecosystem familiarity

### 6. **Mistral-Small-3.2-24B-Instruct-2506** (Visual LLM)

- **Parameters:** 24B (bf16 quantization)
- **Context:** 128K tokens
- **Capabilities:** Function calling, Multimodal
- **Pricing:** €0.09/Mtoken input, €0.28/Mtoken output
- **Model ID:** `ovhcloud/mistral-small-3.2-24b-instruct-2506`
- **Responsiveness:** ⚡⚡⚡⚡ Excellent (smaller size, good optimization)
- **Best For:** European data sovereignty preference, Mistral ecosystem users

---

## Budget-Friendly Options

### 7. **Qwen3.5-9B** ⭐ NEW - FASTEST

- **Parameters:** 9.7B (bf16 quantization)
- **Context:** 262K tokens
- **Capabilities:** Function calling, Multimodal, Reasoning
- **Pricing:** €0.1/Mtoken input, €0.15/Mtoken output
- **Model ID:** `ovhcloud/qwen3.5-9b`
- **Responsiveness:** ⚡⚡⚡⚡⚡ Very Fast (small model size = near-instant responses)
- **Best For:** Rapid prototyping, simple edits, learning, budget-conscious development

### 8. **gpt-oss-20b** (Reasoning LLM) 💰 CHEAPEST

- **Parameters:** 21B (fp4 quantization)
- **Context:** 131K tokens
- **Capabilities:** Function calling, Reasoning
- **Pricing:** €0.04/Mtoken input, €0.15/Mtoken output
- **Model ID:** `ovhcloud/gpt-oss-20b`
- **Responsiveness:** ⚡⚡⚡⚡⚡ Very Fast (fp4 quantization, small model)
- **Best For:** High-volume tasks, experimentation, CI/CD integration

### 9. **Qwen3-Coder-30B-A3B-Instruct** (Code LLM) 🔧 CODE SPECIALIST

- **Parameters:** 30B (fp8 quantization)
- **Context:** 256K tokens
- **Capabilities:** Function calling, Code Assistant
- **Pricing:** €0.06/Mtoken input, €0.22/Mtoken output
- **Model ID:** `ovhcloud/qwen3-coder-30b-a3b-instruct`
- **Responsiveness:** ⚡⚡⚡⚡ Excellent (optimized specifically for code generation)
- **Best For:** Pure coding tasks, code completion, refactoring, bug fixes

---

## Responsiveness Comparison Table

| Model | Size | Quantization | Speed Rating | Latency (Est.)* | Use Case |
|-------|------|--------------|--------------|-----------------|----------|
| **Qwen3.5-9B** | 9.7B | bf16 | ⚡⚡⚡⚡⚡ | ~100-200ms | Fastest responses |
| **gpt-oss-20b** | 21B | fp4 | ⚡⚡⚡⚡⚡ | ~150-250ms | Fast & cheap |
| **Qwen3.6-27B** | 35B | fp8 | ⚡⚡⚡⚡ | ~200-400ms | Balanced choice |
| **Qwen3-Coder-30B** | 30B | fp8 | ⚡⚡⚡⚡ | ~200-400ms | Code-focused |
| **Qwen3-32B** | 32.8B | fp8 | ⚡⚡⚡⚡ | ~250-450ms | Quick reasoning |
| **Meta-Llama-3.3-70B** | 70B | fp8 | ⚡⚡⚡⚡ | ~300-600ms | Reliable workhorse |
| **gpt-oss-120b** | 117B | fp4 | ⚡⚡⚡⚡ | ~400-700ms | Strong reasoning |
| **Qwen3.5-397B** | 397B | fp8 | ⚡⚡⚡ | ~800-1500ms | Most powerful |

*Estimated latency for typical prompt (500 input tokens, 100 output tokens) on OVH EU infrastructure. Actual latency depends on server load, network conditions, and prompt complexity.

---

## Key Capabilities Comparison

| Feature | Claude Sonnet 4.5 | OVH Top Models | Notes |
|---------|------------------|----------------|-------|
| **Function Calling** | ✅ Yes | ✅ Yes (all recommended) | Essential for OpenCode tool use |
| **Extended Thinking** | ✅ Yes | ✅ Yes (Qwen/gpt-oss series) | Advanced reasoning capabilities |
| **Multimodal (Vision)** | ✅ Yes | ✅ Yes (Qwen 3.5/3.6, Mistral-Small) | Image understanding |
| **Context Length** | 200K | 🏆 Up to 262K (Qwen3.5/3.6) | OVH wins on context |
| **Parameters** | ~200B+ | 🏆 Up to 397B (Qwen3.5-397B) | Comparable scale |
| **Responsiveness** | ⚡⚡⚡⚡⚡ | ⚡⚡⚡⚡ to ⚡⚡⚡⚡⚡ | Varies by model size |
| **Data Sovereignty** | ❌ US-based | ✅ European (OVH) | GDPR compliance |
| **Pricing** | $$$ Premium | $ to $$ Competitive | Significant cost savings |

---

## Quantization Impact on Responsiveness

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

---

## My Recommendations by Use Case

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

---

## Getting Started

### Step 1: Connect OpenCode to OVH

```bash
# Run the connect command in OpenCode
/connect

# Search for "OVHcloud AI Endpoints" and enter your API key
```

### Step 2: Select a Model

```bash
# List available models
/models

# Select your preferred model from the list
# Recommended starting point: ovhcloud/qwen3.6-27b
```

### Step 3: Test Your Setup

```bash
# Simple test
Ask OpenCode: "What is 2+2?"

# Code generation test
Ask OpenCode: "Create a hello world function in Python"

# Tool use test (function calling)
Ask OpenCode: "Read the README.md file and summarize it"
```

---

## Configuration Examples

### Set Default Model in OpenCode Config

Edit `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "ovhcloud/qwen3.6-27b",
  "provider": {
    "ovhcloud": {
      "models": {
        "qwen3.6-27b": {
          "name": "Qwen 3.6 27B (Default)"
        },
        "gpt-oss-120b": {
          "name": "GPT-OSS 120B (Fast & Cheap)"
        },
        "qwen3.5-9b": {
          "name": "Qwen 3.5 9B (Ultra Fast)"
        }
      }
    }
  }
}
```

### Project-Specific Model Selection

Create `.opencode/config.json` in your project root:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "ovhcloud/qwen3-coder-30b-a3b-instruct",
  "comment": "Use code-specialized model for this project"
}
```

---

## Switching Models During Session

Use the `/models` command in OpenCode to switch models on-the-fly:

```bash
# Quick switch during chat
/models

# Then select from the interactive picker
# Perfect for trying different models based on task complexity
```

**Strategy:**

- Start with **Qwen3.5-9B** for quick edits
- Switch to **Qwen3.6-27B** for standard coding
- Use **Qwen3.5-397B** for complex architectural decisions
- Try **Qwen3-Coder-30B** for pure code generation tasks

---

## Troubleshooting Responsiveness

### If responses feel slow

1. **Check your network latency to EU:**

   ```bash
   ping endpoints.ai.ovhcloud.net
   ```

   OVH endpoints are in European data centers. Non-EU users may see 200-500ms additional latency.

2. **Switch to a faster model:**
   - Try: `qwen3.5-9b` or `gpt-oss-20b` for near-instant responses
   - Avoid: `qwen3.5-397b-a17b` for interactive editing

3. **Check model load:**
   Some models may be under heavy load during peak hours. Try alternative models or retry later.

4. **Verify fp4/fp8 quantization:**
   Models with fp4 (gpt-oss series) or fp8 (Qwen series) quantization are significantly faster than bf16/fp16 models.

---

## References

- [OVHcloud AI Endpoints Catalog](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/catalog/)
- [OVHcloud AI Endpoints Documentation](https://docs.ovhcloud.com/ai-endpoints/)
- [OpenCode Models Documentation](https://opencode.ai/docs/models/)
- [OpenCode Providers Guide](https://opencode.ai/docs/providers/)
- [Models.dev - Model Registry](https://models.dev/)

---

## Oh-My-OpenAgent Category Recommendations

When using [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent) with OVHcloud, you need to configure models for **four agent categories**. Each category serves a specific purpose in the agent orchestration system.

### Understanding the Categories

oh-my-openagent uses a **category-based model selection system**. Instead of hardcoding models for specific agents, you define which model to use for each category of work. Agents then pick the appropriate category for their task.

| Category | Purpose | Priority | Recommended Traits |
|----------|---------|----------|-------------------|
| **visual-engineering** | Frontend, UI/UX, design tasks | Balance | Multimodal support, good at CSS/HTML/React |
| **deep** | Autonomous research + execution, complex architectural work | Quality over speed | Strong reasoning, large context, function calling |
| **quick** | Single-file changes, typos, simple refactors | Speed | Fast inference, low cost, basic function calling |
| **ultrabrain** | Hard logic, complex algorithms, critical decisions | Maximum intelligence | Best reasoning model available, high accuracy |

### OVH Model Recommendations by Category

Here's the recommended OVH model configuration for each oh-my-openagent category:

| Category | Primary Recommendation | Alternative | Budget Option | Rationale |
|----------|----------------------|-------------|---------------|-----------|
| **visual-engineering** | `ovhcloud/qwen3.6-27b` | `ovhcloud/qwen2.5-vl-72b-instruct` | `ovhcloud/mistral-small-3.2-24b-instruct-2506` | Multimodal support for screenshot analysis, fast enough for interactive UI work, good balance of speed/quality |
| **deep** | `ovhcloud/qwen3.5-397b-a17b` | `ovhcloud/gpt-oss-120b` | `ovhcloud/qwen3-32b` | Maximum reasoning capability for autonomous exploration, large context window (262K), strong function calling |
| **quick** | `ovhcloud/qwen3.5-9b` | `ovhcloud/gpt-oss-20b` | `ovhcloud/mistral-7b-instruct-v0.3` | Near-instant responses (⚡⚡⚡⚡⚡), ultra-cheap, sufficient for simple tasks, huge context (262K) despite small size |
| **ultrabrain** | `ovhcloud/qwen3.5-397b-a17b` | `ovhcloud/gpt-oss-120b` | `ovhcloud/meta-llama-3_3-70b-instruct` | Most powerful reasoning model in OVH catalog, 397B parameters, fp8 quantization for production speed |

### Example Configuration

Add this to your `~/.config/opencode/oh-my-openagent.jsonc`:

```jsonc
{
  "$schema": "https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/dev/assets/oh-my-opencode.schema.json",
  "categories": {
    "visual-engineering": {
      "model": "ovhcloud/qwen3.6-27b",
      "fallback_models": [
        "ovhcloud/qwen2.5-vl-72b-instruct",
        "ovhcloud/mistral-small-3.2-24b-instruct-2506"
      ]
    },
    "deep": {
      "model": "ovhcloud/qwen3.5-397b-a17b",
      "fallback_models": [
        "ovhcloud/gpt-oss-120b",
        "ovhcloud/qwen3-32b"
      ]
    },
    "quick": {
      "model": "ovhcloud/qwen3.5-9b",
      "fallback_models": [
        "ovhcloud/gpt-oss-20b",
        "ovhcloud/mistral-7b-instruct-v0.3"
      ],
      "temperature": 0.3  // Lower temperature for consistency in simple tasks
    },
    "ultrabrain": {
      "model": "ovhcloud/qwen3.5-397b-a17b",
      "fallback_models": [
        "ovhcloud/gpt-oss-120b",
        "ovhcloud/meta-llama-3_3-70b-instruct"
      ],
      "temperature": 0.2  // Very low temperature for maximum precision
    }
  }
}
```

### Budget-Optimized Configuration

If you want to minimize costs while maintaining good performance:

```jsonc
{
  "categories": {
    "visual-engineering": {
      "model": "ovhcloud/mistral-small-3.2-24b-instruct-2506"
    },
    "deep": {
      "model": "ovhcloud/gpt-oss-120b"  // Best value: €0.08/€0.4 per Mtoken
    },
    "quick": {
      "model": "ovhcloud/qwen3.5-9b"    // Cheapest: €0.1/€0.15 per Mtoken
    },
    "ultrabrain": {
      "model": "ovhcloud/gpt-oss-120b"
    }
  }
}
```

**Estimated monthly cost for budget config:** ~€15-30 for moderate usage (assuming 50M tokens input, 10M tokens output per month)

### Performance-Optimized Configuration

Maximum quality, accepting slower responses and higher costs:

```jsonc
{
  "categories": {
    "visual-engineering": {
      "model": "ovhcloud/qwen2.5-vl-72b-instruct"  // Most powerful multimodal
    },
    "deep": {
      "model": "ovhcloud/qwen3.5-397b-a17b"        // Most powerful overall
    },
    "quick": {
      "model": "ovhcloud/qwen3-32b"                // Fast but still capable
    },
    "ultrabrain": {
      "model": "ovhcloud/qwen3.5-397b-a17b"        // Maximum reasoning
    }
  }
}
```

### Balanced Configuration (Recommended)

Best balance of cost, speed, and quality for most users:

```jsonc
{
  "categories": {
    "visual-engineering": {
      "model": "ovhcloud/qwen3.6-27b"
    },
    "deep": {
      "model": "ovhcloud/gpt-oss-120b"
    },
    "quick": {
      "model": "ovhcloud/qwen3.5-9b"
    },
    "ultrabrain": {
      "model": "ovhcloud/qwen3.5-397b-a17b"
    }
  }
}
```

**Estimated monthly cost for balanced config:** ~€25-50 for moderate usage

### Category Usage Patterns

Understanding when each category is invoked helps you optimize your configuration:

| Category | Triggered By | Frequency | Cost Impact |
|----------|-------------|-----------|-------------|
| **visual-engineering** | UI/UX tasks, frontend work, design implementation | Medium | Medium |
| **deep** | `Hephaestus` agent (autonomous worker), complex multi-file changes | Low-Medium | High (slow, powerful) |
| **quick** | Single-file edits, simple refactors, typo fixes | Very High | Low (fast, cheap) |
| **ultrabrain** | Critical architecture decisions, complex algorithms, verification | Low | High (expensive) |

**Cost optimization tip:** Since `quick` is invoked most frequently, using the cheapest fast model here (Qwen3.5-9B at €0.1/€0.15) significantly reduces your overall bill while maintaining responsiveness.

### Model Comparison for oh-my-openagent Categories

| Model | visual-engineering | deep | quick | ultrabrain | Notes |
|-------|:-----------------:|:----:|:-----:|:----------:|-------|
| **Qwen3.6-27B** | ✅ Primary | ⚠️ Too slow | ❌ Overkill | ❌ Not powerful enough | Perfect for UI work with multimodal |
| **Qwen3.5-397B** | ⚠️ Too slow | ✅ Primary | ❌ Overkill | ✅ Primary | Most powerful option |
| **gpt-oss-120b** | ❌ No multimodal | ✅ Best value | ❌ Overkill | ✅ Good fallback | Great value for reasoning |
| **Qwen3.5-9B** | ⚠️ Weak for complex UI | ❌ Too weak | ✅ Primary | ❌ Too weak | Fastest, cheapest, huge context |
| **Qwen3-32B** | ⚠️ No multimodal | ✅ Good fallback | ✅ Alternative | ⚠️ Acceptable | Balanced middle ground |
| **Meta-Llama-3.3-70B** | ❌ No multimodal | ✅ Alternative | ❌ Overkill | ✅ Good fallback | Reliable general-purpose |
| **Mistral-Small-3.2-24B** | ✅ Good fallback | ❌ Too small | ✅ Alternative | ❌ Too small | Cheap multimodal option |
| **Qwen2.5-VL-72B** | ✅ Best multimodal | ⚠️ Expensive | ❌ Overkill | ❌ Not general-purpose | Specialized for vision |
| **gpt-oss-20b** | ❌ No multimodal | ❌ Too weak | ✅ Budget option | ❌ Too weak | Ultra-cheap for simple tasks |

✅ = Excellent fit | ⚠️ = Workable with caveats | ❌ = Not recommended

### Verification After Configuration

After setting up your categories, verify the configuration:

```bash
# Check if oh-my-openagent loaded your config
bunx oh-my-openagent doctor

# Test each category with OpenCode
# Visual test:
echo "Create a simple React button component" | opencode

# Deep test:
echo "Analyze the entire codebase architecture and suggest improvements" | opencode

# Quick test:
echo "Fix the typo in README.md line 42" | opencode

# Ultrabrain test:
echo "Design an optimal algorithm for [complex problem]" | opencode
```

### Troubleshooting Category Selection

If agents aren't using the models you configured:

1. **Check config location:** `~/.config/opencode/oh-my-openagent.jsonc` (or legacy `oh-my-opencode.jsonc`)
2. **Verify JSON syntax:** Use a JSON validator or let OpenCode's schema validation catch errors
3. **Check model availability:** Run `/models` in OpenCode to ensure OVH models are listed
4. **Review agent logs:** Check `~/.local/share/opencode/logs/` for category resolution errors
5. **Restart OpenCode:** Config changes require a restart

### Advanced: Custom Categories

You can define your own categories for specialized workflows:

```jsonc
{
  "categories": {
    // Standard categories
    "visual-engineering": { "model": "ovhcloud/qwen3.6-27b" },
    "deep": { "model": "ovhcloud/qwen3.5-397b-a17b" },
    "quick": { "model": "ovhcloud/qwen3.5-9b" },
    "ultrabrain": { "model": "ovhcloud/qwen3.5-397b-a17b" },

    // Custom categories
    "security-audit": {
      "model": "ovhcloud/gpt-oss-120b",
      "temperature": 0.1  // Very low for security work
    },
    "documentation": {
      "model": "ovhcloud/qwen3-32b",
      "temperature": 0.7  // Higher for creative writing
    }
  }
}
```

Then specify the category when delegating:

```javascript
// In your agent code or skills
delegate({
  category: "security-audit",
  task: "Audit this authentication flow for vulnerabilities"
});
```

---

## Changelog

- **2026-06-03:** Initial model comparison based on OVH catalog, added responsiveness ratings and quantization impact analysis, added oh-my-openagent category recommendations
