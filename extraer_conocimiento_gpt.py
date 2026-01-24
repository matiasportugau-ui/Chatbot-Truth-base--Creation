#!/usr/bin/env python3
"""
Script para extraer conocimiento de todas las ramas del proyecto
Chatbot-Truth-base--Creation y generar archivo unificado para GPT OpenAI.

Uso:
    python extraer_conocimiento_gpt.py

Salida:
    - CONOCIMIENTO_UNIFICADO_GPT.json
    - reporte_extraccion.md
"""
import json
import subprocess
import os
from datetime import datetime
from pathlib import Path


def run_git_command(args):
    """Ejecuta un comando git y retorna el output."""
    try:
        result = subprocess.run(
            ['git'] + args,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error ejecutando git {' '.join(args)}: {e}")
        return ""


def get_all_branches():
    """Obtiene todas las ramas del repositorio."""
    output = run_git_command(['branch', '-a'])
    branches = []
    for line in output.split('\n'):
        branch = line.strip().replace('* ', '').replace('remotes/origin/', '')
        if branch and 'HEAD' not in branch:
            branches.append(branch)
    return list(set(branches))


def get_commits_since(branch, since='2025-01-01'):
    """Obtiene commits de una rama desde una fecha."""
    output = run_git_command([
        'log', branch, '--oneline', f'--since={since}', '--format=%H|%s|%ai'
    ])
    commits = []
    for line in output.split('\n'):
        if line and '|' in line:
            parts = line.split('|')
            if len(parts) >= 3:
                commits.append({
                    'hash': parts[0][:8],
                    'message': parts[1],
                    'date': parts[2]
                })
    return commits


def get_changed_files(branch1='main', branch2='HEAD'):
    """Obtiene archivos modificados entre dos ramas."""
    output = run_git_command(['diff', '--name-only', f'{branch1}..{branch2}'])
    return [f for f in output.split('\n') if f]


def load_json_file(filepath):
    """Carga un archivo JSON."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error cargando {filepath}: {e}")
        return None


def load_text_file(filepath):
    """Carga un archivo de texto."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error cargando {filepath}: {e}")
        return None


def extract_knowledge():
    """Extrae y unifica el conocimiento del proyecto."""
    base_path = Path(__file__).parent

    print("=" * 60)
    print("EXTRACCIÓN DE CONOCIMIENTO - CHATBOT TRUTH BASE")
    print("=" * 60)

    # 1. Cargar base de conocimiento principal
    print("\n[1/5] Cargando base de conocimiento principal...")
    kb_principal = load_json_file(base_path / 'BMC_Base_Conocimiento_GPT-2.json')
    if not kb_principal:
        kb_principal = load_json_file(base_path / 'BMC_Base_Conocimiento_GPT.json')

    # 2. Cargar datos dinámicos
    print("[2/5] Cargando datos dinámicos de la tienda...")
    datos_tienda = load_json_file(base_path / 'panelin_truth_bmcuruguay_web_only_v2.json')

    # 3. Cargar base unificada para validación
    print("[3/5] Cargando base de validación...")
    kb_validacion = load_json_file(base_path / 'Files' / 'BMC_Base_Unificada_v4.json')

    # 4. Cargar instrucciones
    print("[4/5] Cargando instrucciones del GPT...")
    instrucciones = load_text_file(base_path / 'PANELIN_ULTIMATE_INSTRUCTIONS.md')
    instrucciones_compactas = load_text_file(base_path / 'PANELIN_INSTRUCTIONS_OPTIMIZED.md')

    # 5. Analizar ramas y correcciones
    print("[5/5] Analizando ramas y correcciones...")
    branches = get_all_branches()

    correcciones_por_rama = {}
    for branch in branches:
        commits = get_commits_since(branch)
        if commits:
            correcciones_por_rama[branch] = commits

    # Compilar conocimiento unificado
    print("\nCompilando conocimiento unificado...")

    conocimiento_unificado = {
        "metadata": {
            "version": "1.0.0",
            "fecha_generacion": datetime.now().isoformat(),
            "proyecto": "Chatbot-Truth-base--Creation",
            "proposito": "Base de conocimiento unificada para GPT OpenAI Panelin",
            "ramas_analizadas": branches,
            "total_commits_analizados": sum(len(c) for c in correcciones_por_rama.values())
        },
        "fuentes_conocimiento": {
            "nivel_1_master": {
                "archivo": "BMC_Base_Conocimiento_GPT-2.json",
                "descripcion": "Fuente de verdad absoluta - productos, precios, fórmulas",
                "contenido": kb_principal
            },
            "nivel_2_validacion": {
                "archivo": "BMC_Base_Unificada_v4.json",
                "descripcion": "Cross-reference para validación",
                "disponible": kb_validacion is not None
            },
            "nivel_3_dinamico": {
                "archivo": "panelin_truth_bmcuruguay_web_only_v2.json",
                "descripcion": "Datos actualizados de la tienda Shopify",
                "contenido": datos_tienda
            }
        },
        "instrucciones_gpt": {
            "version_completa": {
                "archivo": "PANELIN_ULTIMATE_INSTRUCTIONS.md",
                "caracteres": len(instrucciones) if instrucciones else 0
            },
            "version_compacta": {
                "archivo": "PANELIN_INSTRUCTIONS_OPTIMIZED.md",
                "caracteres": len(instrucciones_compactas) if instrucciones_compactas else 0
            }
        },
        "correcciones_por_rama": correcciones_por_rama,
        "archivos_para_gpt_openai": {
            "instructions": "PANELIN_INSTRUCTIONS_OPTIMIZED.md",
            "knowledge_files": [
                "BMC_Base_Conocimiento_GPT-2.json",
                "panelin_truth_bmcuruguay_web_only_v2.json",
                "Files/BMC_Base_Unificada_v4.json"
            ],
            "capabilities": {
                "web_browsing": False,
                "code_interpreter": True,
                "dall_e": False,
                "file_uploads": True
            }
        }
    }

    # Guardar conocimiento unificado
    output_file = base_path / 'CONOCIMIENTO_UNIFICADO_GPT.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(conocimiento_unificado, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Archivo generado: {output_file}")

    # Generar reporte
    generate_report(conocimiento_unificado, base_path)

    return conocimiento_unificado


