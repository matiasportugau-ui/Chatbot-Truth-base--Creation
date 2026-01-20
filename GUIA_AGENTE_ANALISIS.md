# 🤖 Guía: Agente de Análisis Inteligente

## 🎯 ¿Qué hace este agente?

El **Agente de Análisis Inteligente** es un sistema que:

1. ✅ **Revisa inputs** de clientes del CSV
2. ✅ **Genera presupuestos** usando el motor validado
3. ✅ **Busca PDFs reales** generados en Dropbox
4. ✅ **Extrae datos** de los PDFs (totales, subtotales, IVA)
5. ✅ **Compara resultados** (presupuesto vs PDF real)
6. ✅ **Analiza diferencias** e identifica causas
7. ✅ **Aprende** de las diferencias y genera lecciones
8. ✅ **Mejora** continuamente su conocimiento

---

## 🚀 Uso Rápido

### Opción 1: Uso Directo (Python)

```python
from agente_analisis_inteligente import AgenteAnalisisInteligente

agente = AgenteAnalisisInteligente()

# Analizar todas las cotizaciones
resultado = agente.proceso_completo(limite=10)

# Analizar por cliente
resultado = agente.proceso_completo(cliente="Agustín", limite=5)

# Analizar por producto
resultado = agente.proceso_completo(producto="ISODEC", limite=10)
```

### Opción 2: Desde Línea de Comandos

```bash
# Analizar todas las cotizaciones
python agente_analisis_inteligente.py

# Analizar por cliente
python agente_analisis_inteligente.py "Agustín Arbiza"

# Analizar por cliente y producto
python agente_analisis_inteligente.py "Agustín" "ISODEC"
```

### Opción 3: Integrado con OpenAI Assistant

```python
from agente_cotizacion_panelin import AgentePanelinOpenAI

agente = AgentePanelinOpenAI("tu-api-key", "asst_xxx")
thread = agente.client.beta.threads.create()

mensaje = """Analiza las cotizaciones de los últimos inputs.
Usa analizar_cotizacion_completa() para revisar, generar, comparar y aprender."""

respuesta = agente.procesar_mensaje(thread.id, mensaje)
```

---

## 📊 Proceso Completo

El agente ejecuta estos pasos automáticamente:

### 1. Revisar Inputs
- Lee el CSV de inputs de clientes
- Filtra por cliente/producto si se especifica
- Extrae parámetros (dimensiones, luz, producto, etc.)

### 2. Generar Presupuesto
- Usa el motor de cotización validado
- Aplica fórmulas de la base de conocimiento
- Valida autoportancia
- Calcula materiales y costos

### 3. Buscar PDF Real
- Busca en Dropbox/Cotizaciones
- Correlaciona por cliente, fecha, producto
- Calcula score de coincidencia

### 4. Extraer Datos del PDF
- Extrae texto del PDF
- Busca totales, subtotales, IVA
- Identifica cliente y fecha

### 5. Comparar Resultados
- Compara presupuesto vs PDF real
- Calcula diferencia porcentual
- Identifica si coincide (< 1% diferencia)

### 6. Analizar Diferencias
- Analiza magnitud de diferencia
- Identifica posibles causas:
  - Diferencia en precios
  - Materiales adicionales
  - Flete no considerado
  - Descuentos aplicados
- Genera recomendaciones

### 7. Aprender
- Genera lecciones aprendidas
- Sugiere mejoras
- Incorpora conocimiento para futuras cotizaciones

---

## 📋 Estructura de Resultados

```json
{
  "resultados": [
    {
      "input": {
        "cliente": "Agustín Arbiza",
        "fecha": "19-01",
        "consulta": "ISODEC EPS 100mm...",
        ...
      },
      "presupuesto": {
        "presupuesto": {
          "costos": {
            "total": 4206.56,
            ...
          },
          ...
        },
        "parametros_usados": {...}
      },
      "pdf_real": {
        "total": 4200.00,
        "subtotal": 3442.62,
        "iva": 757.38,
        "path": "/path/to/pdf",
        ...
      },
      "comparacion": {
        "presupuesto_total": 4206.56,
        "pdf_total": 4200.00,
        "diferencia": 6.56,
        "diferencia_porcentaje": 0.16,
        "coincide": true,
        "analisis": {
          "magnitud": "insignificante",
          "tipo": "sobreestimado",
          "posibles_causas": [...],
          "recomendaciones": [...]
        }
      },
      "leccion": {
        "timestamp": "2025-01-19T...",
        "diferencia_porcentaje": 0.16,
        "lecciones": [...],
        "sugerencias_mejora": [...]
      }
    }
  ],
  "resumen": {
    "totales": 10,
    "con_pdf": 8,
    "comparados": 8,
    "coinciden": 7
  },
  "lecciones_aprendidas": [...]
}
```

