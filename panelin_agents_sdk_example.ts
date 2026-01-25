/**
 * Panelin Agents SDK - Ejemplo de Uso
 * 
 * Este archivo muestra cómo usar el sistema de agentes de Panelin
 */

import { runWorkflow } from "./panelin_agents_sdk";

const DEMO_SESSION_ID = "demo_panelin_sdk";

// ============================================================================
// EJEMPLO 1: COTIZACIÓN BÁSICA
// ============================================================================

async function ejemploCotizacion() {
  console.log("=".repeat(70));
  console.log("EJEMPLO 1: Cotización Básica");
  console.log("=".repeat(70));

  const resultado = await runWorkflow({
    input_as_text: "Necesito cotizar ISODEC 100mm para un techo de 10m x 5m, con luz de 4m entre apoyos, fijación a hormigón",
    session_id: DEMO_SESSION_ID
  });

  console.log("\n📋 Clasificación:", resultado.classification);
  console.log("👤 Usuario:", resultado.nombre_usuario || "No identificado");
  console.log("\n💬 Respuesta:\n", resultado.respuesta);
  console.log("\n");
}

// ============================================================================
// EJEMPLO 2: COTIZACIÓN CON FALTANTE DE DATOS (debe preguntar luz)
// ============================================================================

async function ejemploCotizacionIncompleta() {
  console.log("=".repeat(70));
  console.log("EJEMPLO 2: Cotización Incompleta (falta luz)");
  console.log("=".repeat(70));

  const resultado = await runWorkflow({
    input_as_text: "Quiero cotizar ISODEC 150mm para un techo de 8m x 6m",
    session_id: DEMO_SESSION_ID
  });

  console.log("\n📋 Clasificación:", resultado.classification);
  console.log("\n💬 Respuesta:\n", resultado.respuesta);
  console.log("\n");
}

// ============================================================================
// EJEMPLO 3: CONSULTA INFORMATIVA
// ============================================================================

async function ejemploInformacion() {
  console.log("=".repeat(70));
  console.log("EJEMPLO 3: Consulta Informativa");
  console.log("=".repeat(70));

  const resultado = await runWorkflow({
    input_as_text: "¿Cuál es la diferencia entre ISODEC EPS e ISODEC PIR? ¿Cuándo debo usar cada uno?",
    session_id: DEMO_SESSION_ID
  });

  console.log("\n📋 Clasificación:", resultado.classification);
  console.log("\n💬 Respuesta:\n", resultado.respuesta);
  console.log("\n");
}

// ============================================================================
// EJEMPLO 4: PERSONALIZACIÓN (Mauro)
// ============================================================================

async function ejemploPersonalizacionMauro() {
  console.log("=".repeat(70));
  console.log("EJEMPLO 4: Personalización - Mauro");
  console.log("=".repeat(70));

  const resultado = await runWorkflow({
    input_as_text: "Hola, mi nombre es Mauro. Necesito información sobre autoportancia",
    session_id: DEMO_SESSION_ID
  });

  console.log("\n📋 Clasificación:", resultado.classification);
  console.log("👤 Usuario:", resultado.nombre_usuario);
  console.log("\n💬 Respuesta:\n", resultado.respuesta);
  console.log("\n");
}

// ============================================================================
// EJEMPLO 5: EVALUACIÓN DE VENDEDOR
// ============================================================================

async function ejemploEvaluacion() {
  console.log("=".repeat(70));
  console.log("EJEMPLO 5: Evaluación de Vendedor");
  console.log("=".repeat(70));

  const resultado = await runWorkflow({
    input_as_text: "Evalúa mi conocimiento técnico sobre sistemas de fijación para paneles",
    session_id: DEMO_SESSION_ID
  });

  console.log("\n📋 Clasificación:", resultado.classification);
  console.log("\n💬 Respuesta:\n", resultado.respuesta);
  console.log("\n");
}

// ============================================================================
// EJEMPLO 6: VALIDACIÓN TÉCNICA (autoportancia)
// ============================================================================

async function ejemploValidacionTecnica() {
  console.log("=".repeat(70));
  console.log("EJEMPLO 6: Validación Técnica (Autoportancia)");
  console.log("=".repeat(70));

  const resultado = await runWorkflow({
    input_as_text: "Necesito ISODEC 100mm para 6m de luz. ¿Es posible?",
    session_id: DEMO_SESSION_ID
  });

  console.log("\n📋 Clasificación:", resultado.classification);
  console.log("\n💬 Respuesta:\n", resultado.respuesta);
  console.log("\n");
}

// ============================================================================
// EJEMPLO 7: COMPARATIVA DE ESPESORES
// ============================================================================

async function ejemploComparativa() {
  console.log("=".repeat(70));
  console.log("EJEMPLO 7: Comparativa de Espesores");
  console.log("=".repeat(70));

  const resultado = await runWorkflow({
    input_as_text: "¿Qué diferencia hay entre usar ISODEC 100mm vs 150mm para un techo de 10m x 8m con luz de 5m? Incluye análisis de ahorro energético",
    session_id: DEMO_SESSION_ID
  });

  console.log("\n📋 Clasificación:", resultado.classification);
  console.log("\n💬 Respuesta:\n", resultado.respuesta);
  console.log("\n");
}

// ============================================================================
// EJEMPLO 8: COMANDO SOP
// ============================================================================

async function ejemploComandoSOP() {
  console.log("=".repeat(70));
  console.log("EJEMPLO 8: Comando SOP");
  console.log("=".repeat(70));

  const resultado = await runWorkflow({
    input_as_text: "/estado",
    session_id: DEMO_SESSION_ID
  });

  console.log("\n📋 Clasificación:", resultado.classification);
  console.log("\n💬 Respuesta:\n", resultado.respuesta);
  if (resultado.nota) {
    console.log("\n📝 Nota:", resultado.nota);
  }
  console.log("\n");
}

// ============================================================================
// EJECUTAR TODOS LOS EJEMPLOS
// ============================================================================

async function ejecutarTodos() {
  try {
    // Reset demo session so results are deterministic for each run
    await runWorkflow({ input_as_text: "/estado", session_id: DEMO_SESSION_ID, reset_session: true });

    await ejemploCotizacion();
    await ejemploCotizacionIncompleta();
    await ejemploInformacion();
    await ejemploPersonalizacionMauro();
    await ejemploEvaluacion();
    await ejemploValidacionTecnica();
    await ejemploComparativa();
    await ejemploComandoSOP();

    // Export demo artifacts (writes files if enabled)
    const checkpoint = await runWorkflow({ input_as_text: "/checkpoint", session_id: DEMO_SESSION_ID, write_files: true });
    console.log("\n💾 /checkpoint:\n", checkpoint.respuesta);

    const consolidar = await runWorkflow({ input_as_text: "/consolidar", session_id: DEMO_SESSION_ID, write_files: true });
    console.log("\n📦 /consolidar:\n", consolidar.respuesta);

    console.log("=".repeat(70));
    console.log("✅ Todos los ejemplos ejecutados");
    console.log("=".repeat(70));
  } catch (error) {
    console.error("❌ Error:", error);
  }
}

// Ejecutar si se llama directamente
if (require.main === module) {
  ejecutarTodos();
}

export {
  ejemploCotizacion,
  ejemploCotizacionIncompleta,
  ejemploInformacion,
  ejemploPersonalizacionMauro,
  ejemploEvaluacion,
  ejemploValidacionTecnica,
  ejemploComparativa,
  ejemploComandoSOP
};
