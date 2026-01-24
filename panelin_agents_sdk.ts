import { tool, Agent, AgentInputItem, Runner, withTrace } from "@openai/agents";
import { z } from "zod";
import { OpenAI } from "openai";
import { runGuardrails } from "@openai/guardrails";
import { promises as fs } from "fs";
import path from "path";

// ============================================================================
// TOOL DEFINITIONS
// ============================================================================

const calcularCotizacion = tool({
  name: "calcular_cotizacion",
  description: "Calcula una cotización completa para paneles ISODEC, ISOPANEL, ISOROOF o ISOWALL. Incluye validación técnica de autoportancia, cálculo de materiales y costos con IVA 22%. SIEMPRE usar antes de dar precios.",
  strict: true,
  parameters: z.object({
    producto: z.enum(["ISODEC EPS", "ISODEC PIR", "ISOPANEL EPS", "ISOROOF 3G", "ISOROOF PLUS", "ISOROOF FOIL", "ISOWALL PIR"]),
    espesor: z.string().describe("Espesor del panel en mm (ej: '100', '150', '200')"),
    largo: z.number().describe("Largo del área a cubrir en metros"),
    ancho: z.number().describe("Ancho del área a cubrir en metros"),
    luz: z.number().describe("Distancia entre apoyos (luz) en metros. CRÍTICO para validar autoportancia."),
    tipo_fijacion: z.enum(["hormigon", "metal", "madera"]).describe("Tipo de fijación: 'hormigon' para hormigón, 'metal' para metal, 'madera' para ISOROOF"),
    alero_1: z.number().optional().default(0).describe("Alero en extremo 1 en metros (opcional)"),
    alero_2: z.number().optional().default(0).describe("Alero en extremo 2 en metros (opcional)")
  }),
  execute: async (input: any) => {
    // TODO: Implementar llamada a backend o función Python
    // Por ahora retornar estructura esperada
    return {
      success: true,
      cotizacion: {
        producto: input.producto,
        espesor: input.espesor,
        validacion_autoportancia: {
          cumple: true,
          mensaje: "Validación pendiente de implementación"
        },
        materiales: [],
        total_sin_iva: 0,
        iva: 0,
        total_con_iva: 0
      },
      mensaje: "Cotización calculada. Implementar integración con motor_cotizacion_panelin.py"
    };
  },
});

const buscarEnBaseConocimiento = tool({
  name: "buscar_en_base_conocimiento",
  description: "Busca información en la base de conocimiento de Panelin. Usar para precios, especificaciones técnicas, fórmulas, reglas de negocio. Priorizar BMC_Base_Conocimiento_GPT-2.json (Nivel 1).",
  strict: true,
  parameters: z.object({
    consulta: z.string().describe("Consulta o término a buscar (ej: 'precio ISODEC 100mm', 'autoportancia 150mm', 'fórmula cálculo paneles')"),
    nivel_prioridad: z.enum(["1", "2", "3", "4"]).optional().default("1").describe("Nivel de prioridad: 1=Master, 2=Validación, 3=Dinámico, 4=Soporte")
  }),
  execute: async (input: any) => {
    // TODO: Implementar búsqueda en KB
    return {
      encontrado: true,
      fuente: `Nivel ${input.nivel_prioridad}`,
      resultado: "Búsqueda pendiente de implementación",
      mensaje: "Implementar búsqueda en archivos JSON de Knowledge Base"
    };
  },
});

const evaluarVendedor = tool({
  name: "evaluar_vendedor",
  description: "Evalúa el conocimiento técnico y habilidades de un vendedor basándose en su interacción. Proporciona feedback constructivo.",
  strict: true,
  parameters: z.object({
    nombre_vendedor: z.string().describe("Nombre del vendedor a evaluar"),
    interaccion: z.string().describe("Resumen de la interacción o consulta del vendedor"),
    contexto: z.string().optional().describe("Contexto adicional (ej: 'cotización realizada', 'consulta técnica')")
  }),
  execute: async (input: any) => {
    // TODO: Implementar evaluación
    return {
      evaluacion: {
        conocimiento_tecnico: "Pendiente",
        comprension_autoportancia: "Pendiente",
        habilidades_optimizacion: "Pendiente"
      },
      feedback: "Evaluación pendiente de implementación",
      areas_mejora: []
    };
  },
});

// ============================================================================
// SOP / LEDGER STATE (NO BACKEND: IN-MEMORY, OPTIONAL FILE OUTPUT)
// ============================================================================

type RiesgoDeContexto = "bajo" | "medio" | "alto";
type SopCommand = "/estado" | "/checkpoint" | "/consolidar";

