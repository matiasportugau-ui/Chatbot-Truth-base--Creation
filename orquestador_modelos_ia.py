#!/usr/bin/env python3
"""
Orquestador de Modelos IA
==========================

Sistema que asigna tareas al mejor modelo (OpenAI/Claude/Gemini)
según el tipo de procedimiento y permite intercambio dinámico.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import json

# Importar análisis de modelos
sys.path.insert(0, str(Path(__file__).parent))
from analisis_modelos_ia import (
    ModeloIA, TipoTarea, obtener_modelo_para_tarea,
    analizar_procedimiento, ASIGNACION_MODELOS
)


class OrquestadorModelos:
    """Orquestador que asigna tareas al mejor modelo"""
    
    def __init__(self):
        self.modelos_disponibles = self._detectar_modelos_disponibles()
        self.estadisticas = {
            "tareas_ejecutadas": 0,
            "por_modelo": {
                "openai": 0,
                "claude": 0,
                "gemini": 0
            },
            "fallos": 0,
            "cambios_modelo": 0
        }
    
    def _detectar_modelos_disponibles(self) -> Dict[ModeloIA, bool]:
        """Detecta qué modelos están disponibles"""
        disponibles = {}
        
        # OpenAI
        try:
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            disponibles[ModeloIA.OPENAI] = api_key is not None
        except ImportError:
            disponibles[ModeloIA.OPENAI] = False
        
        # Claude
        try:
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            disponibles[ModeloIA.CLAUDE] = api_key is not None
        except ImportError:
            disponibles[ModeloIA.CLAUDE] = False
        
        # Gemini
        try:
            import google.generativeai as genai
            api_key = os.getenv("GOOGLE_API_KEY")
            disponibles[ModeloIA.GEMINI] = api_key is not None
        except ImportError:
            disponibles[ModeloIA.GEMINI] = False
        
        return disponibles
    
    def obtener_modelo_optimo(self, tarea: TipoTarea, forzar_modelo: Optional[ModeloIA] = None) -> ModeloIA:
        """Obtiene el modelo óptimo para una tarea"""
        if forzar_modelo:
            return forzar_modelo
        
        # Obtener modelo recomendado
        modelo_recomendado = obtener_modelo_para_tarea(tarea)
        
        # Verificar disponibilidad
        if self.modelos_disponibles.get(modelo_recomendado, False):
            return modelo_recomendado
        
        # Si no está disponible, usar alternativo
        asignacion = ASIGNACION_MODELOS.get(tarea)
        if asignacion:
            modelo_alternativo = asignacion["modelo_secundario"]
            if self.modelos_disponibles.get(modelo_alternativo, False):
                self.estadisticas["cambios_modelo"] += 1
                return modelo_alternativo
        
        # Si ninguno está disponible, usar el primero disponible
        for modelo, disponible in self.modelos_disponibles.items():
            if disponible:
                return modelo
        
        # Si ninguno está disponible, retornar el recomendado (fallará pero al menos intentará)
        return modelo_recomendado
    
    def ejecutar_tarea(self, tarea: TipoTarea, funcion: Callable, *args, **kwargs) -> Any:
        """Ejecuta una tarea usando el modelo óptimo"""
        modelo = self.obtener_modelo_optimo(tarea)
        
        self.estadisticas["tareas_ejecutadas"] += 1
        self.estadisticas["por_modelo"][modelo.value] += 1
        
        try:
            # Ejecutar función con el modelo apropiado
            resultado = funcion(modelo, *args, **kwargs)
            return resultado
        except Exception as e:
            self.estadisticas["fallos"] += 1
            # Intentar con modelo alternativo
            asignacion = ASIGNACION_MODELOS.get(tarea)
            if asignacion:
                modelo_alternativo = asignacion["modelo_secundario"]
                if modelo_alternativo != modelo and self.modelos_disponibles.get(modelo_alternativo, False):
                    print(f"⚠️  Fallo con {modelo.value}, intentando con {modelo_alternativo.value}")
                    try:
                        resultado = funcion(modelo_alternativo, *args, **kwargs)
                        self.estadisticas["cambios_modelo"] += 1
                        return resultado
                    except Exception as e2:
                        pass
            
            raise e
    
    def get_estadisticas(self) -> Dict[str, Any]:
        """Retorna estadísticas de uso"""
        return {
            **self.estadisticas,
            "modelos_disponibles": {
                modelo.value: disponible 
                for modelo, disponible in self.modelos_disponibles.items()
            }
        }


# ============================================================================
# FUNCIONES ESPECÍFICAS POR MODELO
# ============================================================================

def ejecutar_revisar_inputs(modelo: ModeloIA, *args, **kwargs):
    """Revisa inputs usando el modelo especificado"""
    from agente_analisis_inteligente import AgenteAnalisisInteligente
    
    agente = AgenteAnalisisInteligente()
    return agente.revisar_inputs(*args, **kwargs)


def ejecutar_generar_presupuesto(modelo: ModeloIA, input_data: Dict):
    """Genera presupuesto usando el modelo especificado"""
    from agente_analisis_inteligente import AgenteAnalisisInteligente
    
    agente = AgenteAnalisisInteligente()
    
    if modelo == ModeloIA.OPENAI:
        # Usar motor directo (más preciso)
        return agente.generar_presupuesto(input_data)
    elif modelo == ModeloIA.CLAUDE:
        # Usar motor directo también (Claude para análisis después)
        return agente.generar_presupuesto(input_data)
    else:  # GEMINI
        # Usar motor directo
        return agente.generar_presupuesto(input_data)


def ejecutar_buscar_pdf(modelo: ModeloIA, input_data: Dict):
    """Busca PDF usando el modelo especificado"""
    from agente_analisis_inteligente import AgenteAnalisisInteligente
    
    agente = AgenteAnalisisInteligente()
    return agente.buscar_pdf_cotizacion(input_data)


def ejecutar_extraer_datos_pdf(modelo: ModeloIA, pdf_path: str):
    """Extrae datos de PDF usando el modelo especificado"""
    from agente_analisis_inteligente import AgenteAnalisisInteligente
    
    agente = AgenteAnalisisInteligente()
    
    if modelo == ModeloIA.OPENAI:
        # OpenAI puede usar Code Interpreter si está disponible
        return agente.extraer_datos_pdf(pdf_path)
    else:
        # Otros modelos usan extracción estándar
        return agente.extraer_datos_pdf(pdf_path)


def ejecutar_comparar_resultados(modelo: ModeloIA, presupuesto: Dict, pdf_real: Dict):
    """Compara resultados usando el modelo especificado"""
    from agente_analisis_inteligente import AgenteAnalisisInteligente
    
    agente = AgenteAnalisisInteligente()
    
    if modelo == ModeloIA.CLAUDE:
        # Claude es mejor para análisis comparativo
        # Usar función de comparación mejorada con Claude
        return agente.comparar_resultados(presupuesto, pdf_real)
    else:
        # Otros modelos usan comparación estándar
        return agente.comparar_resultados(presupuesto, pdf_real)


def ejecutar_analizar_diferencias(modelo: ModeloIA, comparacion: Dict):
    """Analiza diferencias usando el modelo especificado"""
    from agente_analisis_inteligente import AgenteAnalisisInteligente
    
    agente = AgenteAnalisisInteligente()
    
    if modelo == ModeloIA.CLAUDE:
        # Claude es mejor para análisis profundo
        analisis = comparacion.get('analisis', {})
        # Mejorar análisis con Claude si está disponible
        return agente._analizar_diferencias(
            comparacion.get('presupuesto', {}),
            comparacion.get('pdf_real', {}),
            comparacion.get('diferencia', 0),
            comparacion.get('diferencia_porcentaje', 0)
        )
    else:
        return comparacion.get('analisis', {})


def ejecutar_aprender_diferencias(modelo: ModeloIA, comparacion: Dict):
    """Aprende de diferencias usando el modelo especificado"""
    from agente_analisis_inteligente import AgenteAnalisisInteligente
    
    agente = AgenteAnalisisInteligente()
    
    if modelo == ModeloIA.CLAUDE:
        # Claude es mejor para aprendizaje
        return agente.aprender_de_diferencias(comparacion)
    else:
        return agente.aprender_de_diferencias(comparacion)


# ============================================================================
# MAPEO DE FUNCIONES
# ============================================================================

MAPEO_FUNCIONES = {
    TipoTarea.REVISAR_INPUTS: ejecutar_revisar_inputs,
    TipoTarea.GENERAR_PRESUPUESTO: ejecutar_generar_presupuesto,
    TipoTarea.BUSCAR_PDF: ejecutar_buscar_pdf,
    TipoTarea.EXTRAER_DATOS_PDF: ejecutar_extraer_datos_pdf,
    TipoTarea.COMPARAR_RESULTADOS: ejecutar_comparar_resultados,
    TipoTarea.ANALIZAR_DIFERENCIAS: ejecutar_analizar_diferencias,
    TipoTarea.APRENDER_DIFERENCIAS: ejecutar_aprender_diferencias,
}


# ============================================================================
# INTERFAZ SIMPLIFICADA
# ============================================================================

# Instancia singleton opcional para preservar estadísticas entre llamadas
# NOTA: Por defecto se crea una nueva instancia en cada llamada para asegurar aislamiento
# IMPORTANTE: El singleton puede causar acumulación de estado. Usar solo cuando sea necesario.
_orquestador_instance = None
_usar_singleton = False  # Flag para controlar si se usa singleton o instancia fresca
# Por defecto False para asegurar aislamiento completo entre llamadas


def resetear_orquestador():
    """Resetea la instancia singleton del orquestador"""
    global _orquestador_instance
    _orquestador_instance = None


def usar_singleton(usar: bool = True):
    """
    Configura si se debe usar una instancia singleton o crear una nueva en cada llamada.
    
    Args:
        usar: Si True, usa singleton (preserva estadísticas). Si False, crea instancia fresca (aislamiento).
    """
    global _usar_singleton, _orquestador_instance
    _usar_singleton = usar
    if not usar:
        # Si se desactiva el singleton, resetear la instancia existente
        _orquestador_instance = None


def ejecutar_procedimiento(tarea: TipoTarea, *args, usar_singleton_instancia: Optional[bool] = None, **kwargs) -> Any:
    """
    Ejecuta un procedimiento usando el modelo óptimo.
    
    Args:
        tarea: Tipo de tarea a ejecutar
        *args: Argumentos posicionales para la función de tarea
        usar_singleton_instancia: Si se proporciona, sobrescribe la configuración global para esta llamada.
                                 Si None, usa la configuración global (por defecto: False = instancia fresca).
        **kwargs: Argumentos con nombre para la función de tarea
    
    Returns:
        Resultado de la ejecución de la tarea
    
    Note:
        Por defecto, cada llamada crea una nueva instancia del orquestador para asegurar
        aislamiento completo. Si necesitas preservar estadísticas entre llamadas, usa
        usar_singleton(True) o pasar usar_singleton_instancia=True.
    """
    global _orquestador_instance, _usar_singleton
    
    # Determinar si usar singleton para esta llamada
    usar_singleton_esta_llamada = _usar_singleton if usar_singleton_instancia is None else usar_singleton_instancia
    
    if usar_singleton_esta_llamada:
        # Usar singleton (preserva estadísticas entre llamadas)
        if _orquestador_instance is None:
            _orquestador_instance = OrquestadorModelos()
        orquestador = _orquestador_instance
    else:
        # Crear instancia fresca (aislamiento completo entre llamadas)
        orquestador = OrquestadorModelos()
    
    funcion = MAPEO_FUNCIONES.get(tarea)
    
    if not funcion:
        raise ValueError(f"No hay función definida para la tarea: {tarea.value}")
    
    return orquestador.ejecutar_tarea(tarea, funcion, *args, **kwargs)


if __name__ == "__main__":
    from analisis_modelos_ia import TipoTarea
    
    print("=" * 70)
    print("🎯 ORQUESTADOR DE MODELOS IA")
    print("=" * 70)
    
    orquestador = OrquestadorModelos()
    
    print("\n📊 Modelos Disponibles:")
    for modelo, disponible in orquestador.modelos_disponibles.items():
        estado = "✅ Disponible" if disponible else "❌ No disponible"
        print(f"   {modelo.value.upper()}: {estado}")
    
    print("\n💡 Ejemplo de uso:")
    print("   from orquestador_modelos_ia import ejecutar_procedimiento, TipoTarea")
    print("   resultado = ejecutar_procedimiento(TipoTarea.REVISAR_INPUTS, cliente='Agustín')")
    
    print("\n📈 Estadísticas:")
    stats = orquestador.get_estadisticas()
    print(f"   Tareas ejecutadas: {stats['tareas_ejecutadas']}")
    print(f"   Por modelo: {stats['por_modelo']}")
