# GPT Actions - Referencia Rápida

**Para**: Implementación en Panelin  
**Fecha**: 2026-01-26

---

## ¿Qué son las Actions?

Integraciones con **APIs externas** que permiten a un GPT:
- ✅ Consultar datos en tiempo real (precios, stock)
- ✅ Escribir/guardar datos (cotizaciones, leads)
- ✅ Ejecutar operaciones (enviar emails, crear órdenes)
- ✅ Integrar con servicios externos (Shopify, CRM, WhatsApp)

---

## Ubicación en GPT Builder

```
Configure → [scroll down] → ACTIONS → [+ Create new action]
```

Está **debajo** de:
- Knowledge (archivos)
- Capabilities (Web Browsing, DALL·E, Code Interpreter)

---

## Componentes de una Action

| Componente | Descripción |
|------------|-------------|
| **Schema OpenAPI** | Define endpoints, parámetros, respuestas (YAML/JSON) |
| **Autenticación** | None, API Key, o OAuth 2.0 |
| **Privacy Policy** | URL requerida para GPTs públicos |
| **Backend/Servidor** | Tu API que procesa las solicitudes |

---

## Tipos de Autenticación

| Tipo | Uso Típico |
|------|-----------|
| **None** | APIs públicas sin restricción |
| **API Key** | APIs privadas con clave secreta (más común) |
| **OAuth 2.0** | Servicios que requieren autorización del usuario |

---

## Schema Mínimo Funcional

```yaml
openapi: 3.0.0
info:
  title: Mi API
  version: 1.0.0
servers:
  - url: https://api.midominio.com
paths:
  /endpoint:
    get:
      operationId: miOperacion
      summary: Descripción corta
      responses:
        '200':
          description: OK
```

---

## Actions Propuestas para Panelin

| Action | Prioridad | Función |
|--------|-----------|---------|
| `calculate_quote` | ⭐ Alta | Cotización determinística con motor Python |
| `check_stock` | ⭐ Alta | Verificar disponibilidad en tiempo real |
| `search_kb` | ⭐ Alta | Búsqueda híbrida optimizada en KB |
| `get_price` | Media | Precios actualizados de Shopify |
| `send_email` | Media | Enviar cotización por email |
| `create_lead` | Baja | Guardar lead en CRM |

---

## Flujo de Decisión: ¿Cuándo usar Actions?

```
¿Los datos cambian frecuentemente?
├── NO → Knowledge Base
└── SÍ → ¿Necesitas escribir datos?
          ├── NO → ¿Son públicos de internet?
          │         ├── SÍ → Web Browsing
          │         └── NO → Actions (lectura)
          └── SÍ → Actions ✅
```

---

## Comparativa Rápida

| | Knowledge | Web Browse | Code Interp | Actions |
|--|-----------|------------|-------------|---------|
| Datos | Estáticos | Internet | Sesión | APIs |
| Actualización | Manual | Tiempo real | Por sesión | Tiempo real |
| Escribir | ❌ | ❌ | ❌ | ✅ |
| Servidor | ❌ | ❌ | ❌ | ✅ |

---

## Seguridad Crítica

❌ **NUNCA**:
- API keys en Knowledge Base
- API keys en Canvas
- API keys en instrucciones

✅ **SIEMPRE**:
- Usar autenticación de GPT Builder
- Validar inputs en backend
- Rate limiting en backend

---

## Roadmap para Panelin

```
ACTUAL: Knowledge + Code Interpreter ✅
   ↓
FASE 1: Backend básico (calculate_quote, search_kb)
   ↓
FASE 2: Integración Shopify (check_stock, get_price)
   ↓
FASE 3: Comunicación (send_email, whatsapp)
```

---

## Recursos

- [Guía Completa](./GPT_ACTIONS_COMPLETE_GUIDE.md)
- [OpenAI Docs](https://platform.openai.com/docs/actions)
- [Swagger Editor](https://editor.swagger.io)

---

**Ver documentación completa**: `GPT_ACTIONS_COMPLETE_GUIDE.md`
