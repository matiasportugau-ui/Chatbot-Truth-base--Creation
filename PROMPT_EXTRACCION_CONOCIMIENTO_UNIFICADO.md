# PROMPT: Extracción y Unificación del Conocimiento para GPT OpenAI

## Objetivo
Extraer de cada rama del proyecto **Chatbot-Truth-base--Creation** las correcciones realizadas y generar un archivo unificado de conocimiento para crear un GPT de OpenAI con la misma lógica de Panelin.

---

## PARTE 1: Identificación de Archivos Clave

### Archivos de Conocimiento (Knowledge Base)

| Prioridad | Archivo | Ruta | Propósito |
|-----------|---------|------|-----------|
| **CRÍTICO** | `BMC_Base_Conocimiento_GPT-2.json` | `/` | Base de verdad absoluta - Productos, precios, fórmulas |
| **CRÍTICO** | `PANELIN_ULTIMATE_INSTRUCTIONS.md` | `/` | Instrucciones completas del GPT |
| **ALTO** | `BMC_Base_Unificada_v4.json` | `/Files/` | Validación cruzada |
| **ALTO** | `panelin_truth_bmcuruguay_web_only_v2.json` | `/` | Datos dinámicos de la tienda |
| **MEDIO** | `panelin_context_consolidacion_sin_backend.md` | `/` | Workflow SOP y comandos |
| **MEDIO** | `Aleros -2.rtf` | `/Files/` | Reglas técnicas específicas |

### Archivos de Configuración GPT

| Archivo | Ruta | Uso |
|---------|------|-----|
| `Panelin Knowledge Base Assistant_config.json` | `/gpt_configs/` | Configuración JSON para OpenAI |
| `INSTRUCCIONES_PANELIN_ACTUALIZADAS.txt` | `/gpt_configs/` | Instrucciones actualizadas |
| `PANELIN_INSTRUCTIONS_OPTIMIZED.md` | `/` | Versión compacta (<8000 chars) |

### Archivos de Entrenamiento

| Archivo | Ruta | Contenido |
|---------|------|-----------|
| `sample_interactions.json` | `/training_data/interactions/` | Ejemplos de interacciones |
| `sample_quotes.json` | `/training_data/quotes/` | Ejemplos de cotizaciones |

---

## PARTE 2: Historial de Correcciones por Rama

### Ramas del Proyecto

```
1. main (principal)
2. claude/gpt-knowledge-analysis-SSJYE (análisis de conocimiento)
3. copilot/analyze-and-resolve-issues (corrección de issues)
4. copilot/checkout-pull-request-5
5. changes (mejoras varias)
6. copilot/create-gemini-knowledge-base
```

### Correcciones Identificadas (Commits Relevantes)

#### PR #8: claude/gpt-knowledge-analysis-SSJYE
- Análisis y configuración optimizada del GPT
- Documento de análisis de conocimiento GPT

#### PR #7: copilot/analyze-and-resolve-issues
- Resolución de issues detectados

#### PR #5: claude/gpt-knowledge-analysis-SSJYE
- Plan inicial de análisis

#### Rama changes:
- **Agente integrador de conocimiento** (`agente_integrador_conocimiento.py`)
- Mejoras en procesamiento de datos
- Guías de uso actualizadas

#### Commits individuales importantes:
- `1eee664`: Mejoras en PANELIN_ULTIMATE_INSTRUCTIONS.md
- `308923a`: Cálculos de ahorro energético actualizados
- `03363e2`: Integración MongoDB para ingesta
- `d89408c`: Refactor lectura PDFs y export Instagram

---

## PARTE 3: Prompt para Extraer Conocimiento

```markdown
Analiza el proyecto Chatbot-Truth-base--Creation y extrae el conocimiento para crear un GPT de OpenAI.

### PASO 1: Lee los archivos de conocimiento base
1. Lee `BMC_Base_Conocimiento_GPT-2.json` - Extraer:
   - Productos y sus propiedades
   - Precios por espesor
   - Coeficientes térmicos
   - Fórmulas de cotización
   - Datos de referencia (kWh, grados-día)

2. Lee `PANELIN_ULTIMATE_INSTRUCTIONS.md` - Extraer:
   - Identidad del bot
   - Proceso de cotización (5 fases)
   - Guardrails y validaciones
   - Personalización por usuario

3. Lee `BMC_Base_Unificada_v4.json` - Extraer:
   - Datos de validación cruzada
   - Posibles inconsistencias

### PASO 2: Identifica correcciones en cada rama
Para cada rama, ejecuta:
```bash
git log <branch> --oneline --since="2025-01-01"
git diff main..<branch> -- "*.json" "*.md" "*.txt"
```

Documenta:
- Qué archivos fueron modificados
- Qué correcciones se aplicaron
- Si hay conflictos entre ramas

### PASO 3: Unifica el conocimiento
Genera un archivo `CONOCIMIENTO_UNIFICADO_GPT.json` con:

{
  "metadata": {
    "version": "1.0",
    "fecha_generacion": "YYYY-MM-DD",
    "ramas_analizadas": ["main", "..."],
    "commits_incluidos": ["..."]
  },
  "base_conocimiento": {
    "productos": [...],
    "precios": {...},
    "formulas": {...},
    "reglas_negocio": [...]
  },
  "instrucciones_gpt": {
    "identidad": "...",
    "proceso_cotizacion": [...],
    "guardrails": [...],
    "personalizaciones": {...}
  },
  "correcciones_aplicadas": [
    {
      "rama": "...",
      "commit": "...",
      "descripcion": "...",
      "archivos_afectados": [...]
    }
  ]
}
```

