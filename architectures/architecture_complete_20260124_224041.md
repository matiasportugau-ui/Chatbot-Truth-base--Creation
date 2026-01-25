# Panelin BMC Uruguay Chatbot Architecture

**Version:** 1.0.0  
**Created:** 2026-01-24  
**Tier:** Complete  
**Target:** Panelin BMC Uruguay (Uruguay)

---

## Executive Summary

This architecture deploys a multi-channel AI chatbot for **1,500 monthly conversations** at approximately **$13.75/month**, saving **$2,115.00 annually** compared to Botmaker ($190/month).

---

## Architecture Diagram

```

+------------------+     +-------------------+     +------------------+
|    CUSTOMERS     | --> |   CHANNEL APIs    | --> |  WEBHOOK SERVER  |
+------------------+     +-------------------+     +------------------+
                         | WhatsApp Business / Facebook Messenger / |          |
                         +-------------------+     v
                                               +------------------+
                                               |    n8n (free)    |
                                               |   Orchestrator   |
                                               +------------------+
                                                        |
                              +-------------------------+-------------------------+
                              |                         |                         |
                              v                         v                         v
                    +------------------+      +------------------+      +------------------+
                    |   GPT-4o Mini    |      |  Python Backend  |      |    Database      |
                    |    (LLM API)     |      | Quotation Engine |      | (SQLite)  |
                    +------------------+      +------------------+      +------------------+
                              |                         |
                              +-------------------------+
                                        |
                                        v
                              +------------------+
                              |    RESPONSE      |
                              | --> Customer     |
                              +------------------+

HOSTING: Oracle Cloud (Always Free) (Sao Paulo)
COST: ~$0.00/mo hosting + API fees

```

---

## Cost Breakdown

| Component | Monthly Cost |
|-----------|-------------|
| Cloud Hosting | $0.00 |
| WhatsApp Business API | $12.13 |
| LLM API (OpenAI) | $0.37 |
| Contingency (10%) | $1.25 |
| **TOTAL** | **$13.75** |

---

## Channel Configuration

### WhatsApp Business

- **Status:** Enabled
- **Priority:** 1/10
- **Traffic Share:** 70%
- **Implementation Hours:** 40
- **Notes:** Meta Cloud API direct. Marketing=$0.065, Utility=$0.012. Service conversations (customer-initiated) FREE since Nov 2024.

### Facebook Messenger

- **Status:** Enabled
- **Priority:** 2/10
- **Traffic Share:** 15%
- **Implementation Hours:** 16
- **Notes:** Graph API is completely FREE. No message fees.

### Instagram DMs

- **Status:** Enabled
- **Priority:** 3/10
- **Traffic Share:** 10%
- **Implementation Hours:** 8
- **Notes:** Graph API is completely FREE. Same app as Messenger.

### Mercado Libre

- **Status:** Enabled
- **Priority:** 2/10
- **Traffic Share:** 5%
- **Implementation Hours:** 60
- **Notes:** FREE for registered sellers. Focus on Questions API for pre-sale.

---

## Infrastructure Stack

### Hosting: Oracle Cloud (Always Free)

- **Region:** Sao Paulo
- **Cost:** $0.00/month
- **Specs:** 4 CPU, 24GB RAM, 200GB storage
- **Latency:** ~50ms to Uruguay
- **Notes:** Best free value. ARM architecture may require container adjustments. Use Sao Paulo region. Capacity constraints may delay provisioning.

### LLM: GPT-4o Mini

- **Model ID:** `gpt-4o-mini`
- **Input Cost:** $0.15/1M tokens
- **Output Cost:** $0.6/1M tokens
- **Caching:** Yes (50% discount)
- **Notes:** RECOMMENDED. Handles 90%+ of queries effectively at 16x less than GPT-4o. Best cost/performance ratio for quotation bots.

### Orchestration: n8n (self-hosted, free)

---

## Implementation Roadmap

### Phase 1: Core Infrastructure + WhatsApp

**Duration:** 2 week(s) | **Hours:** 40

Establish the foundation: cloud hosting, n8n orchestration, Python backend, and WhatsApp Business integration. This phase delivers a working chatbot handling 70% of expected traffic.

