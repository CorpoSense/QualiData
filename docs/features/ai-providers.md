# AI Providers

MasterDataCleaner supports multiple AI providers through LangChain, giving you flexibility to choose the best model for your needs.

## Supported Providers

| Provider | Default Model | Environment Variable | Supports Custom URL |
|----------|---------------|---------------------|---------------------|
| **OpenAI** | gpt-4o-mini | `OPENAI_API_KEY` | Yes |
| **Anthropic** | claude-sonnet-4-20250514 | `ANTHROPIC_API_KEY` | No |
| **Google** | gemini-2.0-flash | `GOOGLE_API_KEY` | No |
| **Ollama** | llama3.2 | (none - local) | Yes |
| **Groq** | llama-3.3-70b-versatile | `GROQ_API_KEY` | Yes |
| **DeepSeek** | deepseek-chat | `DEEPSEEK_API_KEY` | Yes |
| **OpenRouter** | openai/gpt-4o-mini | `OPENROUTER_API_KEY` | No |
| **Hugging Face** | meta-llama/Llama-3.1-8B-Instruct | `HUGGINGFACE_API_KEY` | Yes |

## Configuration

### Global Configuration (.env)

Add API keys to `backend/.env`:

```env
# AI Provider API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
GROQ_API_KEY=...
DEEPSEEK_API_KEY=...
OPENROUTER_API_KEY=...
HUGGINGFACE_API_KEY=...
```

### Per-Agent Configuration

Configure different providers for different agents:

1. Go to **Agents** → **Create Agent**
2. Select provider from dropdown
3. Enter API key (overrides global config)
4. Choose model (or use default)
5. Configure temperature and prompts
6. Save agent

## Provider Comparison

### OpenAI

**Best for:** General purpose, reliable performance

| Feature | Details |
|---------|---------|
| **Models** | gpt-4o-mini, gpt-4o, gpt-4-turbo |
| **Speed** | Fast |
| **Quality** | High |
| **Cost** | $$ |
| **Rate Limit** | 500 req/min, 90K tokens/min |

**Use cases:**
- General data cleaning
- Text normalization
- Format standardization

### Anthropic

**Best for:** Complex reasoning, careful analysis

| Feature | Details |
|---------|---------|
| **Models** | claude-sonnet-4, claude-opus |
| **Speed** | Medium |
| **Quality** | Very High |
| **Cost** | $$$ |
| **Rate Limit** | 60 req/min, 40K tokens/min |

**Use cases:**
- Complex data transformations
- Contextual understanding
- Sensitive data handling

### Google

**Best for:** Multi-modal tasks, cost efficiency

| Feature | Details |
|---------|---------|
| **Models** | gemini-2.0-flash, gemini-pro |
| **Speed** | Fast |
| **Quality** | High |
| **Cost** | $ |
| **Rate Limit** | 300 req/min, 60K tokens/min |

**Use cases:**
- Large batch processing
- Multi-language data
- Image + text data

### Ollama

**Best for:** Local processing, privacy

| Feature | Details |
|---------|---------|
| **Models** | llama3.2, mistral, custom |
| **Speed** | Depends on hardware |
| **Quality** | Good |
| **Cost** | Free (self-hosted) |
| **Rate Limit** | None (local) |

**Use cases:**
- Sensitive data (no cloud)
- Development and testing
- High-volume processing

**Setup:**
```bash
# Install Ollama
brew install ollama  # macOS
# or download from https://ollama.ai

# Pull model
ollama pull llama3.2

# Start server
ollama serve
```

### Groq

**Best for:** Speed, large models

| Feature | Details |
|---------|---------|
| **Models** | llama-3.3-70b, mixtral-8x7b |
| **Speed** | Very Fast |
| **Quality** | High |
| **Cost** | $ |
| **Rate Limit** | 30 req/min, 18K tokens/min |

**Use cases:**
- Real-time cleaning
- Large model inference
- Cost-effective processing

### DeepSeek

**Best for:** Cost-effective, good quality

| Feature | Details |
|---------|---------|
| **Models** | deepseek-chat, deepseek-coder |
| **Speed** | Fast |
| **Quality** | Good |
| **Cost** | $ |
| **Rate Limit** | 60 req/min, 30K tokens/min |

**Use cases:**
- Budget-conscious projects
- Code generation for cleaning
- General data tasks

### OpenRouter

**Best for:** Access to multiple models

| Feature | Details |
|---------|---------|
| **Models** | 100+ models from various providers |
| **Speed** | Varies by model |
| **Quality** | Varies by model |
| **Cost** | Varies by model |
| **Rate Limit** | Varies by underlying provider |

**Use cases:**
- Model comparison
- Fallback options
- Specialized tasks

## Custom Base URL

Some providers support custom endpoints for self-hosted models:

```env
# Example: Self-hosted OpenAI-compatible API
OPENAI_BASE_URL=http://localhost:1234/v1
```

Configure in agent settings:
1. Create/Edit agent
2. Enable "Custom Base URL"
3. Enter endpoint URL
4. Save and test

## Rate Limiting

MasterDataCleaner automatically handles rate limits:

### Built-in Protection
- **Automatic retries** with exponential backoff
- **Request queuing** during high load
- **Progress indicators** during delays
- **Quota warnings** before limits reached

### Best Practices
1. **Batch processing** - Process data in larger batches to reduce API calls
2. **Caching** - Reuse agent configurations
3. **Off-peak processing** - Run large jobs during low-traffic periods
4. **Monitor usage** - Check provider dashboard for quota status

## Choosing a Provider

### Decision Guide

**For Development:**
- **Ollama** - Free, unlimited local testing
- **OpenAI** - Reliable, well-documented

**For Production:**
- **OpenAI** - Best overall reliability
- **Anthropic** - Highest quality for complex tasks
- **Google** - Best cost/performance ratio

**For Budget:**
- **DeepSeek** - Good quality at low cost
- **Groq** - Fast and affordable
- **Ollama** - Free (self-hosted)

**For Privacy:**
- **Ollama** - Completely local
- **Self-hosted** - Custom endpoints

## Troubleshooting

### API Key Errors

**Issue:** "Invalid API key"
- Verify key is correct (no extra spaces)
- Check key has necessary permissions
- Ensure account has credits/quota

### Rate Limit Errors

**Issue:** "Rate limit exceeded"
- Wait and retry (automatic with backoff)
- Reduce batch size
- Upgrade provider tier
- Switch to different provider

### Model Not Found

**Issue:** "Model not available"
- Verify model name is correct
- Check model is available in your region
- Ensure account has access to model

### Connection Errors

**Issue:** "Connection failed"
- Check internet connection
- Verify provider status page
- For local providers, ensure service is running

## Example Configurations

### Basic OpenAI Setup

```env
OPENAI_API_KEY=sk-...
```

Agent config:
- Provider: OpenAI
- Model: gpt-4o-mini
- Temperature: 0.3

### Multi-Provider Setup

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

Create multiple agents:
- **Quick Clean** - OpenAI (fast, cheap)
- **Complex Transform** - Anthropic (high quality)
- **Batch Process** - Google (cost effective)

### Local-Only Setup

```env
# No API keys needed
```

Agent config:
- Provider: Ollama
- Model: llama3.2
- Base URL: http://localhost:11434

---

*Part of the [MasterDataCleaner Documentation](../README.md)*