---

## PARTE 4: Checklist de Validación

Antes de crear el GPT, verifica:

- [ ] `BMC_Base_Conocimiento_GPT-2.json` es la fuente primaria
- [ ] Las fórmulas de cotización están correctas
- [ ] Los precios están actualizados
- [ ] Las instrucciones incluyen las 5 fases de cotización
- [ ] Los guardrails están definidos
- [ ] El análisis de ahorro energético está incluido
- [ ] Las personalizaciones por usuario están definidas
- [ ] Los comandos SOP funcionan (/estado, /checkpoint, /consolidar)

---

## PARTE 5: Estructura Final para OpenAI GPT

### 1. Campo "Instructions" (copiar de):
- `PANELIN_INSTRUCTIONS_OPTIMIZED.md` (versión compacta)
- O `PANELIN_ULTIMATE_INSTRUCTIONS.md` (versión completa)

### 2. Knowledge Files (subir):
1. `BMC_Base_Conocimiento_GPT-2.json`
2. `panelin_truth_bmcuruguay_web_only_v2.json`
3. `BMC_Base_Unificada_v4.json`
4. `CONOCIMIENTO_UNIFICADO_GPT.json` (generado)

### 3. Capabilities:
```json
{
  "web_browsing": false,
  "code_interpreter": true,
  "dall_e": false,
  "file_uploads": true
}
```

### 4. Conversation Starters:
- "Cotizame X m² de techo con ISODEC EPS 100mm"
- "¿Cuál es la autoportancia del ISOROOF 3G?"
- "Compara EPS vs PIR para una cubierta"
- "¿Qué accesorios necesito para instalar paneles?"

---

## PARTE 6: Comandos Git para Extraer Diferencias

```bash
# Ver todas las ramas
git branch -a

# Ver commits de una rama específica
git log origin/<rama> --oneline -20

# Ver diferencias entre main y una rama
git diff main..origin/<rama> -- "*.json" "*.md"

# Ver qué archivos cambiaron en una rama
git diff --name-only main..origin/<rama>

# Ver el contenido de un commit específico
git show <commit-hash>

# Exportar diff a archivo
git diff main..origin/<rama> > diff_rama.txt
```

---

## PARTE 7: Script de Extracción Automática

```python
#!/usr/bin/env python3
"""
Script para extraer conocimiento de todas las ramas
y generar archivo unificado para GPT OpenAI
"""
import json
import subprocess
import os
from datetime import datetime

def get_branches():
    result = subprocess.run(
        ['git', 'branch', '-a'],
        capture_output=True, text=True
    )
    return [b.strip() for b in result.stdout.split('\n') if b.strip()]

def get_commits(branch, since='2025-01-01'):
    result = subprocess.run(
        ['git', 'log', branch, '--oneline', f'--since={since}'],
        capture_output=True, text=True
    )
    return result.stdout.strip().split('\n')

def get_diff(branch1, branch2, file_pattern='*.json'):
    result = subprocess.run(
        ['git', 'diff', f'{branch1}..{branch2}', '--', file_pattern],
        capture_output=True, text=True
    )
    return result.stdout

def load_knowledge_base(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_unified_knowledge():
    # Cargar base de conocimiento principal
    kb_principal = load_knowledge_base('BMC_Base_Conocimiento_GPT-2.json')

    # Obtener ramas
    branches = get_branches()

    # Compilar correcciones
    correcciones = []
    for branch in branches:
        commits = get_commits(branch)
        for commit in commits:
            correcciones.append({
                'rama': branch,
                'commit': commit,
                'fecha': datetime.now().isoformat()
            })

    # Generar conocimiento unificado
    conocimiento_unificado = {
        'metadata': {
            'version': '1.0',
            'fecha_generacion': datetime.now().isoformat(),
            'ramas_analizadas': branches
        },
        'base_conocimiento': kb_principal,
        'correcciones': correcciones
    }

    # Guardar
    with open('CONOCIMIENTO_UNIFICADO_GPT.json', 'w', encoding='utf-8') as f:
        json.dump(conocimiento_unificado, f, ensure_ascii=False, indent=2)

    print("✓ Conocimiento unificado generado: CONOCIMIENTO_UNIFICADO_GPT.json")

if __name__ == '__main__':
    generate_unified_knowledge()
```

---

## Uso de Este Documento

1. **Para consultar el GPT actual**: Usa los archivos identificados en PARTE 1
2. **Para corregir errores**: Documenta en PARTE 2 y actualiza los archivos base
3. **Para recrear el GPT**: Sigue PARTE 5 con los archivos unificados
4. **Para extraer diferencias**: Usa los comandos de PARTE 6

---

*Generado el: 2026-01-24*
*Proyecto: Chatbot-Truth-base--Creation*
*Propósito: Extracción y unificación de conocimiento para GPT OpenAI*
