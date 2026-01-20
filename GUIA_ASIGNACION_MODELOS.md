# 🎯 Guía: Asignación de Modelos IA por Procedimiento

## 📊 Resumen Ejecutivo

Este documento detalla qué modelo de IA (OpenAI/Claude/Gemini) usar para cada procedimiento del sistema, basado en las fortalezas específicas de cada modelo.

---

## 📈 Distribución de Tareas

| Modelo | Tareas Asignadas | Razón Principal |
|--------|------------------|-----------------|
| **OpenAI** | 7 tareas | Function Calling, Code Interpreter, Precisión |
| **Claude** | 8 tareas | Análisis profundo, Razonamiento, Aprendizaje |
| **Gemini** | 3 tareas | Tareas simples, Bajo costo, Desarrollo |

---

## 🔍 Análisis por Categoría

### 1. ANÁLISIS Y PROCESAMIENTO

#### Revisar Inputs
- **Modelo Principal:** Gemini
- **Modelo Alternativo:** OpenAI
- **Razón:** Tarea simple de procesamiento, Gemini es suficiente y más económico
- **Requisitos:** Procesamiento de CSV, Parsing de datos

#### Extraer Datos PDF
- **Modelo Principal:** OpenAI
- **Modelo Alternativo:** Claude
- **Razón:** OpenAI tiene Code Interpreter para procesar PDFs, Claude para análisis de texto complejo
- **Requisitos:** Procesamiento de PDF, Extracción de texto, Parsing de números

#### Buscar PDF
- **Modelo Principal:** Gemini
- **Modelo Alternativo:** OpenAI
- **Razón:** Búsqueda de archivos es tarea simple, Gemini es eficiente
- **Requisitos:** Búsqueda de archivos, Correlación de nombres

---

### 2. CÁLCULOS Y VALIDACIÓN

#### Generar Presupuesto
- **Modelo Principal:** OpenAI
- **Modelo Alternativo:** Gemini
- **Razón:** OpenAI tiene Function Calling nativo y Code Interpreter para cálculos precisos
- **Requisitos:** Cálculos matemáticos, Function Calling, Precisión

#### Validar Autoportancia
- **Modelo Principal:** OpenAI
- **Modelo Alternativo:** Gemini
- **Razón:** Validación técnica requiere precisión, OpenAI es mejor
- **Requisitos:** Validación técnica, Comparación numérica, Precisión

#### Calcular Materiales
- **Modelo Principal:** OpenAI
- **Modelo Alternativo:** Gemini
- **Razón:** Cálculos de materiales requieren precisión matemática, OpenAI es superior
- **Requisitos:** Cálculos matemáticos, Fórmulas, Precisión

---

### 3. ANÁLISIS Y COMPARACIÓN

#### Comparar Resultados
- **Modelo Principal:** Claude
- **Modelo Alternativo:** OpenAI
- **Razón:** Claude es excelente para análisis comparativo y razonamiento
- **Requisitos:** Análisis comparativo, Razonamiento, Interpretación

#### Analizar Diferencias
- **Modelo Principal:** Claude
- **Modelo Alternativo:** OpenAI
- **Razón:** Claude sobresale en análisis profundo y comprensión de causas
- **Requisitos:** Análisis profundo, Comprensión de contexto, Razonamiento causal

#### Identificar Causas
- **Modelo Principal:** Claude
- **Modelo Alternativo:** OpenAI
- **Razón:** Claude es mejor para razonamiento causal y análisis de causas raíz
- **Requisitos:** Razonamiento causal, Análisis de causas raíz, Comprensión profunda

---

### 4. APRENDIZAJE Y MEJORA

#### Aprender de Diferencias
- **Modelo Principal:** Claude
- **Modelo Alternativo:** OpenAI
- **Razón:** Claude es superior para aprendizaje y extracción de patrones
- **Requisitos:** Aprendizaje, Extracción de patrones, Síntesis

#### Generar Lecciones
- **Modelo Principal:** Claude
- **Modelo Alternativo:** OpenAI
- **Razón:** Claude genera lecciones más profundas y útiles
- **Requisitos:** Síntesis, Generación de conocimiento, Comprensión profunda

#### Sugerir Mejoras
- **Modelo Principal:** Claude
- **Modelo Alternativo:** OpenAI
- **Razón:** Claude es mejor para sugerencias creativas y mejoras
- **Requisitos:** Creatividad, Sugerencias, Mejora continua

---

### 5. INTERACCIÓN CON CLIENTE

#### Cotización Interactiva
- **Modelo Principal:** OpenAI
- **Modelo Alternativo:** Claude
- **Razón:** OpenAI tiene mejor Function Calling para interacción dinámica
- **Requisitos:** Function Calling, Interacción dinámica, Respuestas rápidas

#### Presentación Profesional
- **Modelo Principal:** Claude
- **Modelo Alternativo:** OpenAI
- **Razón:** Claude genera presentaciones más profesionales y bien estructuradas
- **Requisitos:** Generación de texto, Estructura, Profesionalismo