def generate_report(conocimiento, base_path):
    """Genera un reporte markdown del conocimiento extraído."""

    report = f"""# Reporte de Extracción de Conocimiento

**Fecha de generación:** {conocimiento['metadata']['fecha_generacion']}
**Proyecto:** {conocimiento['metadata']['proyecto']}

## Resumen

- **Ramas analizadas:** {len(conocimiento['metadata']['ramas_analizadas'])}
- **Total commits:** {conocimiento['metadata']['total_commits_analizados']}

## Ramas Analizadas

"""

    for rama in conocimiento['metadata']['ramas_analizadas']:
        report += f"- `{rama}`\n"

    report += """
## Correcciones por Rama

"""

    for rama, commits in conocimiento['correcciones_por_rama'].items():
        report += f"### {rama}\n\n"
        for commit in commits[:10]:  # Limitar a 10 commits por rama
            report += f"- `{commit['hash']}`: {commit['message']}\n"
        if len(commits) > 10:
            report += f"- ... y {len(commits) - 10} commits más\n"
        report += "\n"

    report += """
## Archivos para Crear GPT OpenAI

### 1. Instructions (copiar contenido de):
- `PANELIN_INSTRUCTIONS_OPTIMIZED.md` (recomendado, <8000 chars)
- O `PANELIN_ULTIMATE_INSTRUCTIONS.md` (versión completa)

### 2. Knowledge Files (subir estos archivos):
1. `BMC_Base_Conocimiento_GPT-2.json` - Base de verdad absoluta
2. `panelin_truth_bmcuruguay_web_only_v2.json` - Datos de tienda
3. `Files/BMC_Base_Unificada_v4.json` - Validación cruzada

### 3. Capabilities:
- Code Interpreter: ✓ Habilitado
- Web Browsing: ✗ Deshabilitado
- DALL-E: ✗ Deshabilitado
- File Uploads: ✓ Habilitado

### 4. Conversation Starters sugeridos:
- "Cotizame X m² de techo con ISODEC EPS 100mm"
- "¿Cuál es la autoportancia del ISOROOF 3G?"
- "Compara EPS vs PIR para una cubierta"
- "¿Qué accesorios necesito para instalar paneles?"

## Próximos Pasos

1. Ir a https://chat.openai.com/gpts/editor
2. Crear nuevo GPT con nombre "Panelin - Asistente BMC"
3. Pegar instrucciones de `PANELIN_INSTRUCTIONS_OPTIMIZED.md`
4. Subir los Knowledge Files listados arriba
5. Configurar capabilities según indicado
6. Probar con los conversation starters

---
*Generado automáticamente por extraer_conocimiento_gpt.py*
"""

    report_file = base_path / 'REPORTE_EXTRACCION_CONOCIMIENTO.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✓ Reporte generado: {report_file}")


if __name__ == '__main__':
    extract_knowledge()
    print("\n" + "=" * 60)
    print("EXTRACCIÓN COMPLETADA")
    print("=" * 60)
    print("\nArchivos generados:")
    print("  - CONOCIMIENTO_UNIFICADO_GPT.json")
    print("  - REPORTE_EXTRACCION_CONOCIMIENTO.md")
    print("\nUsa estos archivos para crear tu GPT en OpenAI.")
