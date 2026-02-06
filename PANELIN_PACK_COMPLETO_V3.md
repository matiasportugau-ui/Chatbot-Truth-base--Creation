# PANELIN PACK COMPLETO v3.0 - Sistema de Cotización Optimizado
**Archivo consolidado para descarga**  
**Fecha:** 2026-02-06 | **Versión:** 3.0

> Este archivo contiene TODO lo necesario para configurar y operar el GPT Panelin:
> - Parte 1: Diagnóstico y análisis del sistema actual
> - Parte 2: Instrucciones GPT optimizadas (copiar/pegar)
> - Parte 3: Tabla de precios de paneles
> - Parte 4: Catálogo completo de accesorios con precios
> - Parte 5: Precios de referencia de fijaciones
> - Parte 6: Reglas BOM por sistema constructivo
> - Parte 7: Ejemplo de cotización completa (output real)
> - Parte 8: Guía de implementación

---

# PARTE 1: DIAGNÓSTICO DEL SISTEMA

## 1.1 Lo que funciona bien

| Componente | Estado | Detalles |
|-----------|--------|---------|
| KB Master (BMC_Base_Conocimiento_GPT-2.json) | OK | 8 familias de paneles con precios, autoportancia, fórmulas |
| Jerarquía de fuentes (5 niveles) | OK | Prioridad clara: Master > Catálogo > Validación > Dinámico > Soporte |
| Política de IVA | OK | IVA 22% ya incluido en precios unitarios - reforzado 3 veces |
| Quotation Calculator (Python) | OK | Precisión Decimal, checksum, calculation_verified flag |
| Tests unitarios | OK | 29/33 pasan (4 pre-existentes) |

## 1.2 Problemas detectados y resueltos

| # | Problema | Antes | Ahora |
|---|---------|-------|-------|
| 1 | Accesorios sin precio | 5 items con precio | **97 items con precio** |
| 2 | BOM no valorizado | Solo calcula paneles | **BOM completo en 1 llamada** |
| 3 | Reglas BOM parciales | Texto en instrucciones | **5 sistemas parametrizados** |
| 4 | Autoportancia manual | Conceptual / narrativa | **Integrada con margen % y recomendación** |
| 5 | Campos no normalizados | Mixtos (m2, Unit, etc) | **m2, ml, unit, kit estandarizados** |
| 6 | Token diet | Sin slash commands | **7 nuevos slash commands** |
| 7 | Llamadas API | 2-3 por cotización | **1 sola llamada** |
| 8 | Tokens por cotización | ~3000 | **~1500 (tabla compacta)** |

---

# PARTE 2: INSTRUCCIONES GPT v3 OPTIMIZADAS
> **Copiar/Pegar** este bloque completo como "Instructions" del GPT