type DeltaType =
  | "product_spec"
  | "product_positioning"
  | "pricing_estimate"
  | "general_info"
  | "terminology"
  | "compliance_safety"
  | "conversation_rule"
  | "conflict"
  | "todo_engineering";

type DeltaSource = {
  message_ref: string;
  excerpt: string;
  who: "user" | "panelin";
  date: string | null;
};

type DeltaItem = {
  id: string;
  type: DeltaType;
  title: string;
  canonical_text: string;
  structured_data: unknown | null;
  applies_to: string[];
  needs_review: boolean;
  confidence: number;
  sources: DeltaSource[];
};

type PanelinSessionState = {
  session_id: string;
  created_at: string;
  last_update: string;
  riesgo_de_contexto: RiesgoDeContexto;
  missing_context: boolean;
  ledger_markdown: string; // contains the full === LEDGER === block
  deltas: DeltaItem[];
  last_checkpoint_delta_index: number;
};

const sessionStore = new Map<string, PanelinSessionState>();

function nowIso(): string {
  return new Date().toISOString();
}

function yyyymmdd(date = new Date()): string {
  const y = date.getUTCFullYear();
  const m = String(date.getUTCMonth() + 1).padStart(2, "0");
  const d = String(date.getUTCDate()).padStart(2, "0");
  return `${y}${m}${d}`;
}

function detectSopCommand(input: string): SopCommand | null {
  const trimmed = input.trim();
  if (trimmed === "/estado" || trimmed === "/checkpoint" || trimmed === "/consolidar") return trimmed;
  return null;
}

function buildEmptyLedgerMarkdown(): string {
  // Mirror the SOP structure in panelin_context_consolidacion_sin_backend.md
  return [
    "=== LEDGER_DE_ENTRENAMIENTO ===",
    "meta:",
    "  locale: es-UY",
    `  last_update: ${nowIso()}`,
    "  riesgo_de_contexto: bajo",
    "  missing_context: false",
    "",
    "product_facts: []",
    "general_info_facts: []",
    "terminology: []",
    "compliance_safety: []",
    "conversation_rules: []",
    "corrections_log: []",
    "conflicts_pending: []",
    "todos_engineering: []",
    "=== FIN LEDGER ===",
    "",
  ].join("\n");
}

function getOrCreateSessionState(sessionId: string): PanelinSessionState {
  const existing = sessionStore.get(sessionId);
  if (existing) return existing;
  const createdAt = nowIso();
  const state: PanelinSessionState = {
    session_id: sessionId,
    created_at: createdAt,
    last_update: createdAt,
    riesgo_de_contexto: "bajo",
    missing_context: false,
    ledger_markdown: buildEmptyLedgerMarkdown(),
    deltas: [],
    last_checkpoint_delta_index: 0,
  };
  sessionStore.set(sessionId, state);
  return state;
}

function jsonlFromDeltas(deltas: DeltaItem[]): string {
  if (!deltas.length) return "";
  return deltas.map((d) => JSON.stringify(d)).join("\n") + "\n";
}

async function maybeWriteFiles(params: {
  writeFiles: boolean;
  sessionId: string;
  files: Array<{ name: string; content: string }>;
}): Promise<{ written: boolean; outputDir?: string; paths?: string[] }> {
  if (!params.writeFiles) return { written: false };
  const outputDir = path.join(process.cwd(), "panelin_exports", params.sessionId, yyyymmdd());
  await fs.mkdir(outputDir, { recursive: true });
  const paths: string[] = [];
  for (const f of params.files) {
    const outPath = path.join(outputDir, f.name);
    await fs.writeFile(outPath, f.content, "utf-8");
    paths.push(outPath);
  }
  return { written: true, outputDir, paths };
}

function buildEstadoResponse(state: PanelinSessionState): string {
  const deltaCount = state.deltas.length;
  const uncheckpointed = Math.max(0, deltaCount - state.last_checkpoint_delta_index);
  return [
    "**/estado — Estado actual**",
    "",
    `- **session_id**: \`${state.session_id}\``,
    `- **last_update**: \`${state.last_update}\``,
    `- **RIESGO_DE_CONTEXTO**: **${state.riesgo_de_contexto}**`,
    `- **missing_context**: **${state.missing_context ? "true" : "false"}**`,
    `- **deltas_totales**: **${deltaCount}**`,
    `- **deltas_desde_último_checkpoint**: **${uncheckpointed}**`,
    "",
    state.riesgo_de_contexto === "alto"
      ? "Ojo: el contexto se está limitando. Te recomiendo hacer **/checkpoint** ahora para no perder nada. ¿Lo hago?"
      : "",
  ]
    .filter(Boolean)
    .join("\n");
}

