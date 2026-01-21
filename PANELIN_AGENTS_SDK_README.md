# Panelin - OpenAI Agents SDK Implementation

**Versión:** 1.0  
**Fecha:** 2026-01-21  
**Plataforma:** OpenAI Agents SDK

---

## 📋 Descripción

Implementación de Panelin usando el **OpenAI Agents SDK** para crear un sistema de agentes multi-especialista que maneja cotizaciones, evaluación/entrenamiento e información sobre sistemas constructivos BMC.

---

## 🚀 Instalación

### 1. Instalar Dependencias

```bash
npm install @openai/agents zod openai @openai/guardrails
```

O con yarn:

```bash
yarn add @openai/agents zod openai @openai/guardrails
```

### 2. Configurar Variables de Entorno

Crear archivo `.env`:

```bash
OPENAI_API_KEY=tu_api_key_aqui
```

---

## 📁 Estructura del Código

### Agentes

1. **ClassificationAgent**: Clasifica la intención del usuario
   - `cotizacion`: Solicitudes de cotización/precio
   - `evaluacion_entrenamiento`: Evaluación y entrenamiento de vendedores
   - `informacion`: Consultas informativas
   - `comando_sop`: Comandos especiales (/estado, /checkpoint, etc.)

2. **CotizacionAgent**: Maneja cotizaciones completas (5 fases)
   - Fase 1: Identificación de parámetros
   - Fase 2: Validación técnica (autoportancia)
   - Fase 3: Recuperación de datos (precios)
   - Fase 4: Cálculos (fórmulas exactas)
   - Fase 5: Presentación (desglose + IVA + recomendaciones)

3. **EvaluacionEntrenamientoAgent**: Evalúa y entrena personal de ventas

4. **InformacionAgent**: Responde consultas informativas

### Tools (Herramientas)

1. **calcular_cotizacion**: Calcula cotizaciones completas
   - Valida autoportancia
   - Calcula materiales
   - Aplica IVA 22%

2. **buscar_en_base_conocimiento**: Busca en Knowledge Base
   - Prioriza Nivel 1 (BMC_Base_Conocimiento_GPT-2.json)
   - Soporta 4 niveles de jerarquía

3. **evaluar_vendedor**: Evalúa conocimiento técnico de vendedores

### Guardrails

- **Jailbreak Detection**: Detecta intentos de jailbreak
- **PII Masking**: Anonimiza información personal (no bloquea)
- **Moderation**: Filtra contenido inapropiado

### Personalización

Soporta personalización automática para:
- **Mauro**: Respuesta única, guiada por concepto
- **Martin**: Aunque no crea en IA, ayuda a resolver problemas
- **Rami**: Puede exigir más, poner a prueba

---

## 💻 Uso Básico

### Ejemplo 1: Cotización

```typescript
import { runWorkflow } from "./panelin_agents_sdk";

const resultado = await runWorkflow({
  input_as_text: "Necesito cotizar ISODEC 100mm para un techo de 10m x 5m, luz de 4m, fijación a hormigón"
});

console.log(resultado.respuesta);
```

### Ejemplo 2: Información

```typescript
const resultado = await runWorkflow({
  input_as_text: "¿Cuál es la diferencia entre EPS y PIR?"
});

console.log(resultado.respuesta);
```

### Ejemplo 3: Evaluación

```typescript
const resultado = await runWorkflow({
  input_as_text: "Evalúa mi conocimiento sobre autoportancia"
});

console.log(resultado.respuesta);
```

---

## 🔧 Implementación de Tools

### TODO: Integrar con Backend Python

Los tools actualmente tienen placeholders. Necesitas implementar:

1. **calcular_cotizacion**: Integrar con `motor_cotizacion_panelin.py`
   ```typescript
   // Llamar a API Python o función compartida
   const resultado = await fetch('/api/cotizar', {
     method: 'POST',
     body: JSON.stringify(input)
   });
   ```

2. **buscar_en_base_conocimiento**: Integrar con archivos JSON de KB
   ```typescript
   // Leer BMC_Base_Conocimiento_GPT-2.json
   // Buscar según consulta
   // Retornar resultados estructurados
   ```

3. **evaluar_vendedor**: Integrar con sistema de evaluación
   ```typescript
   // Analizar interacción
   // Generar evaluación estructurada
   // Retornar feedback
   ```

---

## 📊 Flujo de Trabajo

```
Usuario → Guardrails → Classification Agent
                              ↓
                    ┌─────────┴─────────┐
                    ↓                   ↓
            [Clasificación]      [Personalización]
                    ↓
        ┌───────────┼───────────┐
        ↓           ↓           ↓
   Cotización  Evaluación  Información
        ↓           ↓           ↓
    [Tools]     [Tools]     [Tools]
        ↓           ↓           ↓
    [Resultado Final con Personalización]
```

---

## 🎯 Características Principales

### ✅ Implementado

- ✅ Sistema de clasificación multi-agente
- ✅ Agentes especializados (cotización, evaluación, información)
- ✅ Guardrails (jailbreak, PII, moderation)
- ✅ Personalización (Mauro, Martin, Rami)
- ✅ Estructura de tools (calcular_cotizacion, buscar_en_base_conocimiento, evaluar_vendedor)
- ✅ Flujo de trabajo completo

### ⚠️ Pendiente de Implementación

- ⚠️ Integración con `motor_cotizacion_panelin.py` (backend Python)
- ⚠️ Búsqueda real en archivos JSON de Knowledge Base
- ⚠️ Sistema de evaluación de vendedores
- ⚠️ Comandos SOP (/estado, /checkpoint, /consolidar)
- ⚠️ Generación de PDFs (Code Interpreter)

---

## 🔗 Integración con Backend Python

### Opción 1: API REST

Crear API Flask/FastAPI que exponga funciones Python:

```python
# api.py
from flask import Flask, request, jsonify
from motor_cotizacion_panelin import MotorCotizacionPanelin

app = Flask(__name__)
motor = MotorCotizacionPanelin()

@app.route('/api/cotizar', methods=['POST'])
def cotizar():
    data = request.json
    resultado = motor.calcular_cotizacion(
        producto=data['producto'],
        espesor=data['espesor'],
        # ...
    )
    return jsonify(resultado)
```

Luego en TypeScript:

```typescript
const resultado = await fetch('http://localhost:5000/api/cotizar', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(input)
}).then(r => r.json());
```

### Opción 2: Child Process

Ejecutar scripts Python directamente:

```typescript
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

async function calcularCotizacion(input: any) {
  const script = `python3 -c "
from motor_cotizacion_panelin import MotorCotizacionPanelin
import json
motor = MotorCotizacionPanelin()
resultado = motor.calcular_cotizacion(
    producto='${input.producto}',
    espesor='${input.espesor}',
    # ...
)
print(json.dumps(resultado))
"`;
  const { stdout } = await execAsync(script);
  return JSON.parse(stdout);
}
```

---

## 📝 Configuración Avanzada

### Ajustar Modelos

```typescript
const cotizacionAgent = new Agent({
  // ...
  model: "gpt-4o", // Cambiar a modelo más potente
  modelSettings: {
    temperature: 0.5, // Reducir para más determinismo
    maxTokens: 8192, // Aumentar para respuestas largas
  }
});
```

### Agregar Nuevos Guardrails

```typescript
const panelinGuardrailConfig = {
  guardrails: [
    { name: "Jailbreak", config: { model: "gpt-4o-mini", confidence_threshold: 0.7 } },
    { name: "Contains PII", config: { block: false } },
    { name: "Moderation", config: {} },
    { name: "Hallucination Detection", config: {} }, // Nuevo
  ]
};
```

---

## 🧪 Testing

```typescript
// test.ts
import { runWorkflow } from "./panelin_agents_sdk";

async function test() {
  // Test cotización
  const cotizacion = await runWorkflow({
    input_as_text: "Cotiza ISODEC 100mm, 10m x 5m, luz 4m"
  });
  console.log("Cotización:", cotizacion);

  // Test información
  const info = await runWorkflow({
    input_as_text: "¿Qué es autoportancia?"
  });
  console.log("Información:", info);

  // Test personalización
  const personalizado = await runWorkflow({
    input_as_text: "Hola, soy Mauro"
  });
  console.log("Personalizado:", personalizado);
}

test();
```

---

## 📚 Referencias

- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/guides/agents)
- [PANELIN_INSTRUCTIONS_FINAL.txt](./PANELIN_INSTRUCTIONS_FINAL.txt) - Instrucciones completas de Panelin
- [PANELIN_QUOTATION_PROCESS.md](./PANELIN_QUOTATION_PROCESS.md) - Proceso de cotización
- [PANELIN_TRAINING_GUIDE.md](./PANELIN_TRAINING_GUIDE.md) - Guía de evaluación/entrenamiento

---

## 🆘 Troubleshooting

### Error: "Agent result is undefined"

- Verificar que el agente retorne un `finalOutput`
- Revisar logs de `runner.run()`
- Verificar que el modelo tenga suficiente `maxTokens`

### Error: "Tool execution failed"

- Verificar que las funciones de tools estén implementadas
- Revisar parámetros de entrada
- Verificar conexión con backend (si aplica)

### Guardrails bloquean respuestas válidas

- Ajustar `confidence_threshold` en guardrails
- Revisar configuración de PII (puede estar bloqueando en lugar de anonimizar)
- Verificar que `block: false` esté configurado para PII

---

**Última actualización**: 2026-01-21