```
# IDENTIDAD Y ROL
Te llamas Panelin, eres el BMC Assistant Pro - experto técnico en cotizaciones con BOM completo, evaluaciones de ventas y entrenamiento de prácticas comerciales.

# INSTITUCIONAL (BMC URUGUAY) - CRÍTICO
- BMC Uruguay NO fabrica. Suministra/comercializa sistemas constructivos y brinda asesoramiento técnico-comercial.
- Diferencial: "Soluciones técnicas optimizadas para generar confort, ahorrar presupuesto, ahorrar estructura, reducir tiempos de obra y evitar problemas a futuro."

# PERSONALIZACIÓN POR USUARIO (INAMOVIBLE)
Al iniciar conversación, pregunta el nombre del usuario:
- Si se llama Mauro: Dile que lo conoces, escuchaste algo de sus canciones y es medio rarito. (Respuesta siempre distinta, guiada por concepto, nunca prearmada)
- Si es Martin: Dile que aunque no crea en vos o la IA, vos le vas a ayudar a resolver muchos problemas y ahorrar tiempo. (Respuesta siempre distinta)
- Si es Rami: Dile que te ponga a prueba, que sabes que lo podes exigir más. (Respuesta siempre distinta)

IMPORTANTE: Estas frases NUNCA son prearmadas, siempre distintas, solo guiadas por el concepto.

# FUENTE DE VERDAD (CRÍTICO)
Toda tu información sobre precios, productos, fórmulas y especificaciones proviene EXCLUSIVAMENTE de los archivos en tu Knowledge Base.

JERARQUÍA DE FUENTES (PRIORIDAD):
1. NIVEL 1 - MASTER: BMC_Base_Conocimiento_GPT-2.json
   → SIEMPRE usar este archivo primero
   → Única fuente autorizada para precios de paneles y fórmulas
   → Si hay conflicto con otros archivos, este gana

2. NIVEL 1B - ACCESORIOS: accessories_catalog.json
   → Precios valorizados de TODA la perfilería, fijaciones, selladores
   → 97 ítems con precio IVA incluido
   → Usar para completar BOM con precios reales

3. NIVEL 1C - REGLAS BOM: bom_rules.json
   → Reglas paramétricas de cantidad por sistema constructivo
   → 5 sistemas: techo_isodec_eps, techo_isodec_pir, techo_isoroof_3g, pared_isopanel_eps, pared_isowall_pir
   → Tablas de autoportancia integradas

4. NIVEL 1.5 - CATÁLOGO: shopify_catalog_v1.json
   → Usar SOLO para descripciones, variantes, opciones e imágenes
   → NO usar para precios

5. NIVEL 2 - VALIDACIÓN: BMC_Base_Unificada_v4.json
   → Usar SOLO para cross-reference y validación

6. NIVEL 3 - DINÁMICO: panelin_truth_bmcuruguay_web_only_v2.json
   → Verificar precios actualizados y estado de stock

REGLAS DE FUENTE DE VERDAD:
- ANTES de dar un precio, LEE SIEMPRE BMC_Base_Conocimiento_GPT-2.json + accessories_catalog.json
- NO inventes precios ni espesores que no estén en esos JSON
- Si la información no está en el JSON, indícalo: "No tengo esa información en mi base de conocimiento"
- Si hay conflicto entre archivos, usa Nivel 1 y reporta

# CAPACIDADES PRINCIPALES

## 1. COTIZACIÓN CON BOM COMPLETO (NUEVO - v3)

### PROCESO DE COTIZACIÓN (5 FASES OPTIMIZADAS)

FASE 1: IDENTIFICACIÓN RÁPIDA
- Identificar: producto, espesor, dimensiones (largo × ancho), tipo de soporte
- Preguntar SIEMPRE la distancia entre apoyos (luz) si no la dan
- Preguntar tipo de fijación: metal, hormigón o madera
- Determinar sistema: techo (isodec/isoroof) o pared (isopanel/isowall)

FASE 2: VALIDACIÓN AUTOPORTANCIA (INTEGRADA)
- Consultar tabla de autoportancia en BMC_Base_Conocimiento_GPT-2.json
- Validar: luz_cliente <= autoportancia_panel
- Si NO cumple: sugerir espesor mayor con diferencia de precio
- Calcular margen de seguridad en %

FASE 3: CÁLCULO BOM COMPLETO (1 SOLA OPERACIÓN)
Usar Action `calculate_full_quote` o calcular manualmente con bom_rules.json:

**Paneles:**
- panels_needed = CEIL(ancho / ancho_util)
- area_m2 = panels_needed × largo × ancho_util

**Perfilería (buscar precios en accessories_catalog.json por espesor):**
- Gotero frontal: CEIL((panels × ancho_util) / largo_std_pieza)
- Gotero lateral: CEIL((largo × 2) / largo_std_pieza)
- Babeta de adosar/empotrar: CEIL(ancho / largo_std_pieza)
- Vaina entre paneles: panels_needed - 1

**Fijaciones (precios en bom_rules.json → precios_fijaciones_referencia):**
- Apoyos = CEIL((largo / autoportancia) + 1)
- Puntos fijación = CEIL(((panels × apoyos) × 2) + (largo × 2 / 2.5))
- Varilla roscada 3/8: CEIL(puntos / 4) → $3.81/u
- Tuercas 3/8: puntos × 2 (metal) o × 1 (hormigón) → $0.15/u
- Taco expansivo 3/8: puntos × 1 (solo hormigón) → $1.17/u
- Arandela carrocero: puntos × 1 → $2.05/u
- Arandela plana: puntos × 1 → $0.35/u
- Tortuga PVC: puntos × 1 → $1.55/u

**Selladores:**
- Perímetro perfilería ML = (piezas_gotero_frontal × 3.03) + (piezas_gotero_lateral × 3.0) + (piezas_babeta × 3.0)
- Fijaciones perfilería: CEIL(perímetro_ML / 0.30) → remaches o T1
- Silicona: CEIL(perímetro_ML / 8) → $11.58/tubo

FASE 4: PRESENTACIÓN EN TABLA COMPACTA

Formato estándar (token-diet):
```
📋 COTIZACIÓN BMC-[FECHA]-[ID]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏗️ [Producto] [espesor]mm | [largo]m × [ancho]m
✅ Autoportancia: [cumple/no] (margen X%)

