# AI Architect Agent

A **functionalist, cost-effective** architecture definition system for deploying multi-channel chatbots to WhatsApp, Facebook Messenger, Instagram, and Mercado Libre.

**Target Outcome**: Deploy a production chatbot for **$25-75/month** vs Botmaker's $190/month—saving **$1,400+ annually**.

## Quick Start

```bash
# Generate default architecture for Panelin BMC Uruguay
python -m ai_architect_agent

# Interactive configuration
python -m ai_architect_agent --interactive

# Compare all architecture tiers
python -m ai_architect_agent --compare

# Custom configuration
python -m ai_architect_agent --company "MyCompany" --budget 50 --conversations 2000
```

## Architecture Tiers

| Tier | Monthly Cost | Channels | Use Case |
|------|-------------|----------|----------|
| **Minimal** | $25-35 | WhatsApp only | Limited budget, MVP |
| **Standard** | $40-55 | WhatsApp + Messenger + Instagram | Recommended starting point |
| **Complete** | $60-75 | All channels + Mercado Libre | Full e-commerce integration |
| **Enterprise** | $100+ | All + redundancy | High volume (10k+ conversations) |

## Core Design Principles

### 1. Functionalist Design
Every component serves a clear purpose. No unnecessary features or complexity.

### 2. Cost Efficiency
- **Free hosting first**: Oracle Cloud Always Free (4 CPU, 24GB RAM)
- **Free channels**: Messenger, Instagram, Mercado Libre cost $0
- **Smart WhatsApp pricing**: Service conversations (customer-initiated) are FREE
- **LLM optimization**: GPT-4o-mini at $0.90/month for 2,000 conversations

### 3. Production Reliability
- No sleeping services (avoid Render free tier)
- Proper webhook handling
- Graceful error handling

### 4. Incremental Deployment
Start with WhatsApp (70% of traffic), add channels as needed.

## Usage Examples

### Python API

```python
from ai_architect_agent import AIArchitectAgent, ArchitectureConfig

# Quick generation
agent = AIArchitectAgent()
architecture = agent.quick_generate(
    company="My E-Commerce",
    conversations=2000,
    budget=60
)

# Print summary
print(architecture.generate_summary())

# Export to files
agent.export_architecture(architecture, format="all")
```

### Custom Configuration

```python
from ai_architect_agent import AIArchitectAgent, ArchitectureConfig

config = ArchitectureConfig(
    company_name="Construction Materials Co",
    country="Uruguay",
    monthly_conversations=1500,
    monthly_budget_min=25,
    monthly_budget_max=75,
    whatsapp_priority=10,  # 1-10, higher = more important
    messenger_priority=6,
    instagram_priority=5,
    mercadolibre_priority=8,
    prefer_free_hosting=True,
    latency_sensitive=True,
)

agent = AIArchitectAgent(config=config)
architecture = agent.generate_architecture()
```

### Compare Tiers

```python
agent = AIArchitectAgent()
comparisons = agent.compare_tiers()

for tier, data in comparisons.items():
    print(f"{tier}: ${data['monthly_cost']}/mo, {data['channels']} channels")
```

## Output Files

Generated architectures are exported to `./architectures/`:

- `architecture_<tier>_<timestamp>.json` - Full architecture data
- `architecture_<tier>_<timestamp>.md` - Detailed Markdown documentation
- `architecture_<tier>_<timestamp>_summary.txt` - Quick reference summary

## Architecture Components

### Channels

| Channel | Monthly Cost | Key Insight |
|---------|-------------|-------------|
| WhatsApp | $20-35 | Service conversations FREE since Nov 2024 |
| Messenger | $0 | Graph API is completely free |
| Instagram | $0 | Free, shares Facebook App with Messenger |
| Mercado Libre | $0 | Free for registered sellers |

### Infrastructure

| Component | Recommended | Cost |
|-----------|-------------|------|
| Hosting | Oracle Cloud Free / Vultr | $0-5/mo |
| Orchestration | n8n Community Edition | $0 |
| LLM | GPT-4o-mini | ~$1/mo |
| Database | SQLite (< 5k conversations) | $0 |
| SSL | Let's Encrypt | $0 |

### LLM Cost Comparison

| Model | 1,000 Conversations | 2,000 Conversations |
|-------|---------------------|---------------------|
| GPT-4o-mini | $0.45/mo | $0.90/mo |
| GPT-4o | $7.50/mo | $15.00/mo |
| Gemini Flash | $0.45/mo (or free tier) | $0.90/mo |

## Implementation Roadmap

### Phase 1: Core + WhatsApp (Week 1-2)
- Deploy hosting (Oracle/Vultr)
- Install n8n orchestrator
- Configure WhatsApp Business API
- Integrate Python backend + LLM

### Phase 2: Messenger + Instagram (Week 3)
- Create Facebook App
- Submit for App Review
- Configure webhooks

### Phase 3: Mercado Libre (Week 4-5)
- Implement OAuth 2.0 flow
- Set up Questions/Messages API
- Handle token refresh

### Phase 4: Optimization (Week 6)
- Enable LLM caching
- Set up monitoring
- Document operations

## Cost Optimization Tips

1. **Maximize customer-initiated WhatsApp messages** (free) vs business-initiated (paid)
2. **Enable OpenAI prompt caching** for 50% savings on repeated prompts
3. **Use Gemini Flash free tier** (1,500 req/day) as LLM fallback
4. **Consolidate Messenger/Instagram** under single Facebook App
5. **Start with SQLite** for < 5,000 monthly conversations

## Project Structure

```
ai_architect_agent/
├── __init__.py              # Package entry point
├── __main__.py              # CLI module entry
├── architect_agent.py       # Main orchestrator
├── cli.py                   # Command-line interface
├── models/
│   ├── architecture.py      # Architecture data models
│   ├── channels.py          # Channel specifications
│   └── infrastructure.py    # Hosting & LLM models
├── engines/
│   ├── architecture_generator.py  # Main generator
│   ├── channel_selector.py        # Channel selection logic
│   ├── cost_optimizer.py          # Cost optimization
│   └── roadmap_builder.py         # Implementation roadmap
└── utils/
    └── visualizer.py        # ASCII diagrams & charts
```

## Requirements

- Python 3.9+
- No external dependencies for core functionality

## License

MIT License - See LICENSE file for details.

---

*Generated by AI Architect Agent v1.0.0*