function buildCheckpointArtifacts(state: PanelinSessionState): { ledgerMd: string; deltasJsonl: string } {
  const deltasSince = state.deltas.slice(state.last_checkpoint_delta_index);
  return {
    ledgerMd: state.ledger_markdown,
    deltasJsonl: jsonlFromDeltas(deltasSince),
  };
}

function buildConsolidarArtifacts(state: PanelinSessionState): {
  kbPackMd: string;
  kbPackJsonl: string;
  consolidatedJson: string;
  patchJson: string;
} {
  const all = state.deltas;
  const pending = all.filter((d) => d.needs_review || d.confidence < 0.7 || d.type === "conflict");
  const merged = all.filter((d) => !pending.includes(d));

  const consolidated = {
    meta: { version: `${new Date().getUTCFullYear()}.${String(new Date().getUTCMonth() + 1).padStart(2, "0")}.${String(new Date().getUTCDate()).padStart(2, "0")}`, generated_at: nowIso(), locale: "es-UY" },
    products: {},
    general_info: {},
    corrections: [],
    terminology: [],
    compliance_safety: [],
    conversation_rules: [],
    change_log: merged,
    pending_changes: pending,
  };

  const countsByType = all.reduce<Record<string, number>>((acc, d) => {
    acc[d.type] = (acc[d.type] ?? 0) + 1;
    return acc;
  }, {});

  const kbPackMd = [
    "# KB_PACK (Panelin)",
    "",
    "## Resumen ejecutivo",
    `- **session_id**: \`${state.session_id}\``,
    `- **generated_at**: \`${nowIso()}\``,
    `- **items_totales**: **${all.length}**`,
    `- **pending_changes**: **${pending.length}**`,
    "",
    "## Conteos por tipo",
    ...Object.entries(countsByType)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([k, v]) => `- **${k}**: ${v}`),
    "",
    "## Items (canónicos)",
    ...all.map((d) => `- **${d.type}** — ${d.title}\n  - ${d.canonical_text}\n  - sources: ${d.sources.map((s) => s.message_ref).join(", ")}`),
    "",
  ].join("\n");

  const kbPackJsonl = jsonlFromDeltas(all);
  const consolidatedJson = JSON.stringify(consolidated, null, 2) + "\n";
  const patchJson = JSON.stringify([], null, 2) + "\n";

  return { kbPackMd, kbPackJsonl, consolidatedJson, patchJson };
}

// ============================================================================
// SHARED CLIENT AND GUARDRAILS
// ============================================================================

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const panelinGuardrailConfig = {
  guardrails: [
    { name: "Jailbreak", config: { model: "gpt-4o-mini", confidence_threshold: 0.7 } },
    { name: "Contains PII", config: { block: false } }, // Anonimizar pero no bloquear
    { name: "Moderation", config: {} }
  ]
};

const context = { guardrailLlm: client };

function guardrailsHasTripwire(results: any[]): boolean {
  return (results ?? []).some((r) => r?.tripwireTriggered === true);
}

function getGuardrailSafeText(results: any[], fallbackText: string): string {
  for (const r of results ?? []) {
    if (r?.info && ("checked_text" in r.info)) {
      return r.info.checked_text ?? fallbackText;
    }
  }
  const pii = (results ?? []).find((r) => r?.info && "anonymized_text" in r.info);
  return pii?.info?.anonymized_text ?? fallbackText;
}

async function scrubConversationHistory(history: any[], piiOnly: any): Promise<void> {
  for (const msg of history ?? []) {
    const content = Array.isArray(msg?.content) ? msg.content : [];
    for (const part of content) {
      if (part && typeof part === "object" && part.type === "input_text" && typeof part.text === "string") {
        const res = await runGuardrails(part.text, piiOnly, context, true);
        part.text = getGuardrailSafeText(res, part.text);
      }
    }
  }
}

async function scrubWorkflowInput(workflow: any, inputKey: string, piiOnly: any): Promise<void> {
  if (!workflow || typeof workflow !== "object") return;
  const value = workflow?.[inputKey];
  if (typeof value !== "string") return;
  const res = await runGuardrails(value, piiOnly, context, true);
  workflow[inputKey] = getGuardrailSafeText(res, value);
}

