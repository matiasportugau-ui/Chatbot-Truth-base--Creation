# Checklist de Verificación: GPT Panelin Configurado

## ✅ Verificación Básica

### 1. Configuración General
- [ ] **Nombre**: "Panelin - BMC Assistant Pro" o similar
- [ ] **Descripción**: Menciona experto técnico en cotizaciones
- [ ] **Instrucciones del Sistema**: Pegadas correctamente
- [ ] **Modelo**: GPT-4 o superior (preferible GPT-5.2 Thinking si disponible)

### 2. Knowledge Base (7 archivos)
- [ ] `BMC_Base_Conocimiento_GPT.json` ⭐ (MASTER - debe estar primero)
- [ ] `BMC_Base_Unificada_v4.json`
- [ ] `BMC_Catalogo_Completo_Shopify (1).json`
- [ ] `panelin_truth_bmcuruguay_web_only_v2.json`
- [ ] `panelin_context_consolidacion_sin_backend.md`
- [ ] `Aleros.rtf` (o convertido a .txt/.md)
- [ ] `panelin_truth_bmcuruguay_catalog_v2_index.csv`

### 3. Capacidades Habilitadas
- [ ] **Web Browsing** ✅ (para verificar precios)
- [ ] **Code Interpreter** ✅ (para PDFs y cálculos)
- [ ] **Image Generation** (opcional)

---

## 🧪 Tests de Funcionalidad

### Test 1: Personalización por Usuario

**Prueba con cada usuario:**

```
Conversación nueva → "Hola"
```

**Resultado esperado:**
- [ ] Pregunta el nombre del usuario
- [ ] Si es "Mauro": Respuesta personalizada (siempre distinta)
- [ ] Si es "Martin": Respuesta personalizada (siempre distinta)
- [ ] Si es "Rami": Respuesta personalizada (siempre distinta)

---

### Test 2: Source of Truth (Nivel 1)

```
Usuario: "¿Cuánto cuesta ISODEC 100mm?"
```

**Resultado esperado:**
- [ ] Lee `BMC_Base_Conocimiento_GPT.json`
- [ ] Responde: **$46.07** (precio exacto del JSON)
- [ ] NO inventa precio
- [ ] Menciona que viene de la fuente maestra

**Si falla:**
- Reforzar en instrucciones: "ANTES de dar precio, LEE SIEMPRE BMC_Base_Conocimiento_GPT.json"

---

### Test 3: Validación Técnica (Autoportancia)

```
Usuario: "Necesito ISODEC 100mm para 7m de luz"
```

**Resultado esperado:**
- [ ] Detecta que NO cumple (autoportancia 5.5m < 7m)
- [ ] Sugiere 150mm o 200mm
- [ ] Explica por qué: "Para 7m necesitas mínimo 150mm (autoportancia 7.5m)"
- [ ] Consulta autoportancia del JSON

---

### Test 4: Cotización Completa

```
Usuario: "Cotizar ISODEC 100mm, 5m de luz, 4 paneles, fijación a metal"
```

**Resultado esperado:**
- [ ] Valida autoportancia (5.5m > 5m ✓)
- [ ] Calcula apoyos: ROUNDUP((5/5.5)+1) = 2
- [ ] Calcula puntos fijación: [fórmula compleja]
- [ ] Calcula varillas: ROUNDUP(puntos/4)
- [ ] Calcula tuercas: puntos * 2 (metal)
- [ ] Precio unitario: $46.07
- [ ] Subtotal + IVA (22%)
- [ ] Desglose completo

**Verificar fórmulas:**
- [ ] Usa fórmulas de `formulas_cotizacion` del JSON
- [ ] Redondea correctamente (ROUNDUP)
- [ ] No inventa fórmulas

---

### Test 5: Comandos SOP

```
Usuario: "/estado"
```

**Resultado esperado:**
- [ ] Reconoce el comando
- [ ] Muestra resumen del Ledger
- [ ] Indica riesgo de contexto (bajo/medio/alto)
- [ ] Da recomendación si aplica

```
Usuario: "/checkpoint"
```

**Resultado esperado:**
- [ ] Exporta LEDGER_SNAPSHOT.md
- [ ] Exporta DELTAS_SIN_MERGE.jsonl
- [ ] Entrega en formato texto (bloques markdown/json)

---

### Test 6: Guardrails (No Inventar Datos)

```
Usuario: "¿Cuánto cuesta ISODEC 300mm?"
```

**Resultado esperado:**
- [ ] Busca en JSON
- [ ] NO encuentra 300mm (no existe)
- [ ] Responde: "No tengo esa información en mi base de conocimiento"
- [ ] Sugiere espesores disponibles: 100mm, 150mm, 200mm, 250mm
- [ ] NO inventa precio

---

### Test 7: Resolución de Conflictos

Si hay diferencia entre archivos:

**Resultado esperado:**
- [ ] Usa Nivel 1 (BMC_Base_Conocimiento_GPT.json)
- [ ] Reporta diferencia: "Nota: Hay una diferencia con otra fuente, usando el precio de la fuente maestra"
- [ ] NO usa Nivel 2 para respuesta directa

---

### Test 8: Generación de PDF

```
Usuario: "Genera un PDF de esta cotización"
```

**Resultado esperado:**
- [ ] Usa Code Interpreter
- [ ] Crea script Python con reportlab
- [ ] Genera PDF con datos de la conversación
- [ ] Ofrece descarga

---

## 🔍 Verificación de Instrucciones

