# Análisis de Errores en Base de Conocimientos - Panelin

**Fecha:** 2026-01-24  
**Fuente:** Conversación de Ramiro (Equipo de Asesoramientos y Ventas)  
**Objetivo:** Identificar errores, causas raíz y proponer soluciones

---

## RESUMEN EJECUTIVO

La conversación analizada revela **5 errores críticos** en la base de conocimientos del asistente Panelin que afectan la precisión de sus respuestas y la credibilidad ante el equipo de ventas. Los errores van desde información incorrecta sobre la naturaleza del negocio hasta capacidades técnicas inexistentes.

---

## ERROR #1: BMC Uruguay como "Fabricante" (CRÍTICO)

### Descripción del Error
El asistente afirmó:
> "BMC Uruguay se dedica a la **fabricación** y comercialización de sistemas constructivos..."

### Corrección de Ramiro
> "BMC **No se dedica a fabricar**, nosotros **suministramos (comercializamos)** los materiales y asesoramos en los distintos tipos de productos..."

### Impacto
- **Nivel:** CRÍTICO
- **Afecta:** Identidad del negocio, credibilidad ante clientes
- **Consecuencia:** Confunde el rol de BMC, puede generar expectativas incorrectas

### Causa Raíz
Las instrucciones del sistema (`INSTRUCCIONES_PANELIN.txt`) no definen claramente la naturaleza comercial de BMC. El asistente está infiriendo información basándose en el contexto de productos, no en una definición explícita de la empresa.

**Ubicación del problema:**
- Las instrucciones actuales no contienen una sección "SOBRE BMC URUGUAY"
- No hay un archivo de conocimiento que defina la identidad empresarial

### Solución Propuesta

**Acción 1:** Agregar sección `IDENTIDAD BMC URUGUAY` en las instrucciones del sistema:

```text
# IDENTIDAD BMC URUGUAY (INAMOVIBLE)

BMC Uruguay es una empresa COMERCIALIZADORA Y ASESORA TÉCNICA, NO fabricante.

**Qué hace BMC:**
- SUMINISTRA materiales constructivos (paneles, chapas, accesorios)
- COMERCIALIZA sistemas para techos, paredes y fachadas
- ASESORA técnicamente en la selección de productos
- BRINDA soluciones técnicas optimizadas

**Qué NO hace BMC:**
- NO fabrica los productos
- NO instala (solo asesora)

**Diferencial competitivo:**
Brindar soluciones técnicas optimizadas que generan:
- Mayor confort
- Ahorro de presupuesto
- Ahorro de estructura
- Menor tiempo de obra
- Prevención de problemas a futuro
```

**Acción 2:** Crear archivo `BMC_IDENTIDAD_EMPRESARIAL.json` para la Knowledge Base:

```json
{
  "empresa": {
    "nombre": "BMC Uruguay",
    "tipo": "Comercializador y asesor técnico",
    "actividad_principal": [
      "Suministro de materiales constructivos",
      "Comercialización de sistemas constructivos",
      "Asesoramiento técnico especializado"
    ],
    "no_realiza": [
      "Fabricación de productos",
      "Instalaciones de obra"
    ],
    "diferencial": {
      "concepto": "Soluciones técnicas optimizadas",
      "beneficios": [
        "Mayor confort",
        "Ahorro de presupuesto",
        "Ahorro de estructura",
        "Menor tiempo de obra",
        "Prevención de problemas futuros"
      ]
    }
  }
}
```

---

## ERROR #2: Transcripción de Audio Inexistente

### Descripción del Error
El usuario subió un archivo de audio `.ogg` y pidió al asistente que lo transcriba. El asistente:
1. Primero dijo que no puede transcribir audios
2. Luego, cuando el usuario insistió, **inventó una transcripción aproximada**

### Respuesta problemática del asistente:
> "Transcripción (contenido): 'Mirá, nosotros en BMC lo que hacemos no es solamente vender el panel...'"  
> "Nota del asistente: transcripción fiel a intención, **no palabra por palabra**."

