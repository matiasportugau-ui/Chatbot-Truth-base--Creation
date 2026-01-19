# Guía Completa: Actions (Acciones/APIs) para Panelin

## ¿Qué son las Actions?

Las **Actions** son integraciones con APIs externas que permiten que tu GPT realice acciones automatizadas más allá de solo responder. Por ejemplo:
- Consultar precios en tiempo real desde Shopify
- Verificar stock actualizado
- Enviar cotizaciones por WhatsApp o Email
- Guardar cotizaciones en una base de datos
- Generar órdenes automáticamente

---

## 🎯 Actions Recomendadas para Panelin

### 1. Shopify API (ALTA PRIORIDAD) ⭐

**¿Para qué?**
- Verificar precios actualizados en tiempo real
- Consultar stock disponible
- Obtener variantes de productos (espesores, colores)
- Validar disponibilidad antes de cotizar

**¿Vale la pena?**
✅ **SÍ** - Es la más útil porque:
- Los precios pueden cambiar
- El stock puede agotarse
- Hay múltiples variantes por producto
- Mejora la precisión de las cotizaciones

---

### 2. WhatsApp Business API (MEDIA PRIORIDAD)

**¿Para qué?**
- Enviar cotizaciones directamente al cliente
- Notificar cuando una cotización está lista
- Enviar recordatorios de seguimiento

**¿Vale la pena?**
⚠️ **DEPENDE** - Útil si:
- Quieres automatizar el envío de cotizaciones
- Tienes muchos clientes
- Quieres mejorar la experiencia del cliente

---

### 3. Email API (BAJA PRIORIDAD)

**¿Para qué?**
- Enviar PDFs de cotizaciones por email
- Enviar confirmaciones
- Enviar resúmenes

**¿Vale la pena?**
⚠️ **OPCIONAL** - Similar a WhatsApp pero menos inmediato

---

### 4. Base de Datos API (MEDIA PRIORIDAD)

**¿Para qué?**
- Guardar historial de cotizaciones
- Trackear conversiones
- Analizar patrones de venta

**¿Vale la pena?**
✅ **ÚTIL** - Si quieres:
- Analizar qué productos se cotizan más
- Mejorar el sistema con datos históricos
- Trackear efectividad

---

## 🚀 Cómo Configurar Actions en OpenAI

### Paso 1: Acceder a la Configuración de Actions

