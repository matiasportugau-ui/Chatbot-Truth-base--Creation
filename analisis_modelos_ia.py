#!/usr/bin/env python3
"""
Análisis de Modelos IA para Procedimientos
===========================================

Analiza cada procedimiento y determina el mejor modelo (OpenAI/Claude/Gemini)
para cada tarea, asignando roles específicos.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import json


class ModeloIA(Enum):
    """Modelos de IA disponibles"""
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"


class TipoTarea(Enum):
    """Tipos de tareas del sistema"""
    # Análisis y procesamiento
    REVISAR_INPUTS = "revisar_inputs"
    EXTRAER_DATOS_PDF = "extraer_datos_pdf"
    BUSCAR_PDF = "buscar_pdf"
    
    # Cálculos y validación
    GENERAR_PRESUPUESTO = "generar_presupuesto"
    VALIDAR_AUTOPORTANCIA = "validar_autoportancia"
    CALCULAR_MATERIALES = "calcular_materiales"
    
    # Análisis y comparación
    COMPARAR_RESULTADOS = "comparar_resultados"
    ANALIZAR_DIFERENCIAS = "analizar_diferencias"
    IDENTIFICAR_CAUSAS = "identificar_causas"
    
    # Aprendizaje y mejora
    APRENDER_DIFERENCIAS = "aprender_diferencias"
    GENERAR_LECCIONES = "generar_lecciones"
    SUGERIR_MEJORAS = "sugerir_mejoras"
    
    # Interacción con cliente
    COTIZACION_INTERACTIVA = "cotizacion_interactiva"
    PRESENTACION_PROFESIONAL = "presentacion_profesional"
    RECOMENDACIONES_TECNICAS = "recomendaciones_tecnicas"
    
    # Procesamiento de conocimiento
    PROCESAR_BASE_CONOCIMIENTO = "procesar_base_conocimiento"
    ACTUALIZAR_CONOCIMIENTO = "actualizar_conocimiento"
    VALIDAR_FORMULAS = "validar_formulas"


# Análisis de fortalezas por modelo
FORTALEZAS_MODELOS = {
    ModeloIA.OPENAI: {
        "fortalezas": [
            "Function Calling nativo y robusto",
            "Code Interpreter integrado",
            "Acceso directo a archivos",
            "Excelente para cálculos precisos",
            "Buen razonamiento estructurado",
            "Mejor integración con APIs"
        ],
        "debilidades": [
            "Costo más alto",
            "Contexto limitado comparado con Claude"
        ],
        "mejor_para": [
            "Cálculos matemáticos",
            "Function Calling",
            "Procesamiento de archivos",
            "Tareas que requieren precisión",
            "Integración con sistemas"
        ]
    },
    ModeloIA.CLAUDE: {
        "fortalezas": [
            "Análisis profundo y razonamiento",
            "Contexto muy largo (200k tokens)",
            "Excelente comprensión de texto",
            "Mejor para análisis cualitativos",
            "Muy bueno para interpretación",
            "Excelente para aprendizaje"
        ],
        "debilidades": [
            "Function Calling menos integrado",
            "No tiene Code Interpreter nativo",
            "Costo similar a OpenAI"
        ],
        "mejor_para": [
            "Análisis de diferencias",
            "Interpretación de resultados",
            "Aprendizaje y lecciones",
            "Análisis cualitativo",
            "Comprensión de contexto largo"
        ]
    },
    ModeloIA.GEMINI: {
        "fortalezas": [
            "Gratis para desarrollo",
            "Multimodal (texto, imágenes)",
            "Buen rendimiento general",
            "Function Calling disponible",
            "Bajo costo"
        ],
        "debilidades": [
            "Menos preciso que OpenAI/Claude",
            "Function Calling menos robusto",
            "Menos documentación"
        ],
        "mejor_para": [
            "Tareas generales",
            "Procesamiento batch",
            "Desarrollo y testing",
            "Tareas que no requieren máxima precisión"
        ]
    }
}


# Asignación de modelos por tarea
ASIGNACION_MODELOS = {
    # ============================================================
    # ANÁLISIS Y PROCESAMIENTO
    # ============================================================
    TipoTarea.REVISAR_INPUTS: {
        "modelo_principal": ModeloIA.GEMINI,
        "modelo_secundario": ModeloIA.OPENAI,
        "razon": "Tarea simple de procesamiento, Gemini es suficiente y más económico",
        "requisitos": ["Procesamiento de CSV", "Parsing de datos"]
    },
    
    TipoTarea.EXTRAER_DATOS_PDF: {
        "modelo_principal": ModeloIA.OPENAI,
        "modelo_secundario": ModeloIA.CLAUDE,
        "razon": "OpenAI tiene Code Interpreter para procesar PDFs, Claude para análisis de texto complejo",
        "requisitos": ["Procesamiento de PDF", "Extracción de texto", "Parsing de números"]
    },
    
    TipoTarea.BUSCAR_PDF: {
        "modelo_principal": ModeloIA.GEMINI,
        "modelo_secundario": ModeloIA.OPENAI,
        "razon": "Búsqueda de archivos es tarea simple, Gemini es eficiente",
        "requisitos": ["Búsqueda de archivos", "Correlación de nombres"]
    },
    
    # ============================================================
    # CÁLCULOS Y VALIDACIÓN
    # ============================================================
    TipoTarea.GENERAR_PRESUPUESTO: {
        "modelo_principal": ModeloIA.OPENAI,
        "modelo_secundario": ModeloIA.GEMINI,
        "razon": "OpenAI tiene Function Calling nativo y Code Interpreter para cálculos precisos",
        "requisitos": ["Cálculos matemáticos", "Function Calling", "Precisión"]
    },
    
    TipoTarea.VALIDAR_AUTOPORTANCIA: {
        "modelo_principal": ModeloIA.OPENAI,
        "modelo_secundario": ModeloIA.GEMINI,
        "razon": "Validación técnica requiere precisión, OpenAI es mejor",
        "requisitos": ["Validación técnica", "Comparación numérica", "Precisión"]
    },
    
    TipoTarea.CALCULAR_MATERIALES: {
        "modelo_principal": ModeloIA.OPENAI,
        "modelo_secundario": ModeloIA.GEMINI,
        "razon": "Cálculos de materiales requieren precisión matemática, OpenAI es superior",
        "requisitos": ["Cálculos matemáticos", "Fórmulas", "Precisión"]
    },
    
    # ============================================================
    # ANÁLISIS Y COMPARACIÓN
    # ============================================================
    TipoTarea.COMPARAR_RESULTADOS: {
        "modelo_principal": ModeloIA.CLAUDE,
        "modelo_secundario": ModeloIA.OPENAI,
        "razon": "Claude es excelente para análisis comparativo y razonamiento",
        "requisitos": ["Análisis comparativo", "Razonamiento", "Interpretación"]
    },
    
    TipoTarea.ANALIZAR_DIFERENCIAS: {
        "modelo_principal": ModeloIA.CLAUDE,
        "modelo_secundario": ModeloIA.OPENAI,
        "razon": "Claude sobresale en análisis profundo y comprensión de causas",
        "requisitos": ["Análisis profundo", "Comprensión de contexto", "Razonamiento causal"]
    },
    
    TipoTarea.IDENTIFICAR_CAUSAS: {
        "modelo_principal": ModeloIA.CLAUDE,
        "modelo_secundario": ModeloIA.OPENAI,
        "razon": "Claude es mejor para razonamiento causal y análisis de causas raíz",
        "requisitos": ["Razonamiento causal", "Análisis de causas raíz", "Comprensión profunda"]
    },
    
    # ============================================================
    # APRENDIZAJE Y MEJORA
    # ============================================================
    TipoTarea.APRENDER_DIFERENCIAS: {
        "modelo_principal": ModeloIA.CLAUDE,
        "modelo_secundario": ModeloIA.OPENAI,
        "razon": "Claude es superior para aprendizaje y extracción de patrones",
        "requisitos": ["Aprendizaje", "Extracción de patrones", "Síntesis"]
    },
    
    TipoTarea.GENERAR_LECCIONES: {
        "modelo_principal": ModeloIA.CLAUDE,
        "modelo_secundario": ModeloIA.OPENAI,
        "razon": "Claude genera lecciones más profundas y útiles",
        "requisitos": ["Síntesis", "Generación de conocimiento", "Comprensión profunda"]
    },
    
    TipoTarea.SUGERIR_MEJORAS: {
        "modelo_principal": ModeloIA.CLAUDE,
        "modelo_secundario": ModeloIA.OPENAI,
        "razon": "Claude es mejor para sugerencias creativas y mejoras",
        "requisitos": ["Creatividad", "Sugerencias", "Mejora continua"]
    },
    
    # ============================================================
    # INTERACCIÓN CON CLIENTE
    # ============================================================
    TipoTarea.COTIZACION_INTERACTIVA: {
        "modelo_principal": ModeloIA.OPENAI,
        "modelo_secundario": ModeloIA.CLAUDE,
        "razon": "OpenAI tiene mejor Function Calling para interacción dinámica",
        "requisitos": ["Function Calling", "Interacción dinámica", "Respuestas rápidas"]
    },
    
    TipoTarea.PRESENTACION_PROFESIONAL: {
        "modelo_principal": ModeloIA.CLAUDE,
        "modelo_secundario": ModeloIA.OPENAI,
        "razon": "Claude genera presentaciones más profesionales y bien estructuradas",
        "requisitos": ["Generación de texto", "Estructura", "Profesionalismo"]
    },
    
    TipoTarea.RECOMENDACIONES_TECNICAS: {
        "modelo_principal": ModeloIA.CLAUDE,
        "modelo_secundario": ModeloIA.OPENAI,
        "razon": "Claude es mejor para recomendaciones técnicas bien fundamentadas",
        "requisitos": ["Razonamiento técnico", "Recomendaciones", "Fundamentación"]
    },
    
    # ============================================================
    # PROCESAMIENTO DE CONOCIMIENTO
    # ============================================================
    TipoTarea.PROCESAR_BASE_CONOCIMIENTO: {
        "modelo_principal": ModeloIA.OPENAI,
        "modelo_secundario": ModeloIA.GEMINI,
        "razon": "OpenAI tiene mejor acceso a archivos y Code Interpreter",
        "requisitos": ["Procesamiento de archivos", "Code Interpreter", "Acceso a KB"]
    },
    
    TipoTarea.ACTUALIZAR_CONOCIMIENTO: {
        "modelo_principal": ModeloIA.CLAUDE,
        "modelo_secundario": ModeloIA.OPENAI,
        "razon": "Claude es mejor para síntesis y actualización de conocimiento",
        "requisitos": ["Síntesis", "Actualización", "Comprensión de cambios"]
    },
    
    TipoTarea.VALIDAR_FORMULAS: {
        "modelo_principal": ModeloIA.OPENAI,
        "modelo_secundario": ModeloIA.GEMINI,
        "razon": "OpenAI tiene Code Interpreter para validar fórmulas matemáticas",
        "requisitos": ["Validación matemática", "Code Interpreter", "Precisión"]
    }
}


def analizar_procedimiento(tarea: TipoTarea) -> Dict[str, Any]:
    """Analiza un procedimiento y retorna recomendación de modelo"""
    asignacion = ASIGNACION_MODELOS.get(tarea)
    if not asignacion:
        return {
            "tarea": tarea.value,
            "error": "Tarea no encontrada"
        }
    
    modelo_principal = asignacion["modelo_principal"]
    modelo_secundario = asignacion["modelo_secundario"]
    
    fortalezas_principal = FORTALEZAS_MODELOS[modelo_principal]
    fortalezas_secundario = FORTALEZAS_MODELOS[modelo_secundario]
    
    return {
        "tarea": tarea.value,
        "modelo_recomendado": modelo_principal.value,
        "modelo_alternativo": modelo_secundario.value,
        "razon": asignacion["razon"],
        "requisitos": asignacion["requisitos"],
        "fortalezas_principal": fortalezas_principal["fortalezas"],
        "fortalezas_secundario": fortalezas_secundario["fortalezas"],
        "cuando_usar_alternativo": f"Usar {modelo_secundario.value} si {modelo_principal.value} no está disponible o hay problemas de costo"
    }


def generar_reporte_completo() -> Dict[str, Any]:
    """Genera reporte completo de asignación de modelos"""
    reporte = {
        "resumen": {
            "total_tareas": len(ASIGNACION_MODELOS),
            "distribucion": {
                "openai": sum(1 for a in ASIGNACION_MODELOS.values() if a["modelo_principal"] == ModeloIA.OPENAI),
                "claude": sum(1 for a in ASIGNACION_MODELOS.values() if a["modelo_principal"] == ModeloIA.CLAUDE),
                "gemini": sum(1 for a in ASIGNACION_MODELOS.values() if a["modelo_principal"] == ModeloIA.GEMINI)
            }
        },
        "asignaciones": {}
    }
    
    for tarea in TipoTarea:
        reporte["asignaciones"][tarea.value] = analizar_procedimiento(tarea)
    
    return reporte


def obtener_modelo_para_tarea(tarea: TipoTarea, usar_alternativo: bool = False) -> ModeloIA:
    """Obtiene el modelo recomendado para una tarea"""
    asignacion = ASIGNACION_MODELOS.get(tarea)
    if not asignacion:
        return ModeloIA.OPENAI  # Default
    
    if usar_alternativo:
        return asignacion["modelo_secundario"]
    return asignacion["modelo_principal"]


if __name__ == "__main__":
    print("=" * 70)
    print("📊 ANÁLISIS DE MODELOS IA POR PROCEDIMIENTO")
    print("=" * 70)
    
    reporte = generar_reporte_completo()
    
    print(f"\n📈 RESUMEN")
    print(f"   Total de tareas: {reporte['resumen']['total_tareas']}")
    print(f"   Distribución:")
    print(f"     - OpenAI: {reporte['resumen']['distribucion']['openai']} tareas")
    print(f"     - Claude: {reporte['resumen']['distribucion']['claude']} tareas")
    print(f"     - Gemini: {reporte['resumen']['distribucion']['gemini']} tareas")
    
    print(f"\n📋 ASIGNACIONES POR CATEGORÍA\n")
    
    categorias = {
        "ANÁLISIS Y PROCESAMIENTO": [
            TipoTarea.REVISAR_INPUTS,
            TipoTarea.EXTRAER_DATOS_PDF,
            TipoTarea.BUSCAR_PDF
        ],
        "CÁLCULOS Y VALIDACIÓN": [
            TipoTarea.GENERAR_PRESUPUESTO,
            TipoTarea.VALIDAR_AUTOPORTANCIA,
            TipoTarea.CALCULAR_MATERIALES
        ],
        "ANÁLISIS Y COMPARACIÓN": [
            TipoTarea.COMPARAR_RESULTADOS,
            TipoTarea.ANALIZAR_DIFERENCIAS,
            TipoTarea.IDENTIFICAR_CAUSAS
        ],
        "APRENDIZAJE Y MEJORA": [
            TipoTarea.APRENDER_DIFERENCIAS,
            TipoTarea.GENERAR_LECCIONES,
            TipoTarea.SUGERIR_MEJORAS
        ],
        "INTERACCIÓN CON CLIENTE": [
            TipoTarea.COTIZACION_INTERACTIVA,
            TipoTarea.PRESENTACION_PROFESIONAL,
            TipoTarea.RECOMENDACIONES_TECNICAS
        ],
        "PROCESAMIENTO DE CONOCIMIENTO": [
            TipoTarea.PROCESAR_BASE_CONOCIMIENTO,
            TipoTarea.ACTUALIZAR_CONOCIMIENTO,
            TipoTarea.VALIDAR_FORMULAS
        ]
    }
    
    for categoria, tareas in categorias.items():
        print(f"  {categoria}")
        print("  " + "-" * 68)
        for tarea in tareas:
            analisis = analizar_procedimiento(tarea)
            modelo = analisis["modelo_recomendado"].upper()
            print(f"    • {tarea.value.replace('_', ' ').title()}")
            print(f"      → {modelo} (alternativa: {analisis['modelo_alternativo'].upper()})")
            print(f"      → {analisis['razon']}")
        print()
    
    # Guardar reporte
    with open("reporte_asignacion_modelos.json", "w", encoding="utf-8") as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"💾 Reporte completo guardado en: reporte_asignacion_modelos.json")