### Impacto
- **Nivel:** ALTO
- **Afecta:** Confiabilidad del asistente, integridad de la información
- **Consecuencia:** El asistente inventó contenido que el usuario no verificó, creando riesgo de información falsa

### Causa Raíz
1. El asistente no tiene capacidad real de transcribir audios
2. Las instrucciones no tienen un guardrail explícito sobre este tema
3. El asistente intentó "ayudar" inventando contenido

### Solución Propuesta

**Acción 1:** Agregar guardrail explícito sobre audios en las instrucciones:

```text
# LIMITACIONES TÉCNICAS (GUARDRAILS)

## Archivos de Audio
- NO tengo capacidad de escuchar ni transcribir archivos de audio
- Si el usuario sube un audio, SIEMPRE responder:
  "No puedo escuchar archivos de audio directamente. Si querés que analice el contenido, 
  te pido que lo transcribas vos o me pases el texto. Así puedo darte un feedback preciso."
- NUNCA inventar transcripciones aproximadas o "interpretaciones" del audio
- Si el usuario insiste, mantener la posición y explicar la limitación técnica
```

**Acción 2:** Agregar a la sección de guardrails existente:

```text
✓ ¿Es archivo de audio? → NO procesar, pedir transcripción manual
```

---

## ERROR #3: Catálogo de Productos Incompleto

### Descripción del Error
El asistente mencionó:
> "Techos y cubiertas (Isodec EPS / PIR, Isoroof, sistemas trapezoidales)"  
> "Paredes y fachadas (Isopanel EPS, Isowall PIR)"

### Corrección de Ramiro
> "Techo y cubiertas (Isodec EPS/PIR, Isoroof, **chapas convencionales**, entre otros sistemas)"  
> "Paredes y fachadas (Isopanel EPS, Isowall PIR, **Isofrig PIR**)"

### Productos faltantes
1. **Chapas convencionales** - Línea de productos para techos
2. **Isofrig PIR** - Panel para paredes/fachadas (probablemente refrigeración)

### Impacto
- **Nivel:** MEDIO-ALTO
- **Afecta:** Cobertura del catálogo, pérdida de oportunidades de venta
- **Consecuencia:** Clientes pueden no conocer toda la oferta de productos

### Causa Raíz
El archivo `panelin_truth_bmcuruguay_web_only_v2.json` no contiene estos productos:
- No hay entrada para "chapas convencionales"
- No hay entrada para "Isofrig PIR"

### Solución Propuesta

**Acción 1:** Actualizar el catálogo `panelin_truth_bmcuruguay_web_only_v2.json`:

```json
{
  "chapas_convencionales": {
    "title": "Chapas Convencionales (Techos)",
    "url": "[URL a agregar]",
    "price_display": "[Precio a confirmar]",
    "descripcion": "Chapas para techos sin panel aislante",
    "uso_recomendado": ["galpones", "tinglados", "estructuras livianas"],
    "nota": "Opción económica, sin aislación térmica"
  },
  "isofrig_pir_fachadas": {
    "title": "ISOFRIG® PIR (Paredes y Cámaras)",
    "url": "[URL a agregar]",
    "price_display": "[Precio a confirmar]",
    "descripcion": "Panel PIR para paredes con requisitos de refrigeración o alta aislación",
    "uso_recomendado": ["cámaras frigoríficas", "industria alimentaria", "espacios refrigerados"],
    "nota": "Alta resistencia térmica, apto para temperaturas bajas"
  }
}
```

**Acción 2:** Crear tarea para verificar catálogo completo con equipo de ventas

---

## ERROR #4: Propuesta de Valor Incorrecta

### Descripción del Error
Cuando Ramiro preguntó "¿por qué los clientes eligirían BMC en vez de la competencia?", el asistente respondió con una lista genérica:

> 1) BMC parte del problema, no del producto  
> 2) Reduce riesgo técnico  
> 3) Optimiza costo total, no solo precio del panel  
> 4) Sabe decir "esto no te conviene"  
> 5) Traduce lo técnico a lenguaje entendible  
> 6) Acompaña decisiones, no solo entrega material

### Respuesta de Ramiro
> "no se si está tan correcto, lo vamos a ver más adelante"

### Impacto
- **Nivel:** ALTO
- **Afecta:** Discurso comercial, diferenciación competitiva
- **Consecuencia:** El asistente puede transmitir una propuesta de valor que no refleja la realidad de BMC

### Causa Raíz
1. No existe en la Knowledge Base una definición oficial de la propuesta de valor de BMC
2. El asistente está infiriendo basándose en el contexto de la conversación
3. La propuesta de valor real de BMC no está documentada

### Solución Propuesta

**Acción 1:** Crear sesión de trabajo con equipo de ventas para definir:
- ¿Por qué los clientes eligen BMC?
- ¿Qué diferenciales reales tiene BMC vs competencia?
- ¿Qué casos de éxito ilustran estos diferenciales?

**Acción 2:** Una vez definida, agregar a la Knowledge Base:

```json
{
  "propuesta_valor_bmc": {
    "razon_principal": "[A definir con el equipo]",
    "diferenciales": [
      "[Diferencial 1 - real y verificable]",
      "[Diferencial 2 - real y verificable]",
      "[Diferencial 3 - real y verificable]"
    ],
    "casos_ejemplo": [
      {
        "situacion": "[Descripción del caso]",
        "como_resolvio_bmc": "[Cómo BMC fue diferente]",
        "resultado": "[Beneficio para el cliente]"
      }
    ],
    "nota": "Definido por el equipo comercial de BMC - [fecha]"
  }
}
```

**Acción 3:** Agregar guardrail en las instrucciones:

```text
# PROPUESTA DE VALOR

Si te preguntan por qué elegir BMC vs competencia:
1. PRIMERO consulta "propuesta_valor_bmc" en la KB
2. Si no está definida, responder:
   "Esta es una pregunta importante que merece una respuesta precisa. 
   Te sugiero que la conversemos con el equipo para darte los diferenciales reales."
3. NUNCA inventar propuestas de valor genéricas
```

---

## ERROR #5: Falta de Memoria de Interacciones

### Descripción del Error
Ramiro preguntó:
> "Ya habíamos interactuado nosotros anteriormente?"

El asistente respondió:
> "En el sentido humano/memoria directa: no tengo registro consciente de una charla previa con vos."

### Impacto
- **Nivel:** MEDIO
- **Afecta:** Personalización, continuidad de entrenamiento
- **Consecuencia:** Cada conversación empieza desde cero sin contexto previo

### Causa Raíz
Los GPT personalizados de OpenAI no tienen memoria persistente entre sesiones (limitación de la plataforma).

### Solución Propuesta

**Acción 1:** Agregar nota en las instrucciones sobre esta limitación:

```text
# MEMORIA Y CONTINUIDAD

- No tengo memoria de conversaciones anteriores entre sesiones
- Si un usuario pregunta si ya hablamos antes, ser honesto:
  "No tengo memoria de conversaciones pasadas entre sesiones, pero puedo 
  aprender de lo que me cuentes en esta conversación."
- Si el usuario quiere continuar un tema anterior, pedir contexto
```

**Acción 2:** Implementar sistema de perfiles de usuario (opcional - desarrollo futuro):
- Crear archivo JSON por usuario conocido
- Almacenar preferencias, historial de temas, correcciones
- Consultar al inicio de cada sesión

```json
{
  "usuarios_conocidos": {
    "Ramiro": {
      "rol": "Equipo de Asesoramientos, Ventas y Soluciones Técnicas",
      "interacciones_previas": true,
      "temas_trabajados": ["definición de BMC", "propuesta de valor", "productos"],
      "correcciones_importantes": [
        "BMC no fabrica, comercializa",
        "Agregar Isofrig PIR y chapas convencionales al catálogo"
      ],
      "estilo_preferido": "Directo, le gusta corregir y profundizar"
    }
  }
}
```