async function runAndApplyGuardrails(inputText: string, config: any, history: any[], workflow: any) {
  const guardrails = Array.isArray(config?.guardrails) ? config.guardrails : [];
  const results = await runGuardrails(inputText, config, context, true);
  const shouldMaskPII = guardrails.find((g: any) => (g?.name === "Contains PII") && g?.config && g.config.block === false);
  if (shouldMaskPII) {
    const piiOnly = { guardrails: [shouldMaskPII] };
    await scrubConversationHistory(history, piiOnly);
    await scrubWorkflowInput(workflow, "input_as_text", piiOnly);
    await scrubWorkflowInput(workflow, "input_text", piiOnly);
  }
  const hasTripwire = guardrailsHasTripwire(results);
  const safeText = getGuardrailSafeText(results, inputText) ?? inputText;
  return { results, hasTripwire, safeText, failOutput: buildGuardrailFailOutput(results ?? []), passOutput: { safe_text: safeText } };
}

function buildGuardrailFailOutput(results: any[]) {
  const get = (name: string) => (results ?? []).find((r: any) => ((r?.info?.guardrail_name ?? r?.info?.guardrailName) === name));
  const pii = get("Contains PII"), mod = get("Moderation"), jb = get("Jailbreak"), hal = get("Hallucination Detection"), nsfw = get("NSFW Text"), url = get("URL Filter"), custom = get("Custom Prompt Check"), pid = get("Prompt Injection Detection");
  const detected = (pii?.info?.detected_entities ?? {}) as Record<string, unknown>;
  const piiCounts = Object.entries(detected)
    .filter(([, v]) => Array.isArray(v))
    .map(([k, v]) => `${k}:${(v as unknown[]).length}`);
  return {
    pii: { failed: (piiCounts.length > 0) || pii?.tripwireTriggered === true, detected_counts: piiCounts },
    moderation: { failed: mod?.tripwireTriggered === true || ((mod?.info?.flagged_categories ?? []).length > 0), flagged_categories: mod?.info?.flagged_categories },
    jailbreak: { failed: jb?.tripwireTriggered === true },
    hallucination: { failed: hal?.tripwireTriggered === true, reasoning: hal?.info?.reasoning },
    nsfw: { failed: nsfw?.tripwireTriggered === true },
    url_filter: { failed: url?.tripwireTriggered === true },
    custom_prompt_check: { failed: custom?.tripwireTriggered === true },
    prompt_injection: { failed: pid?.tripwireTriggered === true },
  };
}

// ============================================================================
// AGENT DEFINITIONS
// ============================================================================

const ClassificationAgentSchema = z.object({
  classification: z.enum(["cotizacion", "evaluacion_entrenamiento", "informacion", "comando_sop"]),
  nombre_usuario: z.string().optional().describe("Nombre del usuario si se menciona (Mauro, Martin, Rami, u otro)")
});

const classificationAgent = new Agent({
  name: "Classification agent",
  instructions: `Clasifica la intención del usuario en una de las siguientes categorías:

1. **cotizacion**: Cualquier solicitud de cotización, precio, presupuesto, cálculo de materiales, validación técnica de paneles
2. **evaluacion_entrenamiento**: Solicitudes de evaluación de vendedores, entrenamiento, feedback sobre habilidades de ventas, comandos /evaluar_ventas o /entrenar
3. **informacion**: Consultas informativas sobre productos, especificaciones técnicas, diferencias entre productos, reglas de negocio, preguntas generales
4. **comando_sop**: Comandos especiales como /estado, /checkpoint, /consolidar

**Personalización**: Si detectas nombres específicos (Mauro, Martin, Rami), extrae el nombre_usuario para personalización posterior.

**Reglas**:
- Si menciona "cotizar", "precio", "presupuesto", "cuánto cuesta" → cotizacion
- Si menciona "evaluar", "entrenar", "feedback" → evaluacion_entrenamiento
- Si menciona comandos con "/" → comando_sop
- Todo lo demás → informacion`,
  model: "gpt-4o-mini",
  outputType: ClassificationAgentSchema,
  modelSettings: {
    temperature: 0.7,
    topP: 1,
    maxTokens: 2048,
    store: true
  }
});

