# Caso de entrenamiento (Leaks / Errores) — Conversación Ramiro ↔ Panelin (2026-01-24)

## Objetivo
Convertir la conversación exportada en una **base de conocimiento de errores**: qué falló, por qué falló y cómo se corrige (instrucciones, datos y flujo de conversación).

## Contexto resumido
- El usuario consulta: **a qué se dedica BMC Uruguay** y **qué función cumple Panelin**.
- El usuario (Ramiro, ventas/asesoramiento) corrige una afirmación clave: **BMC no fabrica**; **comercializa/suministra y asesora**.
- Luego aparece un **audio**: el asistente primero afirma que puede escucharlo, después dice que no puede, y finalmente “transcribe aproximado”.
- Más adelante el usuario pide: **por qué elegirían BMC vs competencia**; la respuesta queda percibida como genérica / no alineada.

## Hechos corregidos (Source of Truth para este caso)
Estos son los datos que se deben considerar verdaderos en el contexto del chat:
- **BMC Uruguay NO fabrica**: **suministra/comercializa** materiales y **asesora técnicamente** la solución según proyecto (obra nueva o reforma).
- **Portafolio** (según la conversación): techos/cubiertas (Isodec EPS/PIR, Isoroof, chapas convencionales, otros sistemas) y paredes/fachadas (Isopanel EPS, Isowall PIR, Isofrig PIR).
- **Diferencial**: no es “vender paneles”, sino **brindar soluciones técnicas optimizadas** para confort, ahorro de presupuesto/estructura, tiempos de obra y prevención de problemas futuros.

## Errores detectados (qué pasó)

### Error 1 — Error factual: “BMC fabrica”
- **Qué dijo el asistente**: “BMC Uruguay se dedica a la fabricación y comercialización…”
- **Por qué es un error**: contradice la corrección explícita del usuario: **BMC comercializa/suministra y asesora**.
- **Causa raíz probable**:
  - KB incompleta o desactualizada sobre “quiénes somos”.
  - Tendencia del modelo a “completar” perfiles empresariales con un patrón típico del rubro.
- **Riesgo**: erosiona confianza interna (equipo BMC) y externa (cliente), y puede generar claims incorrectos.

### Error 2 — Gestión inconsistente de capacidades: audio
- **Qué pasó**:
  1) El asistente afirma: “Puedo escucharlo y analizarlo”.
  2) Luego afirma: “En este entorno no puedo escuchar audios…”
  3) Finalmente entrega una “transcripción aproximada”.
- **Por qué es un error**: inconsistencia operacional + promesa de capacidad no garantizada.
- **Causa raíz probable**:
  - No existe una regla dura de “capability check” antes de prometer una acción.
  - Falta de SOP para inputs no textuales (audio) y su tratamiento.
- **Riesgo**: el usuario percibe improvisación; además se crean “datos” que nunca estuvieron (alucinación).

### Error 3 — Manejo de memoria/personalización (expectativas)
- **Qué dijo el asistente**: “no tengo registro…”, pero luego sugiere familiaridad (“hablás como alguien que ya viene…”).
- **Por qué es un error**: aunque sea estilístico, puede leerse como “sí recuerda” o como contradicción.
- **Causa raíz probable**:
  - Falta de guideline para responder “¿ya hablamos antes?” sin ambigüedad.
- **Riesgo**: expectativa falsa de memoria + fricción (“¿me conoce o no?”).

### Error 4 — Evaluación “4/5” sin rubric alineado
- **Qué pasó**: el usuario acepta el resumen del audio pero rechaza la conclusión.
- **Causa raíz probable**:
  - No existe un **rubric interno** (qué es “bien” para BMC) o no se consultó.
  - El asistente evalúa con criterios genéricos.
- **Riesgo**: feedback percibido como poco útil / no aplicable al estilo BMC.

### Error 5 — “Por qué elegirían BMC” respondido con generalidades
- **Qué dijo el asistente**: lista de atributos consultivos (“reduce riesgo”, “optimiza costo total”…).
- **Por qué puede fallar**: sin anclaje en **pruebas concretas** (servicios, procesos, garantías, logística, soporte, alcance de asesoramiento), suena a marketing estándar.
- **Causa raíz probable**:
  - Falta de “propuesta de valor” versionada en KB.
  - Falta de regla de “pedir contexto” (tipo de cliente, proyecto, industria, urgencia, problema) antes de argumentar.

## Soluciones propuestas (qué cambiar)

### A) Datos / KB (contenido)
- **Agregar/asegurar un bloque “Quiénes somos”** (BMC Uruguay):
  - “No fabricamos; comercializamos/suministramos y asesoramos soluciones.”
  - Portafolio por líneas (techo/pared; EPS/PIR; cámaras/frío si aplica).
  - Diferencial en términos operativos (qué hacemos en el proceso, no adjetivos).

### B) Reglas de conversación (SOP)
- **Regla: capability check**
  - Nunca afirmar “puedo escuchar/transcribir” si no hay pipeline confirmado.
  - Si llega audio: pedir texto o habilitar explícitamente una herramienta de transcripción (si existe).
- **Regla: corrección del usuario = actualización inmediata del marco**
  - Reconocer, ajustar respuesta futura y evitar volver al claim incorrecto.
- **Regla: “ya hablamos antes”**
  - Responder sin ambigüedad: “no tengo historial persistente en este chat; si me das contexto, continúo”.
- **Regla: diferenciación competitiva**
  - Primero preguntar 2–4 datos (tipo de obra, prioridad: costo/tiempo/fuego/aislación, perfil del cliente, plazo).
  - Luego argumentar con pilares verificables (servicio/proceso/evidencia) + un cierre con siguiente paso.

### C) Rubric de feedback (ventas/asesoramiento)
Definir un rubric mínimo para evaluar audios/speeches:
- **Apertura**: encuadre correcto (BMC = asesoramiento + suministro).
- **Diagnóstico**: preguntas clave (luz, uso, riesgo incendio, condensación, presupuesto total).
- **Anclaje técnico**: 1–2 fundamentos simples (autoportancia, aislación, fuego).
- **Cierre**: micro-CTA (“¿me confirmás luz y ubicación para recomendar?”).

## Plan de acción (implementable)
1) **Corregir estructura del repositorio**: asegurar carpeta `Files/` (sin espacios) para que los scripts encuentren KB.
2) **Crear bundle de entrenamiento** con esta conversación, anotando:
   - intents
   - mensajes que requieren KB
   - errores del asistente (tags) y “respuesta objetivo” (golden response)
3) **Agregar un “SOP Audio”**: qué se puede y qué no se puede hacer con `.ogg`.
4) **Agregar un “SOP Diferencial BMC”**: preguntas previas + argumentos verificables.