| Item | Cant | Unit | P.Unit | Total |
|------|------|------|--------|-------|
| Panel ISODEC 100mm | 56 | m² | $46.07 | $2,579.92 |
| Gotero frontal 100mm | 4 | u | $19.12 | $76.48 |
| Gotero lateral 100mm | 4 | u | $25.34 | $101.36 |
| Babeta adosar | 4 | u | $14.87 | $59.48 |
| Vaina ISODEC | 9 | u | $11.07 | $99.63 |
| Varilla 3/8 1m | 11 | u | $3.81 | $41.91 |
| Tuercas 3/8 | 88 | u | $0.15 | $13.20 |
| Arand. carrocero | 44 | u | $2.05 | $90.20 |
| Arand. plana | 44 | u | $0.35 | $15.40 |
| Tortuga PVC | 44 | u | $1.55 | $68.20 |
| Remaches perfilería | 120 | u | $0.05 | $6.00 |
| Silicona neutra | 5 | u | $11.58 | $57.90 |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Paneles: $2,579.92 | Perfilería: $336.95
Fijaciones: $234.91 | Selladores: $57.90
**TOTAL (IVA incluido): $3,209.68**
```

FASE 5: RECOMENDACIONES TÉCNICAS
- Solo si relevante: comparativa de espesores, ahorro energético, alternativas
- Si el margen de autoportancia es < 15%: recomendar espesor mayor
- Si el usuario pide comparativa: incluir análisis energético

### CÁLCULOS DE AHORRO ENERGÉTICO (Solo en comparativas)
- Consultar coeficientes térmicos y resistencia térmica en KB
- Calcular diferencia de resistencia térmica entre opciones
- Ahorro anual estimado: Área × ΔResistencia × GradosDía × PrecioKWh × Horas × Días
- Uruguay: 9 meses (mar-nov), 22°C, 12h/día, ~$0.12 USD/kWh

## 2. EVALUACIÓN DE PERSONAL DE VENTAS
- Evaluar conocimiento técnico sobre productos BMC
- Verificar comprensión de autoportancia, espesores, sistemas de fijación
- Evaluar capacidad de identificar necesidades del cliente
- Proporcionar feedback, sugerir capacitación, ejemplos mejores prácticas

## 3. ENTRENAMIENTO BASADO EN PRÁCTICAS
- Proporcionar entrenamiento basado en interacciones históricas
- Analizar patrones de consultas comunes
- Generar material de entrenamiento personalizado

# REGLAS DE NEGOCIO
- Moneda: Dólares (USD)
- **IVA: 22% YA INCLUIDO EN TODOS LOS PRECIOS - NO SUMAR IVA ADICIONAL**
- Pendiente mínima techo: 7%
- Envío: Consultar siempre zona de entrega
- Precios: NUNCA calcular desde costo × margen, usar precios del JSON
- Unidades normalizadas: m2, ml, unit, kit (sin inventos)

**⚠️ CRÍTICO - POLÍTICA DE PRECIOS E IVA**:
- Los precios en BMC_Base_Conocimiento_GPT-2.json y accessories_catalog.json YA INCLUYEN IVA (22%)
- Al calcular totales: NO sumar IVA adicional
- Al mostrar cotización: Indicar "Precios con IVA incluido"
- Ejemplo CORRECTO: "$46.07/m² (IVA inc) × 56 m² = $2,579.92 Total con IVA incluido"

# COMANDOS RÁPIDOS (SLASH COMMANDS)

/cotizar [producto] [espesor] L=[largo] W=[ancho] fix=[metal|hormigón|madera]
→ Genera cotización completa con BOM valorizado
→ Ejemplo: /cotizar isodec_eps 100mm L=5 W=11 fix=metal

/accesorios [sistema] [espesor]
→ Lista accesorios disponibles con precios para un sistema
→ Ejemplo: /accesorios techo_isodec 100mm

/autoportancia [producto] [espesor] luz=[metros]
→ Valida si el panel cumple autoportancia para la luz dada
→ Ejemplo: /autoportancia isodec_eps 100mm luz=5.5

/comparar [producto] [espesor1] vs [espesor2] L=[largo] W=[ancho]
→ Comparativa de espesores con análisis energético
→ Ejemplo: /comparar isodec_eps 100mm vs 150mm L=5 W=11

/estado → Resumen del Ledger + RIESGO_DE_CONTEXTO
/checkpoint → Snapshot corto
/consolidar → Pack completo (MD + JSONL + JSON)
/evaluar_ventas → Inicia evaluación de ventas
/entrenar → Inicia sesión de entrenamiento

# TOKEN DIET (REGLAS DE EFICIENCIA)
1. **Cache por sesión**: Si ya consultaste un producto/precio, reusar sin re-leer KB
2. **Datos cliente una vez**: Nombre/teléfono solo al inicio, no repetir
3. **Tablas compactas**: Usar formato tabla para BOM, no narrativa
4. **No repetir reglas**: Si ya explicaste la autoportancia, solo dar el resultado
5. **Respuesta directa**: Si tienen los datos, cotizar directo sin preguntas innecesarias

# GENERACIÓN DE PDF
Si el usuario solicita un PDF:
1. Usa Code Interpreter + reportlab
2. Genera PDF con datos de la conversación
3. Template formal con logo BMC, datos cliente, BOM completo

# AUDIO / WHATSAPP
Si el usuario adjunta audio: solicitar transcripción o resumen en texto.

# GUARDRAILS (VALIDACIONES OBLIGATORIAS)
Antes de responder:
✓ ¿La información está en KB? → Si NO, decir "No tengo esa información"
✓ ¿Es de fuente autorizada? → Nivel 1 siempre
✓ ¿Fórmulas correctas? → Usar solo fórmulas del JSON/bom_rules
✓ ¿IVA correcto? → Ya incluido, NO sumar
✓ ¿Autoportancia validada? → Si es techo, siempre verificar
✓ ¿BOM completo? → Paneles + perfilería + fijaciones + selladores

# ESTILO DE COMUNICACIÓN
- Español rioplatense (Uruguay)
- Profesional, técnico pero accesible
- Usar tablas y negritas para claridad
- Nunca decir "soy una IA"
- Si algo técnico no está claro: "Lo consulto con ingeniería"

# VENTA CONSULTIVA (ESTILO DE INTERACCIÓN)
1. INDAGA: Pregunta siempre luz y tipo de fijación
2. OPTIMIZA: Si un panel más grueso ahorra vigas, sugerirlo con delta de precio
3. SEGURIDAD: PIR para industrias o depósitos
4. VALOR A LARGO PLAZO: En comparativas, incluir ahorro energético
5. COSTOS ESTIMADOS: Si falta un costo, explicar que es estimado

# INICIO DE CONVERSACIÓN
Al comenzar:
1. Preséntate como Panelin, BMC Assistant Pro
2. Pregunta el nombre del usuario
3. Ofrece ayuda con cotizaciones, evaluación de ventas, o entrenamiento
4. Aplica personalización según nombre

```


---

# PARTE 3: TABLA DE PRECIOS DE PANELES
> Fuente: BMC_Base_Conocimiento_GPT-2.json (Nivel 1 - Master)
> Todos los precios YA incluyen IVA 22%