---

## 🔧 Configuración

### Rutas (en `agente_analisis_inteligente.py`)

```python
CSV_INPUTS = "/Volumes/My Passport for Mac/2.0 -  Administrador de Cotizaciones  - Admin..csv"
DROPBOX_COTIZACIONES = "/Users/matias/Library/CloudStorage/Dropbox/BMC - Uruguay/Cotizaciones"
```

Ajusta estas rutas según tu configuración.

### Dependencias

```bash
pip install PyPDF2 pandas openpyxl
```

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Análisis Completo

```python
from agente_analisis_inteligente import AgenteAnalisisInteligente

agente = AgenteAnalisisInteligente()
resultado = agente.proceso_completo(limite=20)

# Ver resumen
print(f"Procesados: {resultado['resumen']['totales']}")
print(f"Con PDF: {resultado['resumen']['con_pdf']}")
print(f"Coinciden: {resultado['resumen']['coinciden']}")
```

### Ejemplo 2: Análisis por Cliente

```python
agente = AgenteAnalisisInteligente()
resultado = agente.proceso_completo(cliente="Agustín", limite=5)

# Ver diferencias
for item in resultado['resultados']:
    if item.get('comparacion'):
        diff = item['comparacion']['diferencia_porcentaje']
        print(f"{item['input']['cliente']}: {diff:+.2f}%")
```

### Ejemplo 3: Integrado con OpenAI

```python
from agente_cotizacion_panelin import AgentePanelinOpenAI
import os

agente = AgentePanelinOpenAI(os.getenv("OPENAI_API_KEY"))
thread = agente.client.beta.threads.create()

# El asistente puede llamar analizar_cotizacion_completa() automáticamente
respuesta = agente.procesar_mensaje(
    thread.id,
    "Analiza las cotizaciones de ISODEC del último mes y dime qué aprendiste"
)
```

---

## 🧠 Aprendizaje Continuo

El agente aprende de cada comparación:

1. **Diferencia < 1%**: Excelente coincidencia - lógica precisa
2. **Diferencia 1-5%**: Diferencia pequeña - probablemente redondeos
3. **Diferencia 5-15%**: Diferencia moderada - revisar materiales adicionales
4. **Diferencia > 15%**: Diferencia grande - requiere revisión de lógica

Las lecciones se acumulan en `lecciones_aprendidas` y pueden usarse para:
- Mejorar fórmulas
- Agregar factores de ajuste
- Identificar casos especiales
- Actualizar base de conocimiento

---

## 📊 Interpretación de Resultados

### Coincidencia Perfecta (< 1%)
✅ La lógica de cotización es precisa para este caso.

### Diferencia Pequeña (1-5%)
⚠️ Probablemente por:
- Redondeos
- Ajustes menores
- Materiales opcionales

### Diferencia Moderada (5-15%)
⚠️ Revisar:
- Materiales adicionales no considerados
- Flete o servicios
- Ajustes comerciales

### Diferencia Grande (> 15%)
❌ Requiere:
- Revisión de fórmulas
- Validación contra más casos
- Actualización de lógica

---

## 🔄 Integración con Panelin

El agente está integrado con Panelin (OpenAI Assistant):

1. Panelin puede llamar `analizar_cotizacion_completa()`
2. El agente procesa automáticamente
3. Panelin recibe resultados y lecciones
4. Panelin incorpora el conocimiento para mejorar

---

## ✅ Ventajas

- ✅ **Automático**: Proceso completo sin intervención
- ✅ **Inteligente**: Correlaciona inputs con PDFs reales
- ✅ **Aprende**: Genera lecciones de cada comparación
- ✅ **Mejora**: Incorpora conocimiento continuamente
- ✅ **Integrado**: Funciona con OpenAI/Claude/Gemini

---

## 📝 Próximos Pasos

1. Ejecutar análisis completo
2. Revisar lecciones aprendidas
3. Actualizar base de conocimiento con mejoras
4. Re-ejecutar para validar mejoras
5. Integrar con Panelin para uso continuo