const cotizacionAgent = new Agent({
  name: "Cotización Agent",
  instructions: `Eres Panelin, experto técnico en cotizaciones de sistemas constructivos BMC.

**PROCESO DE COTIZACIÓN (5 FASES)**:

**FASE 1 - IDENTIFICACIÓN**: Extrae producto, espesor, largo, ancho, luz (distancia entre apoyos), tipo de fijación. SIEMPRE pregunta la luz si falta.

**FASE 2 - VALIDACIÓN TÉCNICA**: Usa calcular_cotizacion() que valida autoportancia automáticamente. Si NO cumple, sugiere espesor mayor o apoyo adicional.

**FASE 3 - RECUPERACIÓN DE DATOS**: calcular_cotizacion() obtiene precios de la base de conocimiento (Nivel 1: BMC_Base_Conocimiento_GPT-2.json).

**FASE 4 - CÁLCULOS**: calcular_cotizacion() usa fórmulas exactas del JSON. Incluye análisis de ahorro energético en comparativas.

**FASE 5 - PRESENTACIÓN**: Presenta desglose detallado, IVA 22%, total, recomendaciones técnicas, análisis de valor a largo plazo.

**REGLAS CRÍTICAS**:
- NUNCA inventes precios. SIEMPRE usa calcular_cotizacion() o buscar_en_base_conocimiento()
- SIEMPRE pregunta la luz (distancia entre apoyos) si falta
- Valida autoportancia antes de cotizar
- En comparativas, incluye SIEMPRE análisis de aislamiento térmico y ahorro energético
- Moneda: USD | IVA: 22% (aclarar si incluido)
- Estructura estándar: ISODEC/ISOPANEL → hormigón (varilla+tuerca+tacos). ISOROOF → madera (caballetes+tornillos)

**ESTILO**: Español rioplatense. Profesional, técnico pero accesible. Actúa como ingeniero experto, no calculador.`,
  model: "gpt-4o-mini",
  tools: [
    calcularCotizacion,
    buscarEnBaseConocimiento
  ],
  modelSettings: {
    temperature: 0.7,
    topP: 1,
    parallelToolCalls: true,
    maxTokens: 4096,
    store: true
  }
});

const evaluacionEntrenamientoAgent = new Agent({
  name: "Evaluación y Entrenamiento Agent",
  instructions: `Eres Panelin, experto en evaluación y entrenamiento de personal de ventas para sistemas constructivos BMC.

**EVALUACIÓN**:
- Evalúa conocimiento técnico sobre productos (ISODEC, ISOPANEL, ISOROOF, ISOWALL)
- Evalúa comprensión de autoportancia y espesores
- Evalúa sistemas de fijación
- Evalúa capacidad de identificar necesidades del cliente
- Evalúa habilidades de optimización de soluciones

**ENTRENAMIENTO**:
- Proporciona feedback constructivo
- Simula escenarios de cotización
- Basa entrenamiento en interacciones históricas, cotizaciones exitosas, patrones de consultas
- Proceso: ANALIZAR → IDENTIFICAR → GENERAR → EVALUAR → ITERAR

**HERRAMIENTAS**:
- Usa evaluar_vendedor() para evaluaciones estructuradas
- Usa buscar_en_base_conocimiento() para consultar información técnica

**ESTILO**: Español rioplatense. Constructivo, educativo, profesional.`,
  model: "gpt-4o-mini",
  tools: [
    evaluarVendedor,
    buscarEnBaseConocimiento
  ],
  modelSettings: {
    temperature: 0.7,
    topP: 1,
    parallelToolCalls: true,
    maxTokens: 4096,
    store: true
  }
});

const informacionAgent = new Agent({
  name: "Information Agent",
  instructions: `Eres Panelin, experto técnico en sistemas constructivos BMC. Respondes consultas informativas sobre productos, especificaciones técnicas, reglas de negocio.

**FUENTE DE VERDAD**:
- SIEMPRE consulta buscar_en_base_conocimiento() antes de responder
- Prioridad: Nivel 1 (BMC_Base_Conocimiento_GPT-2.json) → Nivel 2 → Nivel 3 → Nivel 4
- NUNCA inventes información que no esté en la base de conocimiento
- Si no está: "No tengo esa información en mi base de conocimiento"

**TEMAS**:
- Productos: ISODEC, ISOPANEL, ISOROOF, ISOWALL
- Diferencias entre EPS y PIR
- Espesores disponibles y aplicaciones
- Autoportancia y validación técnica
- Sistemas de fijación (hormigón, metal, madera)
- Coeficientes térmicos y resistencia térmica
- Reglas de negocio (IVA 22%, pendiente mínima 7%, etc.)
- Fórmulas de cálculo

**ESTILO**: Español rioplatense. Profesional, técnico pero accesible. Usa negritas y listas. Si algo técnico no está claro: "Lo consulto con ingeniería".`,
  model: "gpt-4o-mini",
  tools: [
    buscarEnBaseConocimiento
  ],
  modelSettings: {
    temperature: 0.7,
    topP: 1,
    maxTokens: 4096,
    store: true
  }
});

// ============================================================================
// LEDGER UPDATE AGENT (LLM-ASSISTED)
// ============================================================================