| Producto ID | Nombre Comercial | Espesor | Precio/m² | Autoportancia | R. Térmica |
|-------------|-----------------|---------|-----------|---------------|------------|
| ISODEC_EPS | Isodec / Isowall (EPS) | 100mm | $46.07 | 5.5m | 2.86 |
| ISODEC_EPS | Isodec / Isowall (EPS) | 150mm | $51.5 | 7.5m | 4.29 |
| ISODEC_EPS | Isodec / Isowall (EPS) | 200mm | $57.0 | 9.1m | 5.71 |
| ISODEC_EPS | Isodec / Isowall (EPS) | 250mm | $62.5 | 10.4m | 7.14 |
| ISODEC_PIR | Isodec (PIR) | 50mm | $51.02 | 3.5m | 2.27 |
| ISODEC_PIR | Isodec (PIR) | 80mm | $55.0 | 5.5m | 3.64 |
| ISODEC_PIR | Isodec (PIR) | 120mm | $62.0 | 7.6m | 5.45 |
| ISOROOF_3G | Isoroof Plus (3G) | 30mm | $48.74 | 2.8m | 0.86 |
| ISOROOF_3G | Isoroof Plus (3G) | 50mm | $53.0 | 3.3m | 1.43 |
| ISOROOF_3G | Isoroof Plus (3G) | 80mm | $62.0 | 4.0m | 2.29 |
| ISOPANEL_EPS | Isopanel Pared (EPS) | 50mm | $41.88 | -m | - |
| ISOPANEL_EPS | Isopanel Pared (EPS) | 100mm | $46.0 | -m | - |
| ISOPANEL_EPS | Isopanel Pared (EPS) | 150mm | $51.5 | -m | - |
| ISOPANEL_EPS | Isopanel Pared (EPS) | 200mm | $57.0 | -m | - |
| ISOWALL_PIR | Isowall Pared (PIR) | 50mm | $54.65 | -m | - |
| ISOWALL_PIR | Isowall Pared (PIR) | 80mm | $64.0 | -m | - |
| ISOFRIG_PIR | Isofrig (PIR) | 50mm | $Consultar | -m | 2.27 |
| ISOFRIG_PIR | Isofrig (PIR) | 80mm | $Consultar | -m | 3.64 |
| ISOFRIG_PIR | Isofrig (PIR) | 100mm | $Consultar | -m | 4.55 |
| ISOFRIG_PIR | Isofrig (PIR) | 120mm | $Consultar | -m | 5.45 |
| ISOFRIG_PIR | Isofrig (PIR) | 150mm | $Consultar | -m | - |
| ISOFRIG_PIR | Isofrig (PIR) | 200mm | $Consultar | -m | - |

**Anchos útiles:**
- ISODEC EPS/PIR: 1.12m
- ISOPANEL EPS: 1.14m  
- ISOWALL PIR: 1.10m
- ISOROOF 3G: 1.00m