#### Recomendaciones Técnicas
- **Modelo Principal:** Claude
- **Modelo Alternativo:** OpenAI
- **Razón:** Claude es mejor para recomendaciones técnicas bien fundamentadas
- **Requisitos:** Razonamiento técnico, Recomendaciones, Fundamentación

---

### 6. PROCESAMIENTO DE CONOCIMIENTO

#### Procesar Base Conocimiento
- **Modelo Principal:** OpenAI
- **Modelo Alternativo:** Gemini
- **Razón:** OpenAI tiene mejor acceso a archivos y Code Interpreter
- **Requisitos:** Procesamiento de archivos, Code Interpreter, Acceso a KB

#### Actualizar Conocimiento
- **Modelo Principal:** Claude
- **Modelo Alternativo:** OpenAI
- **Razón:** Claude es mejor para síntesis y actualización de conocimiento
- **Requisitos:** Síntesis, Actualización, Comprensión de cambios

#### Validar Fórmulas
- **Modelo Principal:** OpenAI
- **Modelo Alternativo:** Gemini
- **Razón:** OpenAI tiene Code Interpreter para validar fórmulas matemáticas
- **Requisitos:** Validación matemática, Code Interpreter, Precisión

---

## 🎯 Reglas de Asignación

### Prioridad 1: Disponibilidad
Si el modelo recomendado no está disponible, usar el modelo alternativo.

### Prioridad 2: Costo
Para tareas simples, preferir Gemini (gratis) sobre OpenAI/Claude.

### Prioridad 3: Precisión
Para cálculos y validaciones, siempre preferir OpenAI.

### Prioridad 4: Análisis
Para análisis profundo y aprendizaje, siempre preferir Claude.

---

## 🔄 Flujo de Trabajo Recomendado

```
1. Revisar Inputs (Gemini)
   ↓
2. Generar Presupuesto (OpenAI)
   ↓
3. Buscar PDF (Gemini)
   ↓
4. Extraer Datos PDF (OpenAI)
   ↓
5. Comparar Resultados (Claude)
   ↓
6. Analizar Diferencias (Claude)
   ↓
7. Aprender de Diferencias (Claude)
   ↓
8. Generar Lecciones (Claude)
   ↓
9. Presentar Resultados (Claude)
```

---

## 💡 Uso del Orquestador

```python
from orquestador_modelos_ia import ejecutar_procedimiento, TipoTarea
from analisis_modelos_ia import TipoTarea

# Ejecutar procedimiento - el orquestador elige el mejor modelo
resultado = ejecutar_procedimiento(
    TipoTarea.REVISAR_INPUTS,
    cliente="Agustín"
)

# El sistema automáticamente:
# 1. Detecta modelos disponibles
# 2. Elige el mejor modelo para la tarea
# 3. Ejecuta la función
# 4. Si falla, intenta con modelo alternativo
```

---

## 📊 Estadísticas de Uso

El orquestador mantiene estadísticas de:
- Tareas ejecutadas por modelo
- Fallos y cambios de modelo
- Modelos disponibles

```python
from orquestador_modelos_ia import OrquestadorModelos

orquestador = OrquestadorModelos()
stats = orquestador.get_estadisticas()

print(f"Tareas ejecutadas: {stats['tareas_ejecutadas']}")
print(f"Por modelo: {stats['por_modelo']}")
```

---

## ✅ Ventajas del Sistema

- ✅ **Optimización automática**: Elige el mejor modelo para cada tarea
- ✅ **Resiliencia**: Cambia automáticamente si un modelo falla
- ✅ **Costo eficiente**: Usa modelos más baratos cuando es posible
- ✅ **Flexibilidad**: Permite forzar un modelo específico si es necesario
- ✅ **Estadísticas**: Rastrea uso y rendimiento

---

## 🔧 Configuración

### Variables de Entorno Requeridas

```bash
# Para OpenAI
export OPENAI_API_KEY=tu-key

# Para Claude
export ANTHROPIC_API_KEY=tu-key

# Para Gemini
export GOOGLE_API_KEY=tu-key
```

### Instalación de Dependencias

```bash
pip install openai anthropic google-generativeai
```

---

## 📝 Notas Importantes

1. **Gemini** es gratis pero menos preciso - usar solo para tareas simples
2. **OpenAI** es el mejor para cálculos y precisión
3. **Claude** es el mejor para análisis y aprendizaje
4. El orquestador maneja automáticamente la disponibilidad y fallos
5. Siempre hay un modelo alternativo configurado

---

## 🚀 Próximos Pasos

1. ✅ Ejecutar `analisis_modelos_ia.py` para ver el análisis completo
2. ✅ Usar `orquestador_modelos_ia.py` para ejecutar tareas
3. ⚠️ Configurar API keys para todos los modelos
4. ⚠️ Probar el sistema con tareas reales
5. ⚠️ Monitorear estadísticas de uso