### Instrucciones Críticas que DEBEN estar:

1. **Source of Truth**:
   ```
   ANTES de dar un precio, LEE SIEMPRE BMC_Base_Conocimiento_GPT.json
   ```

2. **Jerarquía de Fuentes**:
   ```
   NIVEL 1 - MASTER: BMC_Base_Conocimiento_GPT.json
   → SIEMPRE usar este archivo primero
   ```

3. **Guardrails**:
   ```
   NO inventes precios ni espesores que no estén en ese JSON
   ```

4. **Personalización**:
   ```
   Si se llama Mauro: [instrucción]
   Si es Martin: [instrucción]
   Si es Rami: [instrucción]
   ```

5. **Fórmulas**:
   ```
   Usar EXCLUSIVAMENTE las fórmulas de "formulas_cotizacion" en BMC_Base_Conocimiento_GPT.json
   ```

---

## ⚠️ Problemas Comunes y Soluciones

### Problema 1: Inventa Precios

**Síntoma**: Panelin da precios que no están en el JSON

**Solución**:
1. Reforzar en instrucciones: "NUNCA dar precio sin leer JSON primero"
2. Agregar guardrail más estricto
3. Probar con: "¿Cuánto cuesta X?" y verificar que lea archivo

---

### Problema 2: No Aplica Personalización

**Síntoma**: No reconoce usuarios específicos (Mauro, Martin, Rami)

**Solución**:
1. Verificar que instrucciones de personalización estén claras
2. Probar iniciando conversación nueva
3. Asegurar que pregunta el nombre al inicio

---

### Problema 3: No Lee el Archivo Correcto

**Síntoma**: Usa fuente secundaria en lugar de Nivel 1

**Solución**:
1. Verificar que `BMC_Base_Conocimiento_GPT.json` esté subido primero
2. Reforzar jerarquía en instrucciones
3. Agregar ejemplo: "Para precios, SIEMPRE consultar BMC_Base_Conocimiento_GPT.json primero"

---

### Problema 4: Fórmulas Incorrectas

**Síntoma**: Cálculos no coinciden con fórmulas del JSON

**Solución**:
1. Verificar que use fórmulas de `formulas_cotizacion`
2. Agregar ejemplo de cálculo en instrucciones
3. Probar con caso conocido y comparar resultado

---

### Problema 5: No Reconoce Comandos SOP

**Síntoma**: `/estado`, `/checkpoint`, `/consolidar` no funcionan

**Solución**:
1. Verificar que `panelin_context_consolidacion_sin_backend.md` esté subido
2. Reforzar en instrucciones: "Reconoce estos comandos literales"
3. Probar cada comando individualmente

---

## 📊 Métricas de Calidad

### Precisión
- [ ] % de respuestas que usan fuente correcta (Nivel 1) > 95%
- [ ] % de cotizaciones con fórmulas correctas > 98%
- [ ] % de conflictos detectados y resueltos = 100%

### Completitud
- [ ] % de consultas respondidas sin "no sé" innecesario > 90%
- [ ] Cobertura de productos en KB > 95%

### Eficiencia
- [ ] Tiempo de respuesta promedio < 30 segundos
- [ ] Tasa de uso de cache > 50% (si implementado)

---

## 🔧 Optimizaciones Recomendadas

### Si Panelin funciona bien:

1. **Agregar Actions** (opcional):
   - Shopify API para precios en tiempo real
   - Ver `Guia_Actions_Panelin.md`

2. **Mejorar Caching**:
   - Cachear consultas frecuentes
   - Invalidar cuando se actualiza KB

3. **Monitoreo**:
   - Trackear consultas más frecuentes
   - Identificar gaps de información
   - Mejorar KB basado en uso real

### Si Panelin tiene problemas:

1. **Revisar Instrucciones**:
   - Simplificar si son muy largas
   - Enfocar en lo crítico
   - Agregar ejemplos específicos

2. **Reorganizar KB**:
   - Verificar que archivos estén bien formateados
   - Eliminar duplicados
   - Asegurar que Nivel 1 esté completo

3. **Probar Incrementalmente**:
   - Empezar con configuración mínima
   - Agregar complejidad gradualmente
   - Probar cada cambio

---

## 📝 Checklist Final

Antes de considerar el GPT "listo para producción":

- [ ] ✅ Todos los tests pasan
- [ ] ✅ Source of truth funciona correctamente
- [ ] ✅ Personalización funciona
- [ ] ✅ Cotizaciones son precisas
- [ ] ✅ Guardrails previenen inventar datos
- [ ] ✅ Comandos SOP funcionan
- [ ] ✅ PDF generation funciona
- [ ] ✅ Instrucciones están optimizadas
- [ ] ✅ KB está completa y actualizada
- [ ] ✅ Documentación está clara

---

## 🆘 Si Necesitas Ayuda

Si algo no funciona:

1. **Revisa los logs**: ¿Qué archivo está leyendo?
2. **Prueba casos simples**: Empezar con "¿Cuánto cuesta X?"
3. **Verifica instrucciones**: ¿Están claras y completas?
4. **Compara con ejemplos**: ¿Hay casos que sí funcionan?

**Recursos**:
- `Guia_Crear_GPT_OpenAI_Panelin.md` - Guía completa
- `Instrucciones_Sistema_Panelin_CopiarPegar.txt` - Instrucciones listas
- `Arquitectura_Ideal_GPT_Panelin.md` - Arquitectura de referencia

---

**Última actualización**: 2026-01-16
**Versión**: 1.0