1. Ve a tu GPT en [chatgpt.com/gpts/editor](https://chatgpt.com/gpts/editor)
2. Selecciona tu GPT "Panelin"
3. Ve a la pestaña **"Configure"**
4. Desplázate hasta la sección **"Actions"**
5. Haz clic en **"Create new action"**

---

### Paso 2: Configurar Shopify API Action

#### 2.1 Obtener Credenciales de Shopify

**Opción A: Shopify Admin API (Recomendado)**
1. Ve a tu tienda Shopify: [bmcuruguay.com.uy/admin](https://bmcuruguay.com.uy/admin)
2. Ve a **Settings** → **Apps and sales channels** → **Develop apps**
3. Crea una nueva app
4. Configura permisos:
   - `read_products` - Para leer productos
   - `read_product_listings` - Para leer listados
   - `read_inventory` - Para leer stock (opcional)
5. Instala la app y copia:
   - **API Key** (Client ID)
   - **API Secret Key** (Client Secret)
   - **Store URL**: `bmcuruguay.myshopify.com` o `bmcuruguay.com.uy`

**Opción B: Shopify Storefront API (Más simple, menos permisos)**
- Solo lectura pública
- No requiere autenticación compleja
- Limitado a datos públicos

#### 2.2 Crear el Schema OpenAPI

En el editor de Actions, pega este schema:

```yaml
openapi: 3.1.0
info:
  title: Shopify Product API
  description: API para consultar productos, precios y stock de BMC Uruguay
  version: 1.0.0
servers:
  - url: https://bmcuruguay.com.uy
    description: BMC Uruguay Shopify Store

paths:
  /admin/api/2024-01/products.json:
    get:
      summary: Obtener productos de Shopify
      description: Consulta productos, precios y variantes desde Shopify Admin API
      operationId: getProducts
      parameters:
        - name: handle
          in: query
          description: Handle del producto (ej: isodec-eps-techo)
          required: false
          schema:
            type: string
        - name: product_type
          in: query
          description: Tipo de producto (ej: Panel Aislante)
          required: false
          schema:
            type: string
        - name: limit
          in: query
          description: Límite de resultados (máx 250)
          required: false
          schema:
            type: integer
            default: 50
      security:
        - ShopifyAdminAPI: []
      responses:
        '200':
          description: Lista de productos
          content:
            application/json:
              schema:
                type: object
                properties:
                  products:
                    type: array
                    items:
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
                              inventory_quantity:
                                type: integer
                              option1:
                                type: string
                              option2:
                                type: string

  /admin/api/2024-01/products/{product_id}.json:
    get:
      summary: Obtener producto específico
      description: Obtiene detalles completos de un producto por ID
      operationId: getProductById
      parameters:
        - name: product_id
          in: path
          required: true
          description: ID del producto en Shopify
          schema:
            type: integer
      security:
        - ShopifyAdminAPI: []
      responses:
        '200':
          description: Detalles del producto
          content:
            application/json:
              schema:
                type: object

components:
  securitySchemes:
    ShopifyAdminAPI:
      type: http
      scheme: basic
      description: Autenticación básica con API Key y Secret
```

#### 2.3 Configurar Autenticación

En la sección **"Authentication"**:

1. Selecciona **"HTTP (Basic)"** o **"API Key"**
2. Para **HTTP Basic**:
   - **Username**: Tu API Key de Shopify
   - **Password**: Tu API Secret Key
3. Para **API Key**:
   - **Header name**: `X-Shopify-Access-Token`
   - **API Key**: Tu Access Token

**Nota de Seguridad**: 
- ⚠️ **NUNCA** compartas estas credenciales públicamente
- Usa variables de entorno si es posible
- Considera usar un servicio intermedio (proxy) para mayor seguridad

#### 2.4 Configurar Privacy Policy

Si tu Action accede a datos de clientes, necesitas:
- URL de Privacy Policy
- Descripción de qué datos se acceden

---

### Paso 3: Actualizar Instrucciones del Sistema

Agrega estas instrucciones a tu GPT:

```
# USO DE SHOPIFY API (Action)

Cuando necesites verificar precios o stock actualizado:

1. PRIMERO: Consulta BMC_Base_Conocimiento_GPT.json (Nivel 1)
2. SI el usuario pregunta por precio actualizado o stock:
   → Usa la Action "getProducts" o "getProductById"
   → Compara con el precio del JSON
   → Si hay diferencia, usa el precio de Shopify (más actualizado)
   → Reporta: "Precio en Shopify: $X (vs $Y en base de datos)"

3. SI el usuario pregunta por disponibilidad:
   → Usa la Action para verificar inventory_quantity
   → Informa: "Stock disponible: X unidades" o "Agotado"

4. SI hay error en la API:
   → Usa el precio del JSON (Nivel 1)
   → Informa: "No pude verificar precio actualizado, usando precio de base de datos"
```

---

## 📋 Schema Simplificado (Alternativa Más Fácil)

Si la configuración completa es muy compleja, aquí hay una versión simplificada usando Storefront API (pública):

```yaml
openapi: 3.1.0
info:
  title: Shopify Storefront API
  version: 1.0.0
servers:
  - url: https://bmcuruguay.com.uy/api/2024-01/graphql.json

paths:
  /api/2024-01/graphql.json:
    post:
      summary: Consultar productos via GraphQL
      operationId: queryProducts
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: string
                  example: |
                    {
                      products(first: 10, query: "handle:isodec-eps-techo") {
                        edges {
                          node {
                            id
                            title
                            handle
                            variants(first: 10) {
                              edges {
                                node {
                                  id
                                  price
                                  availableForSale
                                }
                              }
                            }
                          }
                        }
                      }
                    }
      responses:
        '200':
          description: Respuesta GraphQL
          content:
            application/json:
              schema:
                type: object
```

---

## 🧪 Cómo Probar las Actions

### Test 1: Verificar Precio Actualizado

```
Usuario: "¿Cuánto cuesta ISODEC 100mm ahora en Shopify?"

Panelin debe:
1. Leer precio de JSON: $46.07
2. Llamar Action getProducts con handle="isodec-eps-techo"
3. Comparar precios
4. Responder con precio actualizado si hay diferencia
```

### Test 2: Verificar Stock

```
Usuario: "¿Hay stock de ISOROOF PLUS?"

Panelin debe:
1. Llamar Action getProducts
2. Verificar inventory_quantity
3. Informar disponibilidad
```

---

## ⚠️ Consideraciones Importantes

### Seguridad

1. **Credenciales**:
   - ⚠️ NUNCA compartas API keys públicamente
   - Usa variables de entorno si es posible
   - Considera usar un proxy/intermediario

2. **Rate Limits**:
   - Shopify tiene límites de requests
   - Implementa caching cuando sea posible
   - No abuses de las llamadas

3. **Datos Sensibles**:
   - Solo accede a datos necesarios
   - Respeta privacidad de clientes

### Costos

- **Shopify API**: Generalmente gratis hasta cierto límite
- **WhatsApp API**: Puede tener costos por mensaje
- **Email API**: Generalmente gratis o muy barato

### Alternativas Sin Actions

Si no quieres configurar Actions, puedes:

1. **Usar Web Browsing**:
   - Panelin puede navegar a bmcuruguay.com.uy
   - Leer precios directamente de la web
   - Menos preciso pero más simple

2. **Actualizar JSON Manualmente**:
   - Actualizar `BMC_Base_Conocimiento_GPT.json` periódicamente
   - Subir nuevo archivo al GPT
   - Más trabajo pero más control

---

## 🎯 Recomendación Final

### Para Empezar (Fase 1):

**NO configures Actions todavía** si:
- ✅ Tu JSON está actualizado
- ✅ No necesitas verificación en tiempo real
- ✅ Prefieres simplicidad

**SÍ configura Actions** si:
- ✅ Los precios cambian frecuentemente
- ✅ Necesitas verificar stock en tiempo real
- ✅ Quieres automatizar envío de cotizaciones

### Para Escalar (Fase 2):

1. **Shopify API** (Prioridad 1)
   - Mayor impacto en precisión
   - Mejora experiencia del usuario

2. **WhatsApp/Email API** (Prioridad 2)
   - Automatiza envío
   - Mejora seguimiento

3. **Base de Datos API** (Prioridad 3)
   - Analítica y mejora continua

---

## 📝 Checklist de Configuración

- [ ] Decidir qué Actions necesitas
- [ ] Obtener credenciales de APIs (Shopify, etc.)
- [ ] Crear schema OpenAPI
- [ ] Configurar autenticación
- [ ] Actualizar instrucciones del sistema
- [ ] Probar cada Action
- [ ] Documentar uso para Panelin
- [ ] Configurar privacy policy si aplica
- [ ] Monitorear uso y costos

---

## 🔗 Recursos Útiles

- [OpenAI Actions Documentation](https://platform.openai.com/docs/actions)
- [Shopify Admin API](https://shopify.dev/docs/api/admin)
- [Shopify Storefront API](https://shopify.dev/docs/api/storefront)
- [OpenAPI Specification](https://swagger.io/specification/)

---

## 💡 Ejemplo Completo: Action de Shopify Simplificada

Si quieres empezar con algo simple, aquí tienes un ejemplo mínimo funcional:

```yaml
openapi: 3.1.0
info:
  title: BMC Shopify Products
  version: 1.0.0
servers:
  - url: https://bmcuruguay.com.uy

paths:
  /products/{handle}.json:
    get:
      summary: Obtener producto por handle
      operationId: getProductByHandle
      parameters:
        - name: handle
          in: path
          required: true
          schema:
            type: string
          example: isodec-eps-techo
      responses:
        '200':
          description: Producto encontrado
          content:
            application/json:
              schema:
                type: object
```

**Nota**: Este ejemplo usa la API pública de Shopify que no requiere autenticación pero tiene limitaciones.

---

¿Necesitas ayuda configurando alguna Action específica? Puedo ayudarte a crear el schema exacto para tu caso.