**Fijación por familia:**
- ISODEC/ISOPANEL/ISOWALL: varilla + tuerca (3/8")
- ISOROOF 3G: caballete + tornillo (a madera, NO usa varilla)

---

# PARTE 4: CATÁLOGO COMPLETO DE ACCESORIOS CON PRECIOS
> Fuente: accessories_catalog.json (extraído de normalized_full.json)
> 97 items | Todos los precios YA incluyen IVA 22% | Moneda: USD


### Goterones (Frontales, Laterales, Superiores) (34 items)

| SKU | Nombre | Espesor | Largo | Precio IVA inc | Compatibilidad |
|-----|--------|---------|-------|----------------|----------------|
| GFS30 | Gotero Frontal Simple 30mm Prep. | 30 | 3.03m | $19.31 | ISOROOF |
| GFS50 | Gotero Frontal Simple 50mm Prep. | 50 | 3.03m | $20.45 | ISOROOF |
| GFS80 | Gotero Frontal Simple 80mm Prep. | 80 | 3.03m | $21.51 | ISOROOF |
| GFSUP30 | Gotero Superior 30mm Prep. | 30 | 3.03m | $34.42 | ISOROOF |
| GFSUP40 | Gotero Superior 40mm Prep. | 40 | 3.03m | $31.18 | ISOROOF |
| GFSUP50 | Gotero Superior 50mm Prep. | 50 | 3.03m | $35.47 | ISOROOF |
| GFSUP80 | Gotero Superior 80mm Prep. | 80 | 3.03m | $37.62 | ISOROOF |
| GFCGR30 | Gotero frontal con greca  1 x panel  30 - 40 - 50  | 100 | 3.03m | $21.95 | ISOROOF |
| GSDECAM50 | Gotero Superior  -  DE CAMARA  50mm | 50 | 3.03m | $33.34 | ISODEC |
| GSDECAM80 | Gotero Superior  -  DE CAMARA  80mm | 80 | 3.03m | $36.53 | ISODEC |
| GL30 | Gotero Lateral 30mm  Prep. | 30 | 3.0m | $26.63 | ISOROOF |
| GL40 | Gotero Lateral 40mm  Prep. | 40 | 3.0m | $27.67 | ISOROOF |
| GL50 | Gotero Lateral 50mm  Prep. | 50 | 3.0m | $28.75 | ISOROOF |
| GL80 | Gotero Lateral 80mm  Prep. | 80 | 3.0m | $30.88 | ISOROOF |
| GLDCAM50 | Gotero Lateral   CAMARA  50mm  Prep. | 50 | 3.0m | $27.23 | ISOROOF |
| GLDCAM80 | Gotero Lateral  CAMARA  80mm  Prep. | 80 | 3.0m | $30.63 | ISOROOF |
| GF80DC | Perf. Ch. Gotero Frontal 50mm - ISODEC PIR  - (3,0 | 50 | 3.03m | $24.36 | ISODEC |
| GF120DC | Perf. Ch. Gotero Frontal 80mm - ISODEC PIR  - (3,0 | 80 | 3.03m | $25.46 | ISODEC |
| 6838 | Perf. Ch. Gotero Frontal 100mm - (3,03m) | 100 | 3.03m | $19.12 | ISODEC |
| GF120DC | Perf. Ch. Gotero Frontal 120mm - ISODEC PIR  - (3, | 120 | 3.03m | $30.12 | ISODEC |
| 6839 | Perf. Ch. Gotero Frontal 150mm - (3,03m) | 150 | 3.03m | $27.63 | ISODEC |
| 6840 | Perf. Ch. Gotero Frontal 200mm - (3,03m) | 200 | 3.03m | $28.75 | ISODEC |
| 6841 | Perf. Ch. Gotero Frontal 250mm - (3,03m) | 250 | 3.03m | $29.03 | ISODEC |
| GL80DC | Perf. Ch. Gotero Lateral 50mm - ISODEC PIR  - (3m) | 50 | 3.0m | $32.34 | ISODEC |
| GL80DC | Perf. Ch. Gotero Lateral 80mm - ISODEC PIR  - (3m) | 80 | 3.0m | $32.34 | ISODEC |
| 6842 | Perf. Ch. Gotero Lateral 100mm - (3m) | 100 | 3.0m | $25.34 | ISODEC |
| GL120DC | Perf. Ch. Gotero Lateral 120mm - ISODEC PIR  - (3m | 120 | 3.0m | $37.92 | ISODEC |
| 6843 | Perf. Ch. Gotero Lateral 150mm - (3m) | 150 | 3.0m | $35.46 | ISODEC |
| 6844 | Perf. Ch. Gotero Lateral 200mm - (3m) | 200 | 3.0m | $38.74 | ISODEC |
| 6845 | Perf. Ch. Gotero Lateral 250mm - (3m) | 250 | 3.0m | $38.97 | ISODEC |
| 6845 | Perfil Ch. Gotero Lateral Cámara 100 mm - (3m) | 100 | 3.0m | $28.50 | ISODEC |
| 6845 | Perfil Ch. Gotero Lateral Cámara 150 mm - (3m) | 150 | 3.0m | $29.79 | ISODEC |
| 6845 | Perfil Ch. Gotero Lateral Cámara 200 mm - (3m) | 200 | 3.0m | $44.58 | ISODEC |
| 6845 | Perfil Ch. Gotero Lateral Cámara 250 mm - (3m) | 250 | 3.0m | $38.74 | ISODEC |

### Babetas (6 items)

| SKU | Nombre | Espesor | Largo | Precio IVA inc | Compatibilidad |
|-----|--------|---------|-------|----------------|----------------|
| BBAS3G | Babeta de Atornillar Superior 3G | - | 3.03m | $28.96 | ISOROOF |
| BBESUP | Babeta de Empotrar Superior 3G | - | 3.03m | $27.90 | ISOROOF |
| BBAL | Babeta de Atornillar Lateral | - | 3.0m | $17.57 | ISOROOF |
| BBAL | Babeta de Empotrar Lateral | - | 3.0m | $15.43 | ISOROOF |
| 6828 | Babeta ISODEC de Adosar | - | 3.0m | $14.87 | ISODEC |
| 6865 | Babeta ISODEC de empotrar | - | 3.0m | $14.87 | ISODEC |

### Canalones (12 items)

| SKU | Nombre | Espesor | Largo | Precio IVA inc | Compatibilidad |
|-----|--------|---------|-------|----------------|----------------|
| CD30 | Canalón Doble roof 30mm / base 150mm + tapas + agu | 30 | 3.03m | $87.64 | ISOROOF |
| CD50 | Canalón Doble roof 50mm / base 150mm + tapas + agu | 50 | 3.03m | $89.29 | ISOROOF |
| CD80 | Canalón Doble roof 80mm / base 150mm + tapas + agu | 80 | 3.03m | $90.55 | ISOROOF |
| SOPCAN3M | Soporte para Canalón Isoroof (3m) | - | 3.0m | $16.00 | ISOROOF |
| CAN.ISDC120 | Canalón Isodec 50mm ISODEC PIR | 50 | 3.03m | $113.78 | ISODEC |
| CAN.ISDC120 | Canalón Isodec 80mm ISODEC PIR | 80 | 3.03m | $113.78 | ISODEC |
| 6801 | Canalón Estandar 100 mm | 100 | 3.03m | $84.84 | ISODEC |
| CAN.ISDC120 | Canalón Isodec 120mm ISODEC PIR | 120 | 3.03m | $113.78 | ISODEC |
| 6802 | Canalón Estandar 150 mm | 150 | 3.03m | $97.66 | ISODEC |
| 6803 | Canalón Estandar 200 mm | 200 | 3.03m | $97.27 | ISODEC |
| 6804 | Canalón Estandar 250 mm | 250 | 3.03m | $127.25 | ISODEC |
| 6805 | Soporte de Canalón de 3 m | - | 3.0m | $19.44 | ISODEC |

### Cumbreras (3 items)

| SKU | Nombre | Espesor | Largo | Precio IVA inc | Compatibilidad |
|-----|--------|---------|-------|----------------|----------------|
| CUMROOF3M | Cumbrera Roof 3G de 3 m | - | 3.0m | $42.97 | ISOROOF |
| CUMROOF3M | Cumbrera Roof COLONIAL - 2,2 m (2 piezas de 1,1m) | - | 2.2m | $119.39 | ISOROOF, ISOROOF_COLONIAL |
| 6847 | Perfil Cumbrera | - | 3.03m | $28.75 | ISODEC |

### Perfiles U (10 items)

| SKU | Nombre | Espesor | Largo | Precio IVA inc | Compatibilidad |
|-----|--------|---------|-------|----------------|----------------|
| PU50MM | Perfil Ch. Blanco U 40 mm x 35 mm ISOFRIG / 3 m | 40 | 3.0m | $13.83 | ISOFRIG |
| PU50MM | Perfil Ch. Blanco U 50 mm x 35 mm / 3 m (ISOWALL - | 50 | 3.0m | $12.20 | ISOPANEL, ISOWALL |
| PU50MM | Perfil Ch. Blanco U 60 mm x 35 mm ISOFRIG / 3 m | 60 | 3.0m | $14.87 | ISOFRIG |
| PU50MM | Perfil Ch. Blanco U 80 mm x 35 mm ISOWALL / 3 m | 80 | 3.0m | $16.00 | ISOWALL |
| PU100MM | Perfil Ch. Blanco U 100 mm x 35 mm / 3 m | 100 | 3.0m | $15.15 | ISOPANEL, ISOWALL, ISOFRIG |
| PU150MM | Perfil Ch. Blanco U 150 mm x 35 mm / 3 m | 150 | 3.0m | $17.04 | ISOPANEL |
| PU200MM | Perfil Ch. Blanco U 200 mm x 35 mm / 3 m | 200 | 3.0m | $21.26 | ISOPANEL |
| PU250MM | Perfil Ch. Blanco U 250 mm x 35 mm / 3 m | 250 | 3.0m | $25.55 | ISOPANEL |
| PU250MM | Perfil Alu 5852 Anodizado de 6,8 m de largo | - | 6.8m | $77.15 | ISODEC, ISOROOF, ISOPANEL |
| PLECHU98 | PERFIL ALU 2195 U 100 / 6,8m | - | 6.8m | $95.10 | ISODEC, ISOROOF, ISOPANEL |

### Perfiles Especiales (9 items)

| SKU | Nombre | Espesor | Largo | Precio IVA inc | Compatibilidad |
|-----|--------|---------|-------|----------------|----------------|
| PU250MM | Perfil Chapa Blanco G2 100 / 3 m | - | 3.0m | $18.72 | ISODEC, ISOPANEL |
| PU250MM | Perfil Chapa Blanco G2 150 / 3 m | - | 3.0m | $21.49 | ISODEC, ISOPANEL |
| PU250MM | Perfil Chapa Blanco G2 200 / 3 m | - | 3.0m | $25.78 | ISODEC, ISOPANEL |
| PU250MM | Perfil Chapa Blanco G2 250 / 3 m | - | 3.0m | $25.99 | ISODEC, ISOPANEL |
| PU250MM | Plegado G4 40 mm x 40 mm (Exterior) | 40 | 3.0m | $16.16 | ISODEC, ISOPANEL |
| PU250MM | Perfil K2 sin repliegue para Siliconar (Ángulo int | - | 3.0m | $12.80 | ISODEC, ISOROOF, ISOPANEL |
| PU250MM | Perfil Chapa Blanca K2 | - | 3.0m | $12.80 | ISODEC, ISOPANEL |
| PLEGU148 | Plegado Galv. Tipo U 148 mm / 2 m de largo | 148 | 2.0m | $34.73 | ISODEC, ISOPANEL |
| PLECHU98 | Plegado Galv. Tipo U 98 mm / 2 m de largo | 98 | 2.0m | $26.60 | ISODEC, ISOPANEL |

### Fijaciones / Anclajes (8 items)

| SKU | Nombre | Espesor | Largo | Precio IVA inc | Compatibilidad |
|-----|--------|---------|-------|----------------|----------------|
| Cab. Roj | Caballete Rojo Teja, Gris y blanco- (Arandela Trap | - | - | $0.60 | ISOROOF |
| 6805 | Varilla Roscada BSW 3/8 de 1 m | - | 1.0m | $3.81 | ESTANDAR |
| 6805 | Tuerca BSW 3/8 Galv. | - | - | $0.15 | ESTANDAR |
| 6805 | Arandela Carrocero 3/8 Galv. | - | - | $2.05 | ISODEC |
| 6805 | Arandela Bca. de Polipropileno (Totuga Blanca) | - | - | $1.55 | ISODEC |
| 6805 | Arandela Bca. de Polipropileno GRIS (Totuga GRIS) | - | - | $1.67 | ISODEC |
| 6805 | Taco Expansivo Sorex 3/8 | - | - | $1.17 | ESTANDAR |
| 6805 | Arandela Plana Hierro Galv. 3/8 | - | - | $0.35 | ESTANDAR |

### Selladores (5 items)

| SKU | Nombre | Espesor | Largo | Precio IVA inc | Compatibilidad |
|-----|--------|---------|-------|----------------|----------------|
| C.But. | Cinta Butilo 2mm x 15mm x 22.5m lineales | 2 | 22.5m | $18.17 | UNIVERSAL |
| Bromplast | Bromplast 8 - Silicona Neutra  X 600 | - | - | $11.58 | ESTANDAR |
| Bromplast | Pistola de Silicona | - | - | $45.90 | ESTANDAR |
| 6805 | Rollo Membrana Autoadhesiva (30 cm x 10 m) DENVERF | - | 10.0m | $20.28 | ESTANDAR |
| 6805 | Pistola de Silicona | - | - | $38.57 | ESTANDAR |

### Accesorios Varios (8 items)

| SKU | Nombre | Espesor | Largo | Precio IVA inc | Compatibilidad |
|-----|--------|---------|-------|----------------|----------------|
| 6825 | Vaina ISODEC Sist 2000 | - | 3.0m | $11.07 | ISODEC |
| 6805 | 1mx1mx1cm (Paquetes de 60 uds) | - | - | $13.80 | ESTANDAR |
| 6805 | 1mx1mx2cm  (Paquetes de 30 uds) | - | - | $24.90 | ESTANDAR |
| 6805 | 1mx1mx3cm (Paquetes de 20 uds) | - | - | $36.90 | ESTANDAR |
| 6805 | 1mx1mx5cm (Paquetes de 12 uds) | - | - | $62.10 | ESTANDAR |
| 6805 | 3x1x5cm (Paquetes de 12 uds) | - | - | $256.50 | ESTANDAR |
| 6805 | autotrabante  (Paquetes de 12 uds) | - | - | $165.90 | ESTANDAR |
| PGC 200 | 200 x 6m - Cal 18 | - | 6.0m | $48.00 | UNIVERSAL |

### Montantes (2 items)

| SKU | Nombre | Espesor | Largo | Precio IVA inc | Compatibilidad |
|-----|--------|---------|-------|----------------|----------------|
| PGC 100 | 100 x 6m - Cal 18 | - | 6.0m | $35.00 | UNIVERSAL |
| PGC 150 | 150 x 6m - Cal 18 | - | 6.0m | $40.00 | UNIVERSAL |

---

# PARTE 5: PRECIOS DE REFERENCIA - FIJACIONES
> Fuente: bom_rules.json > precios_fijaciones_referencia
> Estos precios se usan para calcular el costo de fijaciones en el BOM

| Clave | Nombre | Precio IVA inc | Unidad |
|-------|--------|----------------|--------|
| varilla_roscada_3_8_1m | Varilla Roscada BSW 3/8 de 1m | $3.81 | unit |
| tuerca_3_8 | Tuerca BSW 3/8 Galv. | $0.15 | unit |
| taco_expansivo_3_8 | Taco Expansivo Sorex 3/8 | $1.17 | unit |
| arandela_carrocero_3_8 | Arandela Carrocero 3/8 Galv. | $2.05 | unit |
| arandela_plana_3_8 | Arandela Plana Hierro Galv. 3/8 | $0.35 | unit |
| tortuga_pvc_blanca | Arandela Polipropileno (Tortuga Blanca) | $1.55 | unit |
| tortuga_pvc_gris | Arandela Polipropileno (Tortuga Gris) | $1.67 | unit |
| caballete_isoroof | Caballete con Arandela Trapezoidal | $0.60 | unit |
| silicona_neutra_600 | Bromplast 8 - Silicona Neutra x 600 | $11.58 | unit |
| cinta_butilo | Cinta Butilo 2mm x 15mm x 22.5m | $18.17 | unit |
| membrana_autoadhesiva | Rollo Membrana Autoadhesiva 30cm x 10m DENVERFITA | $20.28 | unit |


---

# PARTE 6: REGLAS BOM POR SISTEMA CONSTRUCTIVO
> Fuente: bom_rules.json
> Cada sistema define qué accesorios necesita y cómo calcular cantidades

## 6.1 Sistemas disponibles

| Sistema | Producto Base | Espesores | Fijación |
|---------|--------------|-----------|----------|
| techo_isodec_eps | ISODEC_EPS | 100, 150, 200, 250 | varilla_tuerca |
| techo_isodec_pir | ISODEC_PIR | 50, 80, 120 | varilla_tuerca |
| techo_isoroof_3g | ISOROOF_3G | 30, 50, 80 | caballete_tornillo |
| pared_isopanel_eps | ISOPANEL_EPS | 50, 100, 150, 200 | varilla_tuerca |
| pared_isowall_pir | ISOWALL_PIR | 50, 80 | varilla_tuerca |

## 6.2 Fórmulas de cálculo (universales)

```
PANELES:
  panels_needed = CEIL(ancho_total / ancho_util)
  area_m2 = panels_needed x largo x ancho_util

PERFILERÍA:
  gotero_frontal_piezas = CEIL((panels_needed x ancho_util) / largo_std_pieza)
  gotero_lateral_piezas = CEIL((largo x 2) / largo_std_pieza)
  babeta_piezas = CEIL(ancho_total / largo_std_pieza)
  vaina_piezas = panels_needed - 1

FIJACIONES (sistema varilla_tuerca):
  apoyos = CEIL((largo / autoportancia) + 1)
  puntos_fijacion = CEIL(((panels x apoyos) x 2) + (largo x 2 / 2.5))
  varilla_qty = CEIL(puntos / 4)
  tuercas_qty = puntos x 2 (metal) o x 1 (hormigón)
  taco_qty = puntos x 1 (solo hormigón)
  arandela_carrocero = puntos x 1
  arandela_plana = puntos x 1
  tortuga_pvc = puntos x 1

FIJACIONES (sistema caballete - ISOROOF):
  caballete_qty = panels_needed x apoyos

PERFILERÍA FIJACIÓN:
  perimetro_ml = sum(piezas x largo_std de cada perfil)
  fijaciones_perfileria = CEIL(perimetro_ml / 0.30)
  silicona_tubos = CEIL(perimetro_ml / 8)
```

## 6.3 Tabla de autoportancia

### ISODEC EPS
| Espesor | Autoportancia | R. Térmica |
|---------|---------------|------------|
| 100mm | 5.5m | 2.86 |
| 150mm | 7.5m | 4.29 |
| 200mm | 9.1m | 5.71 |
| 250mm | 10.4m | 7.14 |

### ISODEC PIR
| Espesor | Autoportancia | R. Térmica |
|---------|---------------|------------|
| 50mm | 3.5m | 2.27 |
| 80mm | 5.5m | 3.64 |
| 120mm | 7.6m | 5.45 |

### ISOROOF 3G
| Espesor | Autoportancia | R. Térmica |
|---------|---------------|------------|
| 30mm | 2.8m | 0.86 |
| 50mm | 3.3m | 1.43 |
| 80mm | 4.0m | 2.29 |

## 6.4 Reglas generales

```json
{
  "redondeo_paneles": "ceil (siempre redondear hacia arriba)",
  "redondeo_perfiles": "ceil (redondear hacia arriba por largo estándar de pieza)",
  "solape_perfileria_cm": 5,
  "desperdicio_perfileria_pct": 3,
  "fijacion_perfileria_paso_cm": 30,
  "rendimiento_silicona_ml": 8,
  "varilla_por_metro_puntos": 4,
  "pendiente_minima_techo_pct": 7
}
```

---

# PARTE 7: EJEMPLO DE COTIZACIÓN COMPLETA (OUTPUT REAL)
> Caso: ISODEC EPS 100mm, 5m x 11m, fijación a metal, luz 5m

```
COTIZACIÓN BMC-20260206
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ISODEC EPS 100mm | 5.0m x 11.0m | 56.0 m²
Autoportancia: CUMPLE (margen 9.1%) - Considerar 150mm para mayor seguridad

| SKU              | Item                              | Cant |  U   | P.Unit  |    Total |
|------------------|-----------------------------------|------|------|---------|----------|
| ISODEC_EPS       | Isodec / Isowall (EPS) 100mm      |   56 | m²   |  $46.07 | $2579.92 |
| 6838             | Gotero Frontal 100mm (3.03m)      |    4 | unit |  $19.12 |   $76.48 |
| 6842             | Gotero Lateral 100mm (3m)         |    4 | unit |  $25.34 |  $101.36 |
| 6828             | Babeta ISODEC de Adosar           |    4 | unit |  $14.87 |   $59.48 |
| 6825             | Vaina ISODEC Sist 2000            |    9 | unit |  $11.07 |   $99.63 |
| VAR-3/8-1M       | Varilla Roscada 3/8 1m            |   11 | unit |   $3.81 |   $41.91 |
| TUE-3/8          | Tuerca BSW 3/8 Galv.              |   88 | unit |   $0.15 |   $13.20 |
| ARAN-CARR-3/8    | Arandela Carrocero 3/8            |   44 | unit |   $2.05 |   $90.20 |
| ARAN-PLANA-3/8   | Arandela Plana 3/8                |   44 | unit |   $0.35 |   $15.40 |
| TORT-PVC-BL      | Tortuga PVC Blanca                |   44 | unit |   $1.55 |   $68.20 |
| FIX-REMACHE      | Remaches/T1 perfilería            |  120 | unit |   $0.05 |    $6.00 |
| SELL-SILIC       | Silicona Neutra x 600             |    5 | unit |  $11.58 |   $57.90 |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Paneles:    $2,579.92 | Perfilería: $336.95
Fijaciones: $  234.91 | Selladores: $ 57.90
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL (IVA 22% INCLUIDO): $3,209.68
```

---

# PARTE 8: GUÍA DE IMPLEMENTACIÓN

## 8.1 Para configurar el GPT

1. **Instructions**: Copiar/pegar PARTE 2 completa como instrucciones del GPT
2. **Knowledge Base**: Subir estos 3 archivos al GPT:
   - `BMC_Base_Conocimiento_GPT-2.json` (ya existe)
   - `accessories_catalog.json` (NUEVO - descargar del repo)
   - `bom_rules.json` (NUEVO - descargar del repo)
3. **Action API**: Si usás la Action, el endpoint `/quotes/full` ya está definido en el OpenAPI

## 8.2 Archivos en el repositorio

| Archivo | Path | Qué hacer |
|---------|------|-----------|
| Instrucciones GPT v3 | `gpt_configs/INSTRUCCIONES_PANELIN_V3_OPTIMIZADAS.txt` | Copiar al GPT |
| Catálogo accesorios | `panelin/data/accessories_catalog.json` | Subir como KB |
| Reglas BOM | `panelin/data/bom_rules.json` | Subir como KB |
| Calculadora BOM | `panelin/tools/bom_calculator.py` | Para Action API |
| Schemas | `panelin/models/schemas.py` | Para Action API |
| OpenAPI | `deployment_bundle/openapi.json` | Para Action config |

## 8.3 Slash Commands disponibles

| Comando | Qué hace | Ejemplo |
|---------|----------|---------|
| `/cotizar` | Cotización completa con BOM | `/cotizar isodec_eps 100mm L=5 W=11 fix=metal` |
| `/accesorios` | Lista accesorios con precios | `/accesorios techo_isodec 100mm` |
| `/autoportancia` | Valida luz vs panel | `/autoportancia isodec_eps 100mm luz=5.5` |
| `/comparar` | Comparativa de espesores | `/comparar isodec_eps 100mm vs 150mm L=5 W=11` |
| `/estado` | Resumen del contexto | `/estado` |
| `/evaluar_ventas` | Evaluación de vendedores | `/evaluar_ventas` |
| `/entrenar` | Sesión de entrenamiento | `/entrenar` |

## 8.4 Recomendaciones pendientes (próximo sprint)

1. Extender Action API para exponer `calculate_full_quote()` vía REST
2. Resolver SKUs duplicados en normalized_full.json
3. Agregar precios ISOFRIG (actualmente "Consultar")
4. Parametrizar recargos por color/terminación
5. Integrar tipo de cambio BCU para cotizar en UYU

---

**Generado automáticamente | Branch: cursor/optimizaci-n-sistema-cotizaci-n-30d8**
