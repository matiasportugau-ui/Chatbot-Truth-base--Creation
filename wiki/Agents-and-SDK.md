# Agents and SDK

## Multi-platform agent overview
Panelin can run as a function-calling agent across multiple platforms:
- OpenAI (ready)
- Claude (ready)
- Gemini (ready)
- Grok (limited: no public function calling)
- GitHub Copilot (compatible)

Core flow:
```
Agent (OpenAI/Claude/Gemini)
    -> Function call
    -> motor_cotizacion_panelin.py + KB files
    -> Structured response
```

## OpenAI Agents SDK (TypeScript)
The repo includes a full Agents SDK implementation:
- ClassificationAgent (routing)
- CotizacionAgent (5-phase quotation workflow)
- EvaluacionEntrenamientoAgent (sales evaluation)
- InformacionAgent (product and spec queries)
- Guardrails (jailbreak, PII masking, moderation)
- Personalization (Mauro, Martin, Rami)

### Quick start
```bash
npm install
```

Create `.env`:
```
OPENAI_API_KEY=your-key
```

Run example:
```bash
ts-node panelin_agents_sdk_example.ts
```
Optional:
```bash
npm run test
```

### Integration notes
The SDK includes tool placeholders that must be wired to Python backends:
- `calcular_cotizacion` -> `motor_cotizacion_panelin.py`
- `buscar_en_base_conocimiento` -> KB JSON search
- `evaluar_vendedor` -> evaluation logic

Common integration options:
- REST API (Flask/FastAPI)
- Child process invocation

## References
- RESUMEN_AGENTES_IA.md
- PANELIN_AGENTS_SDK_README.md
- PANELIN_AGENTS_SDK_QUICKSTART.md
