# Guía Completa: Acciones (Actions) en GPT Builder

**Versión**: 2.0 Comprehensive  
**Fecha**: 2026-01-26  
**Propósito**: Documentación exhaustiva de la sección de Acciones en la configuración de GPT

---

## 📋 Tabla de Contenidos

1. [¿Qué son las Actions?](#1-qué-son-las-actions)
2. [Ubicación en GPT Builder](#2-ubicación-en-gpt-builder)
3. [Arquitectura y Funcionamiento](#3-arquitectura-y-funcionamiento)
4. [Tipos de Autenticación](#4-tipos-de-autenticación)
5. [Especificación OpenAPI](#5-especificación-openapi)
6. [Casos de Uso y Ejemplos](#6-casos-de-uso-y-ejemplos)
7. [Actions vs Otras Capacidades](#7-actions-vs-otras-capacidades)
8. [Limitaciones y Consideraciones](#8-limitaciones-y-consideraciones)
9. [Seguridad y Mejores Prácticas](#9-seguridad-y-mejores-prácticas)
10. [Implementación para Panelin](#10-implementación-para-panelin)
11. [Troubleshooting](#11-troubleshooting)
12. [Recursos y Referencias](#12-recursos-y-referencias)

---

## 1. ¿Qué son las Actions?

### 1.1 Definición

Las **Actions** (Acciones) son integraciones con APIs externas que permiten que un GPT personalizado realice operaciones más allá de generar texto. Básicamente, le dan al GPT la capacidad de **"hacer cosas"** en el mundo real, no solo responder preguntas.

```
┌─────────────────────────────────────────────────────────────┐
│                    GPT SIN ACTIONS                          │
│                                                             │
│  Usuario: "¿Cuál es el precio actual de Bitcoin?"           │
│  GPT: "No tengo acceso a información en tiempo real..."     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    GPT CON ACTIONS                          │
│                                                             │
│  Usuario: "¿Cuál es el precio actual de Bitcoin?"           │
│  GPT: [Llama API de precios] "Bitcoin está a $65,432.10"    │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Capacidades Fundamentales

| Capacidad | Descripción | Ejemplo |
|-----------|-------------|---------|
| **Leer datos externos** | Consultar APIs para obtener información actualizada | Precio de productos, stock, clima |
| **Escribir datos** | Enviar información a sistemas externos | Crear órdenes, guardar cotizaciones |
| **Ejecutar operaciones** | Disparar procesos en sistemas externos | Enviar emails, generar PDFs en servidor |
| **Integrar servicios** | Conectar con plataformas de terceros | Shopify, CRM, WhatsApp Business |

### 1.3 Diferencia con Otras Funcionalidades

| Funcionalidad | ¿Qué hace? | ¿Requiere servidor externo? |
|---------------|------------|----------------------------|
| **Knowledge Base** | Almacena archivos estáticos para consulta | ❌ No |
| **Web Browsing** | Navega por internet para buscar información | ❌ No |
| **Code Interpreter** | Ejecuta código Python localmente | ❌ No |
| **DALL·E** | Genera imágenes | ❌ No |
| **Actions** | Llama APIs externas personalizadas | ✅ Sí |

---

## 2. Ubicación en GPT Builder

### 2.1 Cómo Acceder

1. Ir a [chatgpt.com/gpts/editor](https://chatgpt.com/gpts/editor)
2. Seleccionar el GPT a configurar (o crear uno nuevo)
3. Ir a la pestaña **"Configure"**
4. Scroll hasta encontrar la sección **"Actions"**

```
┌─────────────────────────────────────────────────────────────┐
│                GPT BUILDER - CONFIGURE                      │
├─────────────────────────────────────────────────────────────┤
│  Name: [___________________]                                │
│  Description: [___________________]                         │
│  Instructions: [___________________]                        │
│                                                             │
│  ═══════════════════════════════════════════════════════   │
│  KNOWLEDGE                                                  │
│  [+ Upload files] ← Aquí se suben archivos de conocimiento │
│  ═══════════════════════════════════════════════════════   │
│                                                             │
│  ═══════════════════════════════════════════════════════   │
│  CAPABILITIES                                               │
│  ☑ Web Browsing   ☑ DALL·E   ☑ Code Interpreter            │
│  ═══════════════════════════════════════════════════════   │
│                                                             │
│  ═══════════════════════════════════════════════════════   │
│  ACTIONS  ← ¡ESTA SECCIÓN!                                  │
│  [+ Create new action]                                      │
│  ═══════════════════════════════════════════════════════   │
│                                                             │
│  Additional Settings...                                     │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Interfaz de Creación de Actions

Al hacer clic en **"Create new action"**, aparece:

```
┌─────────────────────────────────────────────────────────────┐
│  NEW ACTION                                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Schema:                                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ openapi: 3.0.0                                      │   │
│  │ info:                                               │   │
│  │   title: My API                                     │   │
│  │   version: 1.0.0                                    │   │
│  │ ...                                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Authentication:                                            │
│  ○ None  ○ API Key  ○ OAuth                                │
│                                                             │
│  Privacy Policy URL: [_________________________]            │
│                                                             │
│  [Test] [Cancel] [Save]                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Arquitectura y Funcionamiento

### 3.1 Flujo de Ejecución

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO DE UNA ACTION                      │
└─────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   Usuario    │
    │  hace pregunta│
    └──────┬───────┘
           │
           ▼
    ┌──────────────────────────────────────┐
    │              GPT                      │
    │  1. Interpreta la pregunta           │
    │  2. Decide si necesita llamar Action │
    │  3. Extrae parámetros del mensaje    │
    └──────────────┬───────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────┐
    │         OpenAI Proxy                  │
    │  • Valida schema                      │
    │  • Agrega autenticación              │
    │  • Hace la llamada HTTP              │
    └──────────────┬───────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────┐
    │         API Externa                   │
    │  (Tu servidor / Servicio tercero)    │
    │                                       │
    │  • Procesa la solicitud              │
    │  • Retorna respuesta JSON            │
    └──────────────┬───────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────┐
    │              GPT                      │
    │  • Recibe respuesta de API           │
    │  • Interpreta los datos              │
    │  • Formula respuesta en lenguaje     │
    │    natural para el usuario           │
    └──────────────┬───────────────────────┘
                   │
                   ▼
    ┌──────────────┐
    │   Usuario    │
    │ ve respuesta │
    └──────────────┘
```

### 3.2 Componentes Clave

| Componente | Descripción |
|------------|-------------|
| **Schema OpenAPI** | Define la estructura de la API (endpoints, parámetros, respuestas) |
| **Autenticación** | Cómo el GPT se autentica con la API externa |
| **Privacy Policy** | URL con política de privacidad (requerido para APIs públicas) |
| **Servidor/API** | El backend que recibe y procesa las solicitudes |

### 3.3 Métodos HTTP Soportados

| Método | Uso Típico | Ejemplo |
|--------|-----------|---------|
| `GET` | Leer/consultar datos | Obtener precio de producto |
| `POST` | Crear recursos / Enviar datos | Crear cotización, enviar email |
| `PUT` | Actualizar recursos completos | Actualizar pedido completo |
| `PATCH` | Actualizar parcialmente | Cambiar estado de pedido |
| `DELETE` | Eliminar recursos | Cancelar suscripción |

---

## 4. Tipos de Autenticación

### 4.1 Ninguna (None)

```yaml
# Sin autenticación - API pública
servers:
  - url: https://api.publicdata.com/v1
# No se necesita configuración adicional
```

**Cuándo usar**: APIs públicas sin restricción de acceso.

**Riesgos**: Cualquiera puede acceder, limitado a datos no sensibles.

### 4.2 API Key

La más común para integraciones personalizadas.

**Opciones de ubicación**:

| Tipo | Header | Ejemplo |
|------|--------|---------|
| Custom Header | `X-API-Key: tu-clave` | Más común |
| Bearer Token | `Authorization: Bearer tu-clave` | Estándar OAuth-like |
| Query Parameter | `?api_key=tu-clave` | Menos seguro, visible en logs |

**Configuración en Schema**:

```yaml
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
security:
  - ApiKeyAuth: []
```

### 4.3 OAuth 2.0

Para integraciones que requieren autorización del usuario.

**Flujos soportados**:

| Flujo | Descripción | Uso Típico |
|-------|-------------|-----------|
| Authorization Code | Usuario autoriza en ventana externa | Servicios como Google, Microsoft |
| Client Credentials | Credenciales de la aplicación | APIs de empresa |

**Configuración en Schema**:

```yaml
components:
  securitySchemes:
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://example.com/oauth/authorize
          tokenUrl: https://example.com/oauth/token
          scopes:
            read:products: Leer productos
            write:orders: Crear órdenes
```

### 4.4 HTTP Basic

```yaml
components:
  securitySchemes:
    BasicAuth:
      type: http
      scheme: basic
```

**En GPT Builder**: Ingresar username y password.

---

## 5. Especificación OpenAPI

### 5.1 Estructura Básica

```yaml
openapi: 3.0.0            # Versión de OpenAPI (3.0.0 o 3.1.0)
info:
  title: Mi API           # Nombre descriptivo
  version: 1.0.0          # Versión de tu API
  description: |          # Descripción detallada
    API para gestionar cotizaciones y productos.
    
servers:
  - url: https://api.tudominio.com/v1
    description: Servidor de producción

paths:
  /productos:
    get:
      ...
  /cotizacion:
    post:
      ...

components:
  securitySchemes:
    ...
  schemas:
    ...
```

### 5.2 Definición de Endpoints

```yaml
paths:
  /productos/{id}:
    get:
      operationId: getProductById      # ID único para la operación
      summary: Obtener producto por ID  # Resumen corto
      description: |                    # Descripción larga
        Retorna los detalles completos de un producto,
        incluyendo precio, stock y variantes.
      parameters:
        - name: id
          in: path                      # path, query, header, cookie
          required: true
          description: ID del producto
          schema:
            type: string
      responses:
        '200':
          description: Producto encontrado
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Product'
        '404':
          description: Producto no encontrado
```

### 5.3 Parámetros

| Tipo (`in`) | Descripción | Ejemplo |
|-------------|-------------|---------|
| `path` | En la URL | `/productos/{id}` |
| `query` | En query string | `?categoria=paneles` |
| `header` | En headers | `X-Custom-Header` |
| `cookie` | En cookies | `session_id` |

```yaml
parameters:
  - name: categoria
    in: query
    required: false
    schema:
      type: string
      enum: ["paneles", "accesorios", "impermeabilizantes"]
    description: Filtrar por categoría
    
  - name: precio_min
    in: query
    required: false
    schema:
      type: number
      minimum: 0
    description: Precio mínimo en USD
```

### 5.4 Request Body (para POST, PUT, PATCH)

```yaml
paths:
  /cotizacion:
    post:
      operationId: createQuote
      summary: Crear nueva cotización
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - producto
                - espesor
                - largo
                - ancho
              properties:
                producto:
                  type: string
                  enum: ["ISODEC EPS", "ISODEC PIR", "ISOPANEL EPS"]
                  description: Tipo de producto
                espesor:
                  type: string
                  description: Espesor en mm
                largo:
                  type: number
                  description: Largo en metros
                ancho:
                  type: number
                  description: Ancho en metros
                luz:
                  type: number
                  description: Distancia entre apoyos
                tipo_fijacion:
                  type: string
                  enum: ["hormigon", "metal", "madera"]
                  default: "hormigon"
```

### 5.5 Respuestas

```yaml
responses:
  '200':
    description: Operación exitosa
    content:
      application/json:
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              $ref: '#/components/schemas/QuoteResult'
  '400':
    description: Parámetros inválidos
    content:
      application/json:
        schema:
          type: object
          properties:
            error:
              type: string
            details:
              type: array
              items:
                type: string
  '401':
    description: No autorizado
  '500':
    description: Error interno del servidor
```

### 5.6 Schemas Reutilizables

```yaml
components:
  schemas:
    Product:
      type: object
      properties:
        id:
          type: string
        title:
          type: string
        price:
          type: number
          format: float
        currency:
          type: string
          default: "USD"
        in_stock:
          type: boolean
        variants:
          type: array
          items:
            $ref: '#/components/schemas/Variant'
            
    Variant:
      type: object
      properties:
        sku:
          type: string
        thickness:
          type: string
        price:
          type: number
```

---

## 6. Casos de Uso y Ejemplos

### 6.1 Consulta de Productos en Shopify

**Schema completo**:

```yaml
openapi: 3.1.0
info:
  title: BMC Shopify Products API
  version: 1.0.0
  description: API para consultar productos de BMC Uruguay en Shopify

servers:
  - url: https://bmcuruguay.com.uy

paths:
  /products/{handle}.json:
    get:
      operationId: getProductByHandle
      summary: Obtener producto por handle
      description: |
        Consulta un producto específico usando su handle (URL slug).
        Retorna precio, stock y variantes.
      parameters:
        - name: handle
          in: path
          required: true
          schema:
            type: string
          description: Handle del producto (ej: isodec-eps-techo)
          examples:
            isodec:
              value: "isodec-eps-techo"
            isoroof:
              value: "isoroof-3g"
      responses:
        '200':
          description: Producto encontrado
          content:
            application/json:
              schema:
                type: object
                properties:
                  product:
                    type: object
                    properties:
                      id:
                        type: integer
                      title:
                        type: string
                      handle:
                        type: string
                      variants:
                        type: array
                        items:
                          type: object
                          properties:
                            id:
                              type: integer
                            price:
                              type: string
                            sku:
                              type: string
                            available:
                              type: boolean
        '404':
          description: Producto no encontrado
```

### 6.2 Calculadora de Cotización (Backend Propio)

```yaml
openapi: 3.0.0
info:
  title: BMC Quotation Engine
  version: 1.0.0
  description: Motor de cotización determinístico para paneles

servers:
  - url: https://api.bmc.uy/v1

paths:
  /quote:
    post:
      operationId: calculateQuote
      summary: Calcular cotización completa
      description: |
        Calcula una cotización usando el motor Python determinístico.
        Valida autoportancia, calcula materiales y genera desglose.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - producto
                - espesor
                - largo
                - ancho
                - luz
                - tipo_fijacion
              properties:
                producto:
                  type: string
                  enum: 
                    - "ISODEC EPS"
                    - "ISODEC PIR"
                    - "ISOPANEL EPS"
                    - "ISOROOF 3G"
                    - "ISOWALL PIR"
                espesor:
                  type: string
                  description: Espesor en mm
                largo:
                  type: number
                  description: Largo del área en metros
                  minimum: 0.1
                ancho:
                  type: number
                  description: Ancho del área en metros
                  minimum: 0.1
                luz:
                  type: number
                  description: Distancia entre apoyos (metros)
                  minimum: 0.1
                tipo_fijacion:
                  type: string
                  enum: ["hormigon", "metal", "madera"]
                alero_1:
                  type: number
                  default: 0
                alero_2:
                  type: number
                  default: 0
      responses:
        '200':
          description: Cotización calculada exitosamente
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  cotizacion:
                    type: object
                    properties:
                      producto:
                        type: string
                      validacion:
                        type: object
                        properties:
                          cumple_autoportancia:
                            type: boolean
                          autoportancia:
                            type: number
                          advertencia:
                            type: string
                      materiales:
                        type: array
                        items:
                          type: object
                      costos:
                        type: object
                        properties:
                          subtotal:
                            type: number
                          iva:
                            type: number
                          total:
                            type: number
        '400':
          description: Parámetros inválidos
        '500':
          description: Error en el cálculo

components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key

security:
  - ApiKeyAuth: []
```

### 6.3 Verificación de Stock en Tiempo Real

```yaml
openapi: 3.0.0
info:
  title: BMC Stock Checker
  version: 1.0.0

servers:
  - url: https://api.bmc.uy/v1

paths:
  /stock/{sku}:
    get:
      operationId: checkStock
      summary: Verificar stock de producto
      parameters:
        - name: sku
          in: path
          required: true
          schema:
            type: string
          description: SKU del producto (ej: ISODEC-EPS-100)
      responses:
        '200':
          description: Información de stock
          content:
            application/json:
              schema:
                type: object
                properties:
                  sku:
                    type: string
                  in_stock:
                    type: boolean
                  quantity:
                    type: integer
                  lead_time_days:
                    type: integer
                  last_updated:
                    type: string
                    format: date-time
```

### 6.4 Envío de Cotización por Email

```yaml
paths:
  /send-quote:
    post:
      operationId: sendQuoteByEmail
      summary: Enviar cotización por email
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - recipient_email
                - quote_data
              properties:
                recipient_email:
                  type: string
                  format: email
                recipient_name:
                  type: string
                quote_data:
                  type: object
                  description: Datos de la cotización
                include_pdf:
                  type: boolean
                  default: true
      responses:
        '200':
          description: Email enviado
          content:
            application/json:
              schema:
                type: object
                properties:
                  sent:
                    type: boolean
                  message_id:
                    type: string
```

### 6.5 Integración con CRM

```yaml
paths:
  /crm/lead:
    post:
      operationId: createLead
      summary: Crear lead en CRM
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                email:
                  type: string
                phone:
                  type: string
                interest:
                  type: string
                quote_total:
                  type: number
                source:
                  type: string
                  default: "GPT Panelin"
      responses:
        '201':
          description: Lead creado
```

---

## 7. Actions vs Otras Capacidades

### 7.1 Comparativa Detallada

| Aspecto | Knowledge Base | Web Browsing | Code Interpreter | Actions |
|---------|---------------|--------------|------------------|---------|
| **Datos** | Estáticos, subidos | Internet público | Archivos subidos | APIs externas |
| **Actualización** | Manual | Tiempo real | Por sesión | Tiempo real |
| **Cálculos** | ❌ | ❌ | ✅ Python | ✅ Backend |
| **Escribir datos** | ❌ | ❌ | ❌ | ✅ |
| **Requiere servidor** | ❌ | ❌ | ❌ | ✅ |
| **Personalización** | Media | Baja | Alta | Máxima |
| **Complejidad** | Baja | Baja | Media | Alta |

### 7.2 ¿Cuándo Usar Cada Uno?

```
┌─────────────────────────────────────────────────────────────┐
│  ÁRBOL DE DECISIÓN                                          │
└─────────────────────────────────────────────────────────────┘

¿Los datos cambian frecuentemente?
│
├── NO → Knowledge Base (archivos estáticos)
│
└── SÍ → ¿Necesitas escribir datos o ejecutar acciones?
          │
          ├── NO → ¿Son datos públicos de internet?
          │         │
          │         ├── SÍ → Web Browsing
          │         │
          │         └── NO → Actions (API de lectura)
          │
          └── SÍ → ¿Tienes/puedes tener un backend?
                    │
                    ├── SÍ → Actions ✅
                    │
                    └── NO → Code Interpreter (limitado)
```

### 7.3 Combinando Capacidades (Estrategia Híbrida)

Para Panelin, la estrategia óptima es:

```
┌─────────────────────────────────────────────────────────────┐
│  ARQUITECTURA HÍBRIDA PANELIN                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  NIVEL 1: Knowledge Base (Siempre disponible)               │
│  ├── BMC_Base_Conocimiento_GPT-2.json                       │
│  ├── Fórmulas, reglas, especificaciones                     │
│  └── → Consulta PRIMERO, source of truth offline            │
│                                                             │
│  NIVEL 2: Code Interpreter (Cálculos locales)               │
│  ├── Ejecutar fórmulas de cotización                        │
│  ├── Procesar CSV                                           │
│  └── Generar PDFs                                           │
│                                                             │
│  NIVEL 3: Actions (Cuando se implemente backend)            │
│  ├── Verificar precios en tiempo real                       │
│  ├── Consultar stock actualizado                            │
│  ├── Guardar cotizaciones                                   │
│  └── Enviar emails/WhatsApp                                 │
│                                                             │
│  NIVEL 4: Web Browsing (Fallback)                           │
│  └── Solo para información general no crítica              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. Limitaciones y Consideraciones

### 8.1 Limitaciones Técnicas

| Limitación | Descripción | Workaround |
|------------|-------------|------------|
| **Timeout** | Máximo ~30 segundos por request | Optimizar backend, usar caching |
| **Rate Limits** | OpenAI aplica límites | Implementar retry con backoff |
| **Payload Size** | Límites en tamaño de request/response | Paginar respuestas, comprimir datos |
| **CORS** | Algunos servidores bloquean | Configurar headers correctamente |
| **HTTPS Only** | No soporta HTTP | Usar certificados SSL válidos |
| **Streaming** | No soporta respuestas streaming | Diseñar para respuestas completas |

### 8.2 Limitaciones de Contenido

- **No pueden acceder a archivos locales** del usuario
- **No pueden ejecutar código arbitrario** en el servidor (solo lo que la API permita)
- **No pueden recordar entre sesiones** (a menos que guardes en backend)

### 8.3 Consideraciones de Costo

| Componente | Costo | Notas |
|------------|-------|-------|
| **GPT Plus** | $20/mes | Necesario para usar GPTs personalizados |
| **API Backend** | Variable | Hosting, serverless, etc. |
| **Servicios terceros** | Variable | Shopify API (gratis hasta límite), WhatsApp (por mensaje) |
| **Desarrollo** | Tiempo | Crear y mantener el backend |

### 8.4 Latencia

```
Tiempo total = Tiempo GPT + Tiempo red + Tiempo API + Tiempo respuesta GPT

Ejemplo típico:
- GPT procesa pregunta: ~1-2s
- Llamada a API: ~0.5-2s (depende del backend)
- GPT formula respuesta: ~1-2s
- Total: 2.5-6s para respuesta completa
```

---

## 9. Seguridad y Mejores Prácticas

### 9.1 Principios de Seguridad

| Principio | Implementación |
|-----------|----------------|
| **Mínimo privilegio** | API keys con permisos mínimos necesarios |
| **Secretos seguros** | Nunca exponer en Knowledge Base o Canvas |
| **Validación** | Validar todos los inputs en el backend |
| **Rate limiting** | Implementar límites en el backend |
| **Logging** | Registrar todas las llamadas para auditoría |

### 9.2 Manejo de API Keys

❌ **NUNCA hacer**:
- Poner API keys en Knowledge Base
- Escribir API keys en Canvas
- Compartir API keys en las instrucciones del sistema
- Exponer API keys en el schema OpenAPI

✅ **SIEMPRE hacer**:
- Usar el sistema de autenticación de GPT Builder
- Rotar API keys periódicamente
- Usar variables de entorno en el backend
- Limitar scope de las API keys

### 9.3 Validación en Backend

```python
# Ejemplo de validación robusta en el backend

from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

# Validar API key
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.environ.get('VALID_API_KEY'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

# Rate limiting
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.headers.get('X-API-Key'))

@app.route('/quote', methods=['POST'])
@require_api_key
@limiter.limit("10 per minute")
def calculate_quote():
    data = request.json
    
    # Validar inputs
    required = ['producto', 'espesor', 'largo', 'ancho', 'luz']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400
    
    # Validar tipos y rangos
    if data['largo'] <= 0 or data['largo'] > 100:
        return jsonify({'error': 'largo must be between 0 and 100'}), 400
    
    # Procesar cotización
    result = process_quote(data)
    return jsonify(result)
```

### 9.4 Privacy Policy

Para Actions públicas, se requiere una Privacy Policy URL:

```markdown
# Privacy Policy for BMC Panelin API

## Data Collection
- We collect quotation parameters (product, dimensions) to calculate quotes.
- We do not store personal information.

## Data Usage
- Data is used only to generate quotations.
- No data is shared with third parties.

## Data Retention
- Quotation data may be retained for analytics purposes.
- Personal data is deleted upon request.

## Contact
privacy@bmc.uy
```

---

## 10. Implementación para Panelin

### 10.1 Roadmap de Implementación

```
┌─────────────────────────────────────────────────────────────┐
│  FASES DE IMPLEMENTACIÓN ACTIONS PARA PANELIN               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FASE 0: ACTUAL (Sin Actions) ✅                            │
│  └── Usando Knowledge Base + Code Interpreter               │
│                                                             │
│  FASE 1: Backend Básico                                     │
│  ├── Crear API REST Python (Flask/FastAPI)                  │
│  ├── Endpoint: /quote (calcular cotización)                 │
│  ├── Endpoint: /kb/search (buscar en KB)                    │
│  └── Deploy en servicio cloud                               │
│                                                             │
│  FASE 2: Integración Shopify                                │
│  ├── Endpoint: /products (proxy a Shopify)                  │
│  ├── Endpoint: /stock (verificar disponibilidad)            │
│  └── Cache para reducir llamadas                            │
│                                                             │
│  FASE 3: Funcionalidades Avanzadas                          │
│  ├── Endpoint: /send-quote (enviar por email)               │
│  ├── Endpoint: /crm/lead (crear lead en CRM)                │
│  └── Endpoint: /analytics (guardar métricas)                │
│                                                             │
│  FASE 4: WhatsApp Business                                  │
│  └── Endpoint: /whatsapp/send (enviar por WhatsApp)         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 10.2 Actions Propuestas para Panelin

| Action | Prioridad | Complejidad | Beneficio |
|--------|-----------|-------------|-----------|
| `calculate_quote` | Alta ⭐ | Media | Cotización determinística garantizada |
| `search_kb` | Alta ⭐ | Media | Búsqueda híbrida optimizada |
| `verify_stock` | Alta ⭐ | Baja | Stock en tiempo real |
| `get_product_price` | Media | Baja | Precios actualizados de Shopify |
| `send_quote_email` | Media | Media | Automatizar envío |
| `create_crm_lead` | Baja | Media | Tracking de leads |
| `send_whatsapp` | Baja | Alta | Comunicación directa |

### 10.3 Schema Completo Propuesto para Panelin

```yaml
openapi: 3.0.0
info:
  title: Panelin Internal API
  version: 2.0.0
  description: |
    API interna para el GPT Panelin de BMC Uruguay.
    Proporciona cotización determinística, verificación de stock,
    y búsqueda en base de conocimiento.

servers:
  - url: https://api.bmc.uy/v1
    description: Producción
  - url: https://staging-api.bmc.uy/v1
    description: Staging

paths:
  /quote:
    post:
      operationId: calculateQuote
      summary: Calcular cotización determinística
      description: |
        Usa el motor Python para calcular una cotización exacta.
        Valida autoportancia, calcula materiales y accesorios.
      tags: [Quotation]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/QuoteRequest'
      responses:
        '200':
          description: Cotización calculada
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/QuoteResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '500':
          $ref: '#/components/responses/ServerError'

  /kb/search:
    post:
      operationId: searchKnowledgeBase
      summary: Buscar en base de conocimiento
      description: |
        Búsqueda híbrida (semántica + keyword) en la KB.
        Respeta jerarquía de niveles.
      tags: [Knowledge]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [query]
              properties:
                query:
                  type: string
                  description: Texto de búsqueda
                level_priority:
                  type: string
                  enum: ["1", "2", "3", "4", "all"]
                  default: "1"
                max_results:
                  type: integer
                  default: 5
      responses:
        '200':
          description: Resultados de búsqueda
          content:
            application/json:
              schema:
                type: object
                properties:
                  results:
                    type: array
                    items:
                      type: object
                      properties:
                        source:
                          type: string
                        level:
                          type: integer
                        content:
                          type: string
                        confidence:
                          type: number

  /stock/{sku}:
    get:
      operationId: checkStock
      summary: Verificar stock de producto
      tags: [Stock]
      parameters:
        - name: sku
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Estado de stock
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/StockInfo'

  /products/price/{handle}:
    get:
      operationId: getProductPrice
      summary: Obtener precio actualizado de Shopify
      tags: [Products]
      parameters:
        - name: handle
          in: path
          required: true
          schema:
            type: string
          example: isodec-eps-techo
      responses:
        '200':
          description: Información de precio
          content:
            application/json:
              schema:
                type: object
                properties:
                  handle:
                    type: string
                  title:
                    type: string
                  variants:
                    type: array
                    items:
                      type: object
                      properties:
                        thickness:
                          type: string
                        price:
                          type: number
                        currency:
                          type: string

components:
  schemas:
    QuoteRequest:
      type: object
      required:
        - producto
        - espesor
        - largo
        - ancho
        - luz
        - tipo_fijacion
      properties:
        producto:
          type: string
          enum: ["ISODEC EPS", "ISODEC PIR", "ISOPANEL EPS", "ISOROOF 3G", "ISOROOF PLUS", "ISOWALL PIR"]
        espesor:
          type: string
          description: Espesor en mm (ej: "100", "150")
        largo:
          type: number
          description: Largo del área en metros
          minimum: 0.1
          maximum: 100
        ancho:
          type: number
          description: Ancho del área en metros
          minimum: 0.1
          maximum: 50
        luz:
          type: number
          description: Distancia entre apoyos en metros
          minimum: 0.1
          maximum: 15
        tipo_fijacion:
          type: string
          enum: ["hormigon", "metal", "madera"]
        alero_1:
          type: number
          default: 0
        alero_2:
          type: number
          default: 0

    QuoteResponse:
      type: object
      properties:
        success:
          type: boolean
        error:
          type: string
          nullable: true
        cotizacion:
          type: object
          properties:
            producto:
              type: string
            espesor:
              type: string
            dimensiones:
              type: object
              properties:
                largo:
                  type: number
                ancho:
                  type: number
                area:
                  type: number
            validacion:
              type: object
              properties:
                cumple_autoportancia:
                  type: boolean
                autoportancia:
                  type: number
                luz_efectiva:
                  type: number
                advertencia:
                  type: string
            materiales:
              type: array
              items:
                type: object
            costos:
              type: object
              properties:
                subtotal:
                  type: number
                iva:
                  type: number
                total:
                  type: number

    StockInfo:
      type: object
      properties:
        sku:
          type: string
        in_stock:
          type: boolean
        quantity:
          type: integer
        lead_time_days:
          type: integer
        last_updated:
          type: string
          format: date-time

  responses:
    BadRequest:
      description: Parámetros inválidos
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                type: string
              details:
                type: array
                items:
                  type: string

    Unauthorized:
      description: API Key inválida o faltante

    ServerError:
      description: Error interno del servidor

  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: API Key interna de BMC

security:
  - ApiKeyAuth: []

tags:
  - name: Quotation
    description: Operaciones de cotización
  - name: Knowledge
    description: Búsqueda en base de conocimiento
  - name: Stock
    description: Verificación de inventario
  - name: Products
    description: Información de productos
```

### 10.4 Instrucciones del Sistema para Actions

Agregar al sistema de instrucciones de Panelin:

```markdown
# USO DE ACTIONS (API)

## Cuándo usar Actions

1. **calculate_quote**: Usar para cotizaciones que requieran precisión garantizada
   - Preferir sobre cálculos manuales
   - El backend usa el motor Python determinístico

2. **search_kb**: Usar para búsquedas complejas
   - Cuando la KB local no tenga resultado
   - Para validación cruzada

3. **checkStock**: Usar cuando el cliente pregunte por disponibilidad
   - Siempre aclarar que el stock es "sujeto a confirmación"

4. **getProductPrice**: Usar para verificar precios actualizados
   - Si difiere del JSON, reportar ambos precios
   - Usar el precio de la API como más actualizado

## Fallback si Action falla

1. Usar datos de Knowledge Base (Nivel 1)
2. Informar al usuario: "No pude verificar en tiempo real, usando datos de base de datos"
3. Recomendar contactar a BMC para confirmar

## Rate Limits

- No hacer más de 10 llamadas a Actions por conversación
- Cachear mentalmente resultados durante la sesión
```

---

## 11. Troubleshooting

### 11.1 Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| "Failed to fetch" | Servidor no responde | Verificar que el servidor esté activo |
| "Invalid schema" | Schema OpenAPI malformado | Validar con [editor.swagger.io](https://editor.swagger.io) |
| "401 Unauthorized" | API Key incorrecta | Verificar configuración de autenticación |
| "CORS error" | Headers no configurados | Agregar headers CORS en el servidor |
| "Timeout" | Servidor muy lento | Optimizar backend, reducir payload |
| "SSL error" | Certificado inválido | Usar certificado SSL válido |

### 11.2 Debugging

**En GPT Builder**:
1. Usar el botón "Test" al crear la Action
2. Revisar logs de respuesta
3. Verificar que los parámetros se extraigan correctamente

**En el Backend**:
```python
# Agregar logging detallado
import logging
logging.basicConfig(level=logging.DEBUG)

@app.before_request
def log_request():
    logging.debug(f"Request: {request.method} {request.path}")
    logging.debug(f"Headers: {dict(request.headers)}")
    logging.debug(f"Body: {request.get_data()}")

@app.after_request
def log_response(response):
    logging.debug(f"Response: {response.status_code}")
    return response
```

### 11.3 Validación de Schema

Usar [Swagger Editor](https://editor.swagger.io) para validar el schema antes de pegar en GPT Builder.

---

## 12. Recursos y Referencias

### 12.1 Documentación Oficial

- [OpenAI GPT Actions](https://platform.openai.com/docs/actions)
- [OpenAPI Specification 3.0](https://swagger.io/specification/)
- [OpenAPI Specification 3.1](https://spec.openapis.org/oas/v3.1.0)

### 12.2 Herramientas

| Herramienta | Uso | URL |
|-------------|-----|-----|
| Swagger Editor | Editar/validar schemas | [editor.swagger.io](https://editor.swagger.io) |
| Postman | Probar APIs | [postman.com](https://www.postman.com) |
| Insomnia | Alternativa a Postman | [insomnia.rest](https://insomnia.rest) |
| ngrok | Exponer localhost a internet | [ngrok.com](https://ngrok.com) |

### 12.3 Frameworks para Backend

| Framework | Lenguaje | Pros |
|-----------|----------|------|
| FastAPI | Python | Auto-genera OpenAPI, async, rápido |
| Flask | Python | Simple, flexible, bien documentado |
| Express | Node.js | Ecosystem amplio, fácil deployment |
| Hono | Node.js/Bun | Ultra-ligero, edge-ready |

### 12.4 Hosting Recomendado

| Servicio | Tipo | Costo | Ideal para |
|----------|------|-------|------------|
| Vercel | Serverless | Gratis (límites) | APIs simples |
| Railway | Container | ~$5/mes | APIs Python |
| Fly.io | Container | Gratis (límites) | Bajo latency |
| AWS Lambda | Serverless | Pay-per-use | Alto volumen |
| DigitalOcean | VPS | $5+/mes | Control total |

---

## 📋 Resumen Ejecutivo

### ¿Qué son las Actions?
Integraciones con APIs externas que permiten a un GPT realizar operaciones en tiempo real más allá de generar texto.

### ¿Cuándo usarlas?
- Necesitas datos en tiempo real (precios, stock)
- Quieres guardar datos (cotizaciones, leads)
- Requieres cálculos determinísticos garantizados
- Necesitas integrar con servicios externos (email, WhatsApp)

### ¿Cuándo NO usarlas?
- Los datos son estáticos → Usar Knowledge Base
- Solo necesitas buscar en internet → Usar Web Browsing
- Solo necesitas cálculos locales → Usar Code Interpreter

### Próximos pasos para Panelin
1. **Corto plazo**: Seguir con Knowledge Base + Code Interpreter
2. **Mediano plazo**: Implementar backend con `calculate_quote`
3. **Largo plazo**: Agregar integraciones Shopify, email, CRM

---

**Documento creado**: 2026-01-26  
**Versión**: 2.0 Comprehensive  
**Autor**: AI Configuration Analyst  
**Basado en**: Documentación OpenAI + Configuración actual Panelin