const LedgerUpdateOutputSchema = z.object({
  riesgo_de_contexto: z.enum(["bajo", "medio", "alto"]),
  missing_context: z.boolean(),
  ledger_markdown: z
    .string()
    .describe("Debe contener el Ledger COMPLETO con los delimitadores === LEDGER_DE_ENTRENAMIENTO === y === FIN LEDGER ==="),
  delta: z
    .object({
      id: z.string(),
      type: z.enum([
        "product_spec",
        "product_positioning",
        "pricing_estimate",
        "general_info",
        "terminology",
        "compliance_safety",
        "conversation_rule",
        "conflict",
        "todo_engineering",
      ]),
      title: z.string(),
      canonical_text: z.string(),
      structured_data: z.unknown().nullable(),
      applies_to: z.array(z.string()),
      needs_review: z.boolean(),
      confidence: z.number(),
      sources: z.array(
        z.object({
          message_ref: z.string(),
          excerpt: z.string(),
          who: z.enum(["user", "panelin"]),
          date: z.string().nullable(),
        })
      ),
    })
    .nullable(),
});

type LedgerUpdateOutput = z.infer<typeof LedgerUpdateOutputSchema>;

const ledgerUpdateAgent = new Agent({
  name: "Ledger update agent",
  instructions: `Sos Panelin (modo SOP). Tu tarea es SOLO mantener un Ledger incremental y, si corresponde, generar un único "delta".

Reglas:
- No inventes datos ni precios.
- Si el input no agrega información útil, podés devolver delta=null.
- Tenés que devolver el Ledger COMPLETO con el mismo formato y delimitadores.
- Actualizá meta.last_update y meta.riesgo_de_contexto (bajo|medio|alto) y meta.missing_context (true|false).
- Si detectás una corrección/contradicción o algo ambiguo, marcá needs_review=true y/o tipo conflict.

Taxonomía permitida para delta.type:
product_spec, product_positioning, pricing_estimate, general_info, terminology, compliance_safety, conversation_rule, conflict, todo_engineering.

Si generás delta:
- id: DELTA-<YYYYMMDD>-<SEQ> (si no sabés el seq, poné 001)
- sources: al menos un source con message_ref (ej: msg_latest_user) y excerpt corto.

Salida: respondé SOLO con JSON válido según el schema.`,
  model: "gpt-4o-mini",
  outputType: LedgerUpdateOutputSchema,
  modelSettings: {
    temperature: 0.2,
    topP: 1,
    maxTokens: 4096,
    store: true,
  },
});

// ============================================================================
// PERSONALIZATION LOGIC
// ============================================================================

function aplicarPersonalizacion(nombreUsuario: string | undefined, mensajeInicial: string): string {
  if (!nombreUsuario) return mensajeInicial;

  const nombreLower = nombreUsuario.toLowerCase().trim();

  if (nombreLower === "mauro") {
    return `${mensajeInicial}\n\n[Mensaje personalizado para Mauro: Respuesta única, guiada por concepto, nunca prearmada. Lo conoces, escuchaste sus canciones, es medio rarito.]`;
  } else if (nombreLower === "martin") {
    return `${mensajeInicial}\n\n[Mensaje personalizado para Martin: Respuesta única. Aunque no crea en IA, le ayudarás a resolver problemas y ahorrar tiempo.]`;
  } else if (nombreLower === "rami") {
    return `${mensajeInicial}\n\n[Mensaje personalizado para Rami: Respuesta única. Ponerte a prueba, sabes que puede exigir más.]`;
  }

  return mensajeInicial;
}

// ============================================================================
// MAIN WORKFLOW
// ============================================================================

type WorkflowInput = {
  input_as_text: string;
  session_id?: string;
  reset_session?: boolean;
  write_files?: boolean; // if true, writes exports to ./panelin_exports/<session>/<YYYYMMDD>/
};

export const runWorkflow = async (workflow: WorkflowInput): Promise<any> => {
  return await withTrace("Panelin Agent Workflow", async () => {
    const sessionId = (workflow.session_id ?? "default").trim() || "default";
    if (workflow.reset_session) sessionStore.delete(sessionId);
    const sessionState = getOrCreateSessionState(sessionId);

    const conversationHistory: AgentInputItem[] = [
      { role: "user", content: [{ type: "input_text", text: workflow.input_as_text }] }
    ];

    const runner = new Runner({
      traceMetadata: {
        __trace_source__: "panelin-agent-builder",
        workflow_id: "panelin_wf_" + Date.now().toString(36)
      }
    });

    // Apply guardrails
    const guardrailsInputText = workflow.input_as_text;
    const { hasTripwire: guardrailsHasTripwire, safeText: guardrailsAnonymizedText, failOutput: guardrailsFailOutput, passOutput: guardrailsPassOutput } = await runAndApplyGuardrails(guardrailsInputText, panelinGuardrailConfig, conversationHistory, workflow);
    const guardrailsOutput = (guardrailsHasTripwire ? guardrailsFailOutput : guardrailsPassOutput);

    if (guardrailsHasTripwire) {
      return guardrailsOutput;
    }

    const command = detectSopCommand(workflow.input_as_text);
    if (command) {
      if (command === "/estado") {
        return {
          classification: "comando_sop",
          nombre_usuario: undefined,
          respuesta: buildEstadoResponse(sessionState),
        };
      }

      if (command === "/checkpoint") {
        const { ledgerMd, deltasJsonl } = buildCheckpointArtifacts(sessionState);
        const filesToWrite = [
          { name: "LEDGER_SNAPSHOT.md", content: ledgerMd },
          { name: "DELTAS_SIN_MERGE.jsonl", content: deltasJsonl },
        ];
        const writeRes = await maybeWriteFiles({ writeFiles: Boolean(workflow.write_files), sessionId, files: filesToWrite });
        sessionState.last_checkpoint_delta_index = sessionState.deltas.length;
        sessionState.last_update = nowIso();

        const fileNote = writeRes.written
          ? `Archivos escritos en:\n- \`${writeRes.outputDir}\`\n- ${writeRes.paths?.map((p) => `\`${p}\``).join("\n- ") ?? ""}`
          : "No puedo adjuntar archivos acá. Copiá estos bloques y guardalos con estos nombres: `LEDGER_SNAPSHOT.md`, `DELTAS_SIN_MERGE.jsonl`.";

        return {
          classification: "comando_sop",
          nombre_usuario: undefined,
          respuesta: [
            "**/checkpoint — Exportación**",
            "",
            "**A) TEXTO PEGADO**",
            "Archivo: `LEDGER_SNAPSHOT.md`",
            "```md",
            ledgerMd.trimEnd(),
            "```",
            "",
            "Archivo: `DELTAS_SIN_MERGE.jsonl`",
            "```jsonl",
            (deltasJsonl || "").trimEnd(),
            "```",
            "",
            "**B) ARCHIVOS**",
            fileNote,
          ].join("\n"),
        };
      }

      if (command === "/consolidar") {
        const { kbPackMd, kbPackJsonl, consolidatedJson, patchJson } = buildConsolidarArtifacts(sessionState);
        const filesToWrite = [
          { name: "KB_PACK.md", content: kbPackMd },
          { name: "KB_PACK.jsonl", content: kbPackJsonl },
          { name: "BMC_TECHNICAL_TRUTH_CONSOLIDATED.json", content: consolidatedJson },
          { name: "PATCH.json", content: patchJson },
        ];
        const writeRes = await maybeWriteFiles({ writeFiles: Boolean(workflow.write_files), sessionId, files: filesToWrite });
        sessionState.last_update = nowIso();

        const fileNote = writeRes.written
          ? `Archivos escritos en:\n- \`${writeRes.outputDir}\`\n- ${writeRes.paths?.map((p) => `\`${p}\``).join("\n- ") ?? ""}`
          : "No puedo adjuntar archivos acá. Copiá estos bloques y guardalos con estos nombres: `KB_PACK.md`, `KB_PACK.jsonl`, `BMC_TECHNICAL_TRUTH_CONSOLIDATED.json`, `PATCH.json`.";

        return {
          classification: "comando_sop",
          nombre_usuario: undefined,
          respuesta: [
            "**/consolidar — Exportación completa**",
            "",
            "**A) TEXTO PEGADO**",
            "Archivo: `KB_PACK.md`",
            "```md",
            kbPackMd.trimEnd(),
            "```",
            "",
            "Archivo: `KB_PACK.jsonl`",
            "```jsonl",
            (kbPackJsonl || "").trimEnd(),
            "```",
            "",
            "Archivo: `BMC_TECHNICAL_TRUTH_CONSOLIDATED.json`",
            "```json",
            consolidatedJson.trimEnd(),
            "```",
            "",
            "Archivo: `PATCH.json`",
            "```json",
            patchJson.trimEnd(),
            "```",
            "",
            "**B) ARCHIVOS**",
            fileNote,
          ].join("\n"),
        };
      }
    }

    // Classification
    const classificationAgentResultTemp = await runner.run(
      classificationAgent,
      [...conversationHistory]
    );
    conversationHistory.push(...classificationAgentResultTemp.newItems.map((item) => item.rawItem));

    if (!classificationAgentResultTemp.finalOutput) {
      throw new Error("Classification agent result is undefined");
    }

    const classificationAgentResult = {
      output_text: JSON.stringify(classificationAgentResultTemp.finalOutput),
      output_parsed: classificationAgentResultTemp.finalOutput
    };

    const nombreUsuario = classificationAgentResult.output_parsed.nombre_usuario;
    const classification = classificationAgentResult.output_parsed.classification;

    let respuestaBase = "";
    let nota: string | undefined;

    if (classification === "cotizacion") {
      const cotizacionAgentResultTemp = await runner.run(cotizacionAgent, [...conversationHistory]);
      conversationHistory.push(...cotizacionAgentResultTemp.newItems.map((item) => item.rawItem));
      if (!cotizacionAgentResultTemp.finalOutput) throw new Error("Cotización agent result is undefined");
      respuestaBase = cotizacionAgentResultTemp.finalOutput ?? "";
    } else if (classification === "evaluacion_entrenamiento") {
      const evaluacionAgentResultTemp = await runner.run(evaluacionEntrenamientoAgent, [...conversationHistory]);
      conversationHistory.push(...evaluacionAgentResultTemp.newItems.map((item) => item.rawItem));
      if (!evaluacionAgentResultTemp.finalOutput) throw new Error("Evaluación agent result is undefined");
      respuestaBase = evaluacionAgentResultTemp.finalOutput ?? "";
    } else if (classification === "informacion") {
      const informacionAgentResultTemp = await runner.run(informacionAgent, [...conversationHistory]);
      conversationHistory.push(...informacionAgentResultTemp.newItems.map((item) => item.rawItem));
      if (!informacionAgentResultTemp.finalOutput) throw new Error("Información agent result is undefined");
      respuestaBase = informacionAgentResultTemp.finalOutput ?? "";
    } else if (classification === "comando_sop") {
      // If user wrote a command but also text, try to interpret the first token.
      const maybeCmd = detectSopCommand(workflow.input_as_text.split(/\s+/)[0] ?? "");
      if (maybeCmd) {
        // Re-run through deterministic SOP handler for consistency.
        const routed = await runWorkflow({ ...workflow, input_as_text: maybeCmd, session_id: sessionId, write_files: workflow.write_files });
        return routed;
      }
      const informacionAgentResultTemp = await runner.run(informacionAgent, [...conversationHistory]);
      conversationHistory.push(...informacionAgentResultTemp.newItems.map((item) => item.rawItem));
      if (!informacionAgentResultTemp.finalOutput) throw new Error("SOP command agent result is undefined");
      respuestaBase = informacionAgentResultTemp.finalOutput ?? "";
      nota = "Si querías exportar, usá exactamente: /estado, /checkpoint o /consolidar";
    } else {
      return classificationAgentResult;
    }

    const respuestaPersonalizada = aplicarPersonalizacion(nombreUsuario, respuestaBase);

    // Update ledger state after non-SOP interactions (best-effort).
    try {
      const seq = String(sessionState.deltas.length + 1).padStart(3, "0");
      const prompt = [
        "LEDGER_ACTUAL:",
        sessionState.ledger_markdown,
        "",
        "NUEVO_TURNO:",
        `- user: ${workflow.input_as_text}`,
        `- panelin: ${respuestaPersonalizada}`,
        "",
        `Sugerencia para delta.id (si corresponde): DELTA-${yyyymmdd()}-${seq}`,
        "message_ref sugerido: msg_latest_user",
      ].join("\n");
      const ledgerResultTemp = await runner.run(ledgerUpdateAgent, [{ role: "user", content: [{ type: "input_text", text: prompt }] }]);
      if (ledgerResultTemp.finalOutput) {
        const out = ledgerResultTemp.finalOutput as LedgerUpdateOutput;
        sessionState.ledger_markdown = out.ledger_markdown;
        sessionState.riesgo_de_contexto = out.riesgo_de_contexto;
        sessionState.missing_context = out.missing_context;
        sessionState.last_update = nowIso();
        if (out.delta) {
          // Ensure id matches our convention if model left default.
          const delta: DeltaItem = {
            ...out.delta,
            id: out.delta.id || `DELTA-${yyyymmdd()}-${seq}`,
          } as DeltaItem;
          sessionState.deltas.push(delta);
        }
      }
    } catch {
      // Ledger update is best-effort; never block user response.
    }

    return {
      classification,
      nombre_usuario: nombreUsuario,
      respuesta: respuestaPersonalizada,
      nota,
    };
  });
};