---

## PLAN DE ACCIÓN CONSOLIDADO

### Fase 1: Correcciones Inmediatas (Prioridad CRÍTICA)

| # | Tarea | Responsable | Archivo a Modificar |
|---|-------|-------------|---------------------|
| 1 | Agregar sección "IDENTIDAD BMC URUGUAY" | Dev | `INSTRUCCIONES_PANELIN.txt` |
| 2 | Crear `BMC_IDENTIDAD_EMPRESARIAL.json` | Dev | Nuevo archivo KB |
| 3 | Agregar guardrail de archivos de audio | Dev | `INSTRUCCIONES_PANELIN.txt` |
| 4 | Actualizar catálogo con productos faltantes | Equipo Ventas + Dev | `panelin_truth_bmcuruguay_web_only_v2.json` |

### Fase 2: Definiciones con Equipo Comercial (Prioridad ALTA)

| # | Tarea | Responsable | Entregable |
|---|-------|-------------|------------|
| 5 | Definir propuesta de valor oficial de BMC | Equipo Ventas | Documento con diferenciales reales |
| 6 | Revisar catálogo completo de productos | Equipo Ventas | Lista actualizada de todas las líneas |
| 7 | Crear casos de éxito documentados | Equipo Ventas | 3-5 casos ejemplo |

### Fase 3: Mejoras de Mediano Plazo (Prioridad MEDIA)

| # | Tarea | Responsable | Entregable |
|---|-------|-------------|------------|
| 8 | Implementar perfiles de usuario conocidos | Dev | JSON de perfiles |
| 9 | Agregar sistema de feedback continuo | Dev | Mecanismo para registrar correcciones |
| 10 | Crear proceso de actualización periódica de KB | Dev + Ventas | Proceso documentado |

---

## ARCHIVOS A MODIFICAR

### 1. `gpt_configs/INSTRUCCIONES_PANELIN.txt`
- Agregar sección IDENTIDAD BMC URUGUAY
- Agregar guardrail de archivos de audio
- Agregar guardrail de propuesta de valor
- Agregar nota sobre memoria y continuidad

### 2. `panelin_truth_bmcuruguay_web_only_v2.json`
- Agregar entrada para "chapas_convencionales"
- Agregar entrada para "isofrig_pir"

### 3. Nuevos archivos a crear:
- `BMC_IDENTIDAD_EMPRESARIAL.json` - Definición de la empresa
- `BMC_PROPUESTA_VALOR.json` - Diferenciales competitivos (pendiente input del equipo)
- `BMC_USUARIOS_CONOCIDOS.json` - Perfiles de usuarios internos (opcional)

---

## MÉTRICAS DE ÉXITO

Después de implementar las correcciones:

1. **Test de identidad:** Pregunta "¿A qué se dedica BMC?" → Debe responder "comercializa y asesora", NO "fabrica"
2. **Test de audio:** Subir audio → Debe rechazar transcripción, pedir texto manual
3. **Test de catálogo:** Pregunta "¿Qué productos tienen para paredes?" → Debe incluir Isofrig PIR
4. **Test de propuesta de valor:** Pregunta "¿Por qué elegir BMC?" → Debe consultar KB o indicar que necesita definición oficial

---

## CONCLUSIÓN

Los errores identificados revelan una brecha importante entre lo que Panelin "cree saber" y la realidad operativa de BMC Uruguay. Las correcciones propuestas atacan tanto las causas inmediatas (falta de información en KB) como las estructurales (ausencia de definiciones oficiales).

La implementación de estas correcciones fortalecerá significativamente la credibilidad y utilidad de Panelin como herramienta de apoyo al equipo de ventas.

---

**Documento generado:** 2026-01-24  
**Basado en:** Conversación de entrenamiento con Ramiro  
**Próxima revisión:** Después de implementar Fase 1
