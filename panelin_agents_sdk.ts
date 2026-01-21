import { tool, Agent, AgentInputItem, Runner, withTrace } from "@openai/agents";
import { z } from "zod";
import { OpenAI } from "openai";
import { runGuardrails } from "@openai/guardrails";

// ============================================================================
// TOOL DEFINITIONS
// ============================================================================

const calcularCotizacion = tool({
  name: "calcular_cotizacion",
  description: "Calcula una cotización completa para paneles ISODEC, ISOPANEL, ISOROOF o ISOWALL. Incluye validación técnica de autoportancia, cálculo de materiales y costos con IVA 22%. SIEMPRE usar antes de dar precios.",
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
  execute: async (input: {
    producto: string;
    espesor: string;
    largo: number;
    ancho: number;
    luz: number;
    tipo_fijacion: string;
    alero_1?: number;
    alero_2?: number;
  }) => {
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
  parameters: z.object({
    consulta: z.string().describe("Consulta o término a buscar (ej: 'precio ISODEC 100mm', 'autoportancia 150mm', 'fórmula cálculo paneles')"),
    nivel_prioridad: z.enum(["1", "2", "3", "4"]).optional().default("1").describe("Nivel de prioridad: 1=Master, 2=Validación, 3=Dinámico, 4=Soporte")
  }),
  execute: async (input: { consulta: string; nivel_prioridad?: string }) => {
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
  parameters: z.object({
    nombre_vendedor: z.string().describe("Nombre del vendedor a evaluar"),
    interaccion: z.string().describe("Resumen de la interacción o consulta del vendedor"),
    contexto: z.string().optional().describe("Contexto adicional (ej: 'cotización realizada', 'consulta técnica')")
  }),
  execute: async (input: { nombre_vendedor: string; interaccion: string; contexto?: string }) => {
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
  const shouldMaskPII = guardrails.find((g) => (g?.name === "Contains PII") && g?.config && g.config.block === false);
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
  const piiCounts = Object.entries(pii?.info?.detected_entities ?? {}).filter(([, v]) => Array.isArray(v)).map(([k, v]) => k + ":" + v.length);
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

type WorkflowInput = { input_as_text: string };

export const runWorkflow = async (workflow: WorkflowInput) => {
  return await withTrace("Panelin Agent Workflow", async () => {
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

    // Route to appropriate agent
    if (classification === "cotizacion") {
      const cotizacionAgentResultTemp = await runner.run(
        cotizacionAgent,
        [...conversationHistory]
      );
      conversationHistory.push(...cotizacionAgentResultTemp.newItems.map((item) => item.rawItem));

      if (!cotizacionAgentResultTemp.finalOutput) {
        throw new Error("Cotización agent result is undefined");
      }

      const cotizacionAgentResult = {
        output_text: cotizacionAgentResultTemp.finalOutput ?? ""
      };

      // Apply personalization if needed
      const resultadoFinal = aplicarPersonalizacion(nombreUsuario, cotizacionAgentResult.output_text);

      return {
        classification: "cotizacion",
        nombre_usuario: nombreUsuario,
        respuesta: resultadoFinal
      };
    } else if (classification === "evaluacion_entrenamiento") {
      const evaluacionAgentResultTemp = await runner.run(
        evaluacionEntrenamientoAgent,
        [...conversationHistory]
      );
      conversationHistory.push(...evaluacionAgentResultTemp.newItems.map((item) => item.rawItem));

      if (!evaluacionAgentResultTemp.finalOutput) {
        throw new Error("Evaluación agent result is undefined");
      }

      const evaluacionAgentResult = {
        output_text: evaluacionAgentResultTemp.finalOutput ?? ""
      };

      const resultadoFinal = aplicarPersonalizacion(nombreUsuario, evaluacionAgentResult.output_text);

      return {
        classification: "evaluacion_entrenamiento",
        nombre_usuario: nombreUsuario,
        respuesta: resultadoFinal
      };
    } else if (classification === "informacion") {
      const informacionAgentResultTemp = await runner.run(
        informacionAgent,
        [...conversationHistory]
      );
      conversationHistory.push(...informacionAgentResultTemp.newItems.map((item) => item.rawItem));

      if (!informacionAgentResultTemp.finalOutput) {
        throw new Error("Información agent result is undefined");
      }

      const informacionAgentResult = {
        output_text: informacionAgentResultTemp.finalOutput ?? ""
      };

      const resultadoFinal = aplicarPersonalizacion(nombreUsuario, informacionAgentResult.output_text);

      return {
        classification: "informacion",
        nombre_usuario: nombreUsuario,
        respuesta: resultadoFinal
      };
    } else if (classification === "comando_sop") {
      // Handle SOP commands (/estado, /checkpoint, /consolidar, etc.)
      // For now, route to information agent
      const informacionAgentResultTemp = await runner.run(
        informacionAgent,
        [...conversationHistory]
      );
      conversationHistory.push(...informacionAgentResultTemp.newItems.map((item) => item.rawItem));

      if (!informacionAgentResultTemp.finalOutput) {
        throw new Error("SOP command agent result is undefined");
      }

      return {
        classification: "comando_sop",
        nombre_usuario: nombreUsuario,
        respuesta: informacionAgentResultTemp.finalOutput ?? "",
        nota: "Comandos SOP requieren implementación específica según documentación"
      };
    } else {
      // Fallback
      return classificationAgentResult;
    }
  });
};