**Tasks:**
- Provision cloud hosting (Oracle Cloud or Vultr)
- Install and configure n8n Community Edition
- Set up HTTPS with Let's Encrypt SSL
- Configure webhook endpoints
- Deploy Python quotation engine
- Integrate LLM API (GPT-4o-mini)
- Create Meta Business Account
- Register at developers.facebook.com
- Submit business verification
- Configure WhatsApp webhook in n8n
- Set up message templates
- Test end-to-end WhatsApp flow

**Deliverables:**
- Running n8n instance with HTTPS
- Python backend deployed and accessible
- LLM integration tested and working
- Verified WhatsApp Business account
- Working WhatsApp chatbot responding to messages
- Template messages configured for business-initiated contact

### Phase 2: Messenger + Instagram

**Duration:** 1 week(s) | **Hours:** 24

Expand to Facebook Messenger and Instagram. Both channels share the same Facebook App and similar integration patterns, making this a natural second phase. Adds ~25% traffic coverage.

**Tasks:**
- Create Facebook App (if not existing from WhatsApp)
- Configure pages_messaging permission
- Prepare App Review demonstration video
- Submit for Facebook App Review
- Link Facebook Page to App
- Configure Messenger webhook in n8n
- Implement Messenger-specific message formatting
- Test Messenger conversation flows
- Connect Instagram Business account to Facebook Page
- Configure Instagram webhook (shared with Messenger)
- Handle Instagram-specific media messages
- Test Instagram DM flows
- Consolidate Messenger/Instagram handlers (shared codebase)

**Deliverables:**
- Approved Facebook App with messaging permissions
- Working Messenger chatbot
- Working Instagram DM chatbot

### Phase 3: Mercado Libre

**Duration:** 2 week(s) | **Hours:** 60

Integrate with Mercado Libre's Questions and Messages APIs. This is the most complex integration due to OAuth requirements, message moderation, and two separate API systems.

**Tasks:**
- Create Mercado Libre application
- Implement OAuth 2.0 authentication flow
- Set up token refresh mechanism (6-hour expiry)
- Configure Questions API webhook
- Configure Messages API webhook
- Implement 350-character message truncation
- Design contextual responses (avoid AUTOMATIC_MESSAGE flags)
- Test pre-sale question automation
- Test post-sale message handling
- Implement human escalation for complex issues
- Consider pursuing official ML certification

**Deliverables:**
- Mercado Libre app with proper OAuth flow
- Automated pre-sale question responses
- Automated post-sale message handling
- Human escalation workflow

### Phase 4: Optimization

**Duration:** 1 week(s) | **Hours:** 20

Refine the chatbot based on real usage data. Implement monitoring, optimize costs, and prepare for scaling.

**Tasks:**
- Analyze conversation logs for improvement opportunities
- Implement response caching for frequent questions
- Enable LLM prompt caching for cost reduction
- Set up monitoring and alerting
- Configure human handoff workflows (Chatwoot optional)
- Document operational procedures
- Create runbooks for common issues
- Performance test under expected load
- Review and optimize WhatsApp template usage

**Deliverables:**
- Monitoring dashboard
- Response caching system
- Operational documentation
- Performance benchmarks

---

## Recommendations

1. Start with WhatsApp alone; it handles 70%+ of traffic
1. Use GPT-4o-mini for 90%+ of queries; reserve GPT-4o for edge cases
1. Enable OpenAI prompt caching for 50% savings on repeated prompts
1. Maximize customer-initiated WhatsApp messages (free) vs business-initiated (paid)
1. Consider Chatwoot (free, self-hosted) for unified human agent inbox
1. Focus Mercado Libre automation on Questions API (pre-sale) for max conversion impact
1. Switched to Oracle Cloud Free tier (saves $5.00/mo)
1. Messenger and Instagram share single Facebook App (no extra setup)

## Risks & Mitigations

- Oracle Cloud Free: ARM instance availability may delay initial setup. Have Vultr Buenos Aires as backup ($5/mo).
- WhatsApp verification can take 1-3 weeks. Start process early.
- Mercado Libre may moderate AUTOMATIC_MESSAGE responses. Design contextual, non-templated replies.
- Budget 4-8 hours/month for ongoing maintenance and improvements.

---

*Generated by AI Architect Agent v1.0.0*