# Panelin - OpenAI Agents SDK - Guía Completa
**Versión:** 1.0 Final  
**Fecha:** 2026-01-21  
**Plataforma:** OpenAI Agents SDK (TypeScript/Node.js)

---

## 📋 TABLA DE CONTENIDOS

1. [Descripción](#1-descripción)
2. [Instalación](#2-instalación)
3. [Configuración](#3-configuración)
4. [Estructura del Código](#4-estructura-del-código)
5. [Uso Básico](#5-uso-básico)
6. [Implementación de Tools](#6-implementación-de-tools)
7. [Integración con Backend Python](#7-integración-con-backend-python)
8. [Configuración Avanzada](#8-configuración-avanzada)
9. [Testing](#9-testing)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. DESCRIPCIÓN

Implementación de Panelin usando el **OpenAI Agents SDK** para crear un sistema de agentes multi-especialista que maneja:

- **Cotizaciones**: Proceso completo de 5 fases
- **Evaluación/Entrenamiento**: Evaluación y entrenamiento de personal de ventas
- **Información**: Consultas informativas sobre sistemas constructivos BMC
- **Comandos SOP**: Comandos especiales (/estado, /checkpoint, /consolidar)

**Diferencia con GPT Builder**: Este SDK es para desarrollo programático, no para crear un GPT en ChatGPT. Permite integrar Panelin en aplicaciones, APIs, y sistemas automatizados.

---

## 2. INSTALACIÓN

### Requisitos Previos

- Node.js >= 18.0.0
- npm o yarn
- OpenAI API Key

### Paso 1: Instalar Dependencias

```bash
npm install @openai/agents zod openai @openai/guardrails
```

O con yarn:

```bash
yarn add @openai/agents zod openai @openai/guardrails
```

### Paso 2: Instalar Dependencias de Desarrollo

```bash
npm install --save-dev @types/node ts-node typescript
```

O con yarn:

```bash
yarn add -D @types/node ts-node typescript
```

### Paso 3: Verificar Instalación

```bash
npm list @openai/agents zod openai @openai/guardrails
```

---

## 3. CONFIGURACIÓN

### Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
OPENAI_API_KEY=sk-tu-api-key-aqui
```

**⚠️ IMPORTANTE**: 
- No commitear el archivo `.env` (agregar a `.gitignore`)
- Usar variables de entorno en producción
- Rotar API keys periódicamente

### Verificar Configuración

```typescript
// verificar_config.ts
import * as dotenv from 'dotenv';

dotenv.config();

if (!process.env.OPENAI_API_KEY) {
  console.error('❌ OPENAI_API_KEY no configurada');
  process.exit(1);
}

console.log('✅ Configuración correcta');
```

---

## 4. ESTRUCTURA DEL CÓDIGO

### Agentes

#### 1. ClassificationAgent
Clasifica la intención del usuario en:
- `cotizacion`: Solicitudes de cotización/precio
- `evaluacion_entrenamiento`: Evaluación y entrenamiento de vendedores
- `informacion`: Consultas informativas
- `comando_sop`: Comandos especiales (/estado, /checkpoint, etc.)

#### 2. CotizacionAgent
Maneja cotizaciones completas siguiendo el proceso de 5 fases:
- **Fase 1**: Identificación de parámetros (producto, espesor, luz, cantidad, fijación)
- **Fase 2**: Validación técnica (autoportancia)
- **Fase 3**: Recuperación de datos (precios desde KB)
- **Fase 4**: Cálculos (fórmulas exactas del JSON)
- **Fase 5**: Presentación (desglose + IVA + recomendaciones)

#### 3. EvaluacionEntrenamientoAgent
Evalúa y entrena personal de ventas:
- Evaluación de conocimiento técnico
- Feedback estructurado
- Simulación de escenarios
- Entrenamiento basado en interacciones históricas

#### 4. InformacionAgent
Responde consultas informativas:
- Diferencias entre productos (EPS vs PIR)
- Especificaciones técnicas
- Aplicaciones y usos
- Mejores prácticas

### Tools (Herramientas)

#### 1. calcular_cotizacion
Calcula cotizaciones completas:
- Valida autoportancia
- Calcula materiales (paneles, fijaciones, accesorios)
- Aplica IVA 22%
- Genera desglose detallado

**Parámetros**:
```typescript
{
  producto: string;      // "ISODEC", "ISOPANEL", "ISOROOF"
  espesor: string;       // "100", "150", "200"
  dimensiones: {
    largo: number;       // metros
    ancho: number;       // metros
    luz: number;        // distancia entre apoyos (metros)
  };
  fijacion: string;      // "hormigon", "madera"
  cantidad?: number;     // opcional
}
```

#### 2. buscar_en_base_conocimiento
Busca en Knowledge Base con jerarquía de 4 niveles:
- **Nivel 1**: `BMC_Base_Conocimiento_GPT-2.json` (PRIMARIO)
- **Nivel 2**: `BMC_Base_Unificada_v4.json` (validación)
- **Nivel 3**: `panelin_truth_bmcuruguay_web_only_v2.json` (dinámico)
- **Nivel 4**: Archivos de soporte (MD, RTF, CSV)

**Parámetros**:
```typescript
{
  consulta: string;      // "precio ISODEC 100mm"
  nivel?: number;        // 1-4, opcional (default: 1)
}
```

#### 3. evaluar_vendedor
Evalúa conocimiento técnico de vendedores:
- Analiza interacción
- Genera evaluación estructurada
- Proporciona feedback

**Parámetros**:
```typescript
{
  interaccion: string;   // Conversación o respuesta del vendedor
  contexto?: string;     // Contexto adicional
}
```

### Guardrails

#### 1. Jailbreak Detection
Detecta intentos de jailbreak o manipulación del sistema.

#### 2. PII Masking
Anonimiza información personal (no bloquea, solo enmascara).

#### 3. Moderation
Filtra contenido inapropiado o ofensivo.

**Configuración**:
```typescript
const panelinGuardrailConfig = {
  guardrails: [
    { 
      name: "Jailbreak", 
      config: { 
        model: "gpt-4o-mini", 
        confidence_threshold: 0.7 
      } 
    },
    { 
      name: "Contains PII", 
      config: { 
        block: false  // Solo anonimizar, no bloquear
      } 
    },
    { 
      name: "Moderation", 
      config: {} 
    }
  ]
};
```

### Personalización

Soporta personalización automática para usuarios específicos:

- **Mauro**: Respuesta única, guiada por concepto
- **Martin**: Aunque no crea en IA, ayuda a resolver problemas
- **Rami**: Puede exigir más, poner a prueba

---

## 5. USO BÁSICO

### Ejemplo 1: Cotización

```typescript
import { runWorkflow } from "./panelin_agents_sdk";

const resultado = await runWorkflow({
  input_as_text: "Necesito cotizar ISODEC 100mm para un techo de 10m x 5m, luz de 4m, fijación a hormigón"
});

console.log(resultado.respuesta);
// Resultado: Cotización completa con desglose, IVA, total, recomendaciones
```

### Ejemplo 2: Información

```typescript
const resultado = await runWorkflow({
  input_as_text: "¿Cuál es la diferencia entre EPS y PIR?"
});

console.log(resultado.respuesta);
// Resultado: Explicación técnica de diferencias
```

### Ejemplo 3: Evaluación

```typescript
const resultado = await runWorkflow({
  input_as_text: "Evalúa mi conocimiento sobre autoportancia"
});

console.log(resultado.respuesta);
// Resultado: Evaluación estructurada con feedback
```

### Ejemplo 4: Con Personalización

```typescript
const resultado = await runWorkflow({
  input_as_text: "Hola, soy Mauro",
  usuario: "Mauro"  // Opcional: especificar usuario
});

console.log(resultado.respuesta);
// Resultado: Respuesta personalizada para Mauro
```

---

## 6. IMPLEMENTACIÓN DE TOOLS

### ⚠️ TODO: Integrar con Backend Python

Los tools actualmente tienen placeholders. Necesitas implementar:

### 1. calcular_cotizacion

**Opción A: API REST** (Recomendado)

```typescript
async function calcularCotizacion(input: any) {
  const response = await fetch('http://localhost:5000/api/cotizar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input)
  });
  
  if (!response.ok) {
    throw new Error(`Error: ${response.statusText}`);
  }
  
  return await response.json();
}
```

**Opción B: Child Process**

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
    largo=${input.dimensiones.largo},
    ancho=${input.dimensiones.ancho},
    luz=${input.dimensiones.luz},
    fijacion='${input.fijacion}'
)
print(json.dumps(resultado))
"`;
  
  const { stdout, stderr } = await execAsync(script);
  
  if (stderr) {
    throw new Error(`Error: ${stderr}`);
  }
  
  return JSON.parse(stdout);
}
```

### 2. buscar_en_base_conocimiento

```typescript
import * as fs from 'fs';
import * as path from 'path';

async function buscarEnBaseConocimiento(consulta: string, nivel: number = 1) {
  const archivos = {
    1: 'BMC_Base_Conocimiento_GPT-2.json',
    2: 'Files/BMC_Base_Unificada_v4.json',
    3: 'panelin_truth_bmcuruguay_web_only_v2.json',
    4: 'panelin_context_consolidacion_sin_backend.md'
  };
  
  const archivo = archivos[nivel as keyof typeof archivos];
  const ruta = path.join(process.cwd(), archivo);
  
  if (!fs.existsSync(ruta)) {
    throw new Error(`Archivo no encontrado: ${archivo}`);
  }
  
  const contenido = fs.readFileSync(ruta, 'utf-8');
  
  // Buscar según consulta (implementar lógica de búsqueda)
  // Por ejemplo, si es JSON, parsear y buscar
  // Si es MD, buscar texto
  
  return {
    archivo,
    nivel,
    resultados: [] // Implementar búsqueda real
  };
}
```

### 3. evaluar_vendedor

```typescript
async function evaluarVendedor(interaccion: string, contexto?: string) {
  // Implementar lógica de evaluación
  // Analizar interacción
  // Generar evaluación estructurada
  // Retornar feedback
  
  return {
    conocimiento_tecnico: 0.8,  // 0-1
    areas_fuertes: ['autoportancia', 'precios'],
    areas_mejora: ['aislamiento_termico'],
    feedback: 'Feedback estructurado...',
    recomendaciones: ['Revisar fórmulas de ahorro energético']
  };
}
```

---

## 7. INTEGRACIÓN CON BACKEND PYTHON

### Opción 1: API REST (Recomendado)

#### Backend Python (Flask)

```python
# api.py
from flask import Flask, request, jsonify
from motor_cotizacion_panelin import MotorCotizacionPanelin
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permitir CORS para llamadas desde TypeScript

motor = MotorCotizacionPanelin()

@app.route('/api/cotizar', methods=['POST'])
def cotizar():
    try:
        data = request.json
        resultado = motor.calcular_cotizacion(
            producto=data['producto'],
            espesor=data['espesor'],
            largo=data['dimensiones']['largo'],
            ancho=data['dimensiones']['ancho'],
            luz=data['dimensiones']['luz'],
            fijacion=data['fijacion'],
            cantidad=data.get('cantidad', 1)
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/buscar', methods=['POST'])
def buscar():
    try:
        data = request.json
        # Implementar búsqueda en KB
        resultado = buscar_en_kb(data['consulta'], data.get('nivel', 1))
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)
```

#### Frontend TypeScript

```typescript
const API_URL = 'http://localhost:5000/api';

async function calcularCotizacion(input: any) {
  const response = await fetch(`${API_URL}/cotizar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input)
  });
  
  if (!response.ok) {
    throw new Error(`Error: ${response.statusText}`);
  }
  
  return await response.json();
}
```

### Opción 2: Child Process

Ver ejemplo en sección [6. Implementación de Tools](#6-implementación-de-tools)

---

## 8. CONFIGURACIÓN AVANZADA

### Ajustar Modelos

```typescript
const cotizacionAgent = new Agent({
  name: "CotizacionAgent",
  model: "gpt-4o",  // Cambiar a modelo más potente
  modelSettings: {
    temperature: 0.5,    // Reducir para más determinismo
    maxTokens: 8192,     // Aumentar para respuestas largas
  },
  instructions: "...",
  tools: [calcularCotizacion, buscarEnBaseConocimiento]
});
```

### Agregar Nuevos Guardrails

```typescript
const panelinGuardrailConfig = {
  guardrails: [
    { 
      name: "Jailbreak", 
      config: { 
        model: "gpt-4o-mini", 
        confidence_threshold: 0.7 
      } 
    },
    { 
      name: "Contains PII", 
      config: { 
        block: false 
      } 
    },
    { 
      name: "Moderation", 
      config: {} 
    },
    { 
      name: "Hallucination Detection",  // Nuevo
      config: {
        model: "gpt-4o",
        threshold: 0.8
      } 
    }
  ]
};
```

### Personalizar Flujo de Trabajo

```typescript
const workflow = new Workflow({
  name: "PanelinWorkflow",
  agents: [classificationAgent, cotizacionAgent, evaluacionAgent, informacionAgent],
  guardrails: panelinGuardrailConfig,
  onStepComplete: (step) => {
    console.log(`Step completed: ${step.name}`);
  },
  onError: (error) => {
    console.error(`Error: ${error.message}`);
  }
});
```

---

## 9. TESTING

### Test Básico

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

test().catch(console.error);
```

### Ejecutar Tests

```bash
npm run test
# o
ts-node test.ts
```

---

## 10. TROUBLESHOOTING

### Error: "Agent result is undefined"

**Causa**: El agente no retorna un `finalOutput`

**Solución**:
- Verificar que el agente retorne un `finalOutput`
- Revisar logs de `runner.run()`
- Verificar que el modelo tenga suficiente `maxTokens`

### Error: "Tool execution failed"

**Causa**: Las funciones de tools no están implementadas o fallan

**Solución**:
- Verificar que las funciones de tools estén implementadas
- Revisar parámetros de entrada
- Verificar conexión con backend (si aplica)
- Revisar logs de error

### Error: "Guardrails bloquean respuestas válidas"

**Causa**: Configuración de guardrails muy estricta

**Solución**:
- Ajustar `confidence_threshold` en guardrails
- Revisar configuración de PII (puede estar bloqueando en lugar de anonimizar)
- Verificar que `block: false` esté configurado para PII

### Error: "OPENAI_API_KEY not found"

**Causa**: Variable de entorno no configurada

**Solución**:
- Verificar que `.env` exista y tenga `OPENAI_API_KEY`
- Verificar que `dotenv.config()` se ejecute antes de usar la API key
- Verificar que la API key sea válida

### Error: "Module not found"

**Causa**: Dependencias no instaladas

**Solución**:
```bash
npm install
# o
yarn install
```

---

## 📚 ARCHIVOS RELACIONADOS

- `panelin_agents_sdk.ts` - Implementación principal del SDK
- `panelin_agents_sdk_example.ts` - Ejemplos de uso
- `package.json` - Configuración npm
- `tsconfig.json` - Configuración TypeScript
- `PANELIN_INSTRUCTIONS_FINAL.txt` - Instrucciones de Panelin (referencia)
- `PANELIN_QUOTATION_PROCESS.md` - Proceso de cotización (referencia)
- `PANELIN_TRAINING_GUIDE.md` - Guía de evaluación/entrenamiento (referencia)

---

## 🔗 REFERENCIAS

- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/guides/agents)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)

---

## 🎯 PRÓXIMOS PASOS

1. **Implementar Tools**: Conectar con backend Python
   - `calcular_cotizacion` → `motor_cotizacion_panelin.py`
   - `buscar_en_base_conocimiento` → Archivos JSON de KB
   - `evaluar_vendedor` → Sistema de evaluación

2. **Configurar Backend**: Crear API REST o usar child process

3. **Testing**: Ejecutar ejemplos y validar respuestas

4. **Despliegue**: Configurar para producción (variables de entorno, logging, monitoreo)

---

**Última actualización**: 2026-01-21  
**Versión**: 1.0 Final
