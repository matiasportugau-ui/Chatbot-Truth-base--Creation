# Correcciones a la Base de Conocimientos - 2026-01-24

## Contexto
Este documento resume las correcciones implementadas en la base de conocimientos de Panelin (BMC Assistant Pro) basadas en el feedback de alineación conceptual con el equipo de ventas.

---

## Correcciones Implementadas

### KB-001: Descripción Institucional (Prioridad P0 - CRÍTICO)

**Problema identificado:**
El asistente afirmaba que "BMC fabrica" cuando en realidad BMC Uruguay no fabrica.

**Corrección aplicada:**
- BMC Uruguay **comercializa/suministra** productos de fabricantes especializados
- BMC Uruguay brinda **asesoramiento técnico integral**
- Se agregó sección `institucional` en `BMC_Base_Conocimiento_GPT-2.json`
- Se actualizaron todas las instrucciones del sistema para reflejar esta aclaración

**Archivos modificados:**
- `BMC_Base_Conocimiento_GPT-2.json`
- `gpt_configs/INSTRUCCIONES_PANELIN_ACTUALIZADAS.txt`
- `gpt_configs/Panelin_Asistente_Integral_BMC_config.json`
- `PANELIN_INSTRUCTIONS_FINAL.txt`
- `PANELIN_ULTIMATE_INSTRUCTIONS.md`

---

### KB-002: Diferencial Competitivo (Prioridad P0)

**Problema identificado:**
El diferencial competitivo estaba definido de forma genérica.

**Corrección aplicada:**
Se incorporó la formulación definida por el equipo de ventas:

> **"Soluciones técnicas optimizadas para generar confort, ahorrar presupuesto, optimizar estructura, reducir tiempos de obra y evitar problemas a futuro."**

**Valor agregado de BMC:**
- Partir del problema del cliente, no del producto
- Reducir riesgo técnico mediante asesoramiento especializado
- Evaluar costo total (no solo precio del panel) incluyendo estructura y mano de obra
- Capacidad de decir "no conviene" cuando corresponde
- Traducir lo técnico a lenguaje de obra
- Acompañar la decisión de compra con conocimiento experto

---

### KB-003: Catálogo de Productos - Isofrig PIR (Prioridad P1)

**Problema identificado:**
El producto "Isofrig PIR" para cámaras frigoríficas no estaba en el catálogo.

**Corrección aplicada:**
Se agregó el producto `ISOFRIG_PIR` en `BMC_Base_Conocimiento_GPT-2.json`:

```json
"ISOFRIG_PIR": {
  "nombre_comercial": "Isofrig (PIR)",
  "tipo": "pared_frigorifica",
  "ignifugo": "Excelente (PIR - Alta resistencia al fuego)",
  "aplicacion": "Cámaras frigoríficas, cuartos fríos, industria alimenticia",
  "espesores": {
    "50": { "resistencia_termica": 2.27 },
    "80": { "resistencia_termica": 3.64 },
    "100": { "resistencia_termica": 4.55 },
    "120": { "resistencia_termica": 5.45 }
  }
}
```

**Catálogo actualizado:**
- **Techo/Cubiertas:** Isodec EPS, Isodec PIR, Isoroof/Isoroof Plus 3G, Chapas convencionales
- **Paredes/Fachadas:** Isopanel EPS, Isowall PIR, **Isofrig PIR** (cámaras frigoríficas)

---

### KB-004: Política de Transcripción de Audio (Prioridad P1)

**Problema identificado:**
Inconsistencia sobre la capacidad de transcribir audios (en un momento se dijo que no se podía, luego se entregó una "transcripción").

**Corrección aplicada:**
Se definió una política operativa consistente:

> **Panelin NO puede transcribir audios directamente** desde archivos .ogg, .mp3 u otros formatos.
> 
> Si el usuario envía un audio:
> 1. Solicitar que proporcione el contenido en texto o transcripción aproximada
> 2. Con el texto, se puede realizar análisis del discurso, feedback y sugerencias
> 3. NUNCA afirmar que se puede transcribir un audio cuando no se tiene esa capacidad

Se actualizó el campo `capabilities.audio_transcription: false` en la configuración.

---

## Temas Pendientes (P2 / Para Futuro)

### Playbook de Ventas - "Por qué elegir BMC"
**Estado:** Abierto

El argumento de "por qué los clientes elegirían BMC" fue marcado como "no del todo correcto" y quedó pendiente de profundización.

**Próximos pasos sugeridos:**
- Trabajar con casos reales (ventas ganadas/perdidas)
- Segmentar por tipo de cliente/obra (industria, vivienda, agro)
- Identificar variables clave (precio, riesgo fuego, condensación, estructura)
- Construir razones basadas en evidencia empírica

---

## Resumen de Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `BMC_Base_Conocimiento_GPT-2.json` | +sección institucional, +diferencial, +Isofrig PIR |
| `gpt_configs/INSTRUCCIONES_PANELIN_ACTUALIZADAS.txt` | +aclaración institucional, +diferencial, +catálogo, +política audio |
| `gpt_configs/Panelin_Asistente_Integral_BMC_config.json` | +descripción, +instrucciones, +capabilities audio |
| `PANELIN_INSTRUCTIONS_FINAL.txt` | +aclaración institucional, +diferencial, +catálogo, +política audio |
| `PANELIN_ULTIMATE_INSTRUCTIONS.md` | +aclaración institucional, +diferencial, +catálogo, +política audio |

---

## Fecha de Implementación
2026-01-24

## Origen
Conversación de alineación conceptual con Ramiro (Equipo de asesoramiento y ventas / soluciones técnicas BMC)
