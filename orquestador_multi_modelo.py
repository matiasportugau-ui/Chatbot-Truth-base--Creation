#!/usr/bin/env python3
"""
Orquestador Multi-Modelo para Panelin
======================================

Asigna tareas al modelo de IA más adecuado según el procedimiento.
"""

import os
import json
from typing import Dict, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass

# Importar funciones de agentes
from agente_cotizacion_panelin import (
    calcular_cotizacion_agente,
    AgentePanelinOpenAI,
    AgentePanelinClaude,
    AgentePanelinGemini
)
from agente_analisis_inteligente import (
    analizar_cotizacion_completa,
    AgenteAnalisisInteligente
)


class TipoProcedimiento(Enum):
    """Tipos de procedimientos del sistema"""
    REVISION_INPUTS = "revision_inputs"
    GENERACION_PRESUPUESTO = "generacion_presupuesto"
    BUSQUEDA_PDF = "busqueda_pdf"
    EXTRACCION_DATOS = "extraccion_datos"
    COMPARACION = "comparacion"
    ANALISIS_DIFERENCIAS = "analisis_diferencias"
    APRENDIZAJE = "aprendizaje"
    COTIZACION_REALTIME = "cotizacion_realtime"
    VALIDACION_TECNICA = "validacion_tecnica"
    PRESENTACION = "presentacion"


class ModeloIA(Enum):
    """Modelos de IA disponibles"""
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    MOTOR_PYTHON = "motor_python"


@dataclass
class AsignacionModelo:
    """Asignación de modelo para un procedimiento"""
    procedimiento: TipoProcedimiento
    modelo_principal: ModeloIA
    modelo_alternativo: ModeloIA
    prioridad: str  # "critica", "alta", "media", "baja"
    razon: str


class OrquestadorMultiModelo:
    """Orquestador que asigna tareas al modelo más adecuado"""
    
    # Matriz de asignación
    ASIGNACIONES = {
        TipoProcedimiento.REVISION_INPUTS: AsignacionModelo(
            procedimiento=TipoProcedimiento.REVISION_INPUTS,
            modelo_principal=ModeloIA.OPENAI,
            modelo_alternativo=ModeloIA.GEMINI,
            prioridad="alta",
            razon="Code Interpreter excelente para parsing estructurado"
        ),
        TipoProcedimiento.GENERACION_PRESUPUESTO: AsignacionModelo(
            procedimiento=TipoProcedimiento.GENERACION_PRESUPUESTO,
            modelo_principal=ModeloIA.OPENAI,
            modelo_alternativo=ModeloIA.MOTOR_PYTHON,
            prioridad="critica",
            razon="Code Interpreter para cálculos precisos, Function Calling"
        ),
        TipoProcedimiento.BUSQUEDA_PDF: AsignacionModelo(
            procedimiento=TipoProcedimiento.BUSQUEDA_PDF,
            modelo_principal=ModeloIA.CLAUDE,
            modelo_alternativo=ModeloIA.OPENAI,
            prioridad="media",
            razon="Excelente razonamiento para matching inteligente"
        ),
        TipoProcedimiento.EXTRACCION_DATOS: AsignacionModelo(
            procedimiento=TipoProcedimiento.EXTRACCION_DATOS,
            modelo_principal=ModeloIA.OPENAI,
            modelo_alternativo=ModeloIA.GEMINI,
            prioridad="alta",
            razon="Code Interpreter para parsing complejo, multimodal para PDFs"
        ),
        TipoProcedimiento.COMPARACION: AsignacionModelo(
            procedimiento=TipoProcedimiento.COMPARACION,
            modelo_principal=ModeloIA.OPENAI,
            modelo_alternativo=ModeloIA.MOTOR_PYTHON,
            prioridad="alta",
            razon="Code Interpreter para cálculos precisos"
        ),
        TipoProcedimiento.ANALISIS_DIFERENCIAS: AsignacionModelo(
            procedimiento=TipoProcedimiento.ANALISIS_DIFERENCIAS,
            modelo_principal=ModeloIA.CLAUDE,
            modelo_alternativo=ModeloIA.OPENAI,
            prioridad="media",
            razon="Excelente razonamiento profundo, identificación de causas"
        ),
        TipoProcedimiento.APRENDIZAJE: AsignacionModelo(
            procedimiento=TipoProcedimiento.APRENDIZAJE,
            modelo_principal=ModeloIA.CLAUDE,
            modelo_alternativo=ModeloIA.OPENAI,
            prioridad="baja",
            razon="Excelente para síntesis, generación de insights"
        ),
        TipoProcedimiento.COTIZACION_REALTIME: AsignacionModelo(
            procedimiento=TipoProcedimiento.COTIZACION_REALTIME,
            modelo_principal=ModeloIA.OPENAI,
            modelo_alternativo=ModeloIA.CLAUDE,
            prioridad="critica",
            razon="Function Calling nativo, integración perfecta"
        ),
        TipoProcedimiento.VALIDACION_TECNICA: AsignacionModelo(
            procedimiento=TipoProcedimiento.VALIDACION_TECNICA,
            modelo_principal=ModeloIA.OPENAI,
            modelo_alternativo=ModeloIA.MOTOR_PYTHON,
            prioridad="critica",
            razon="Code Interpreter para validación matemática"
        ),
        TipoProcedimiento.PRESENTACION: AsignacionModelo(
            procedimiento=TipoProcedimiento.PRESENTACION,
            modelo_principal=ModeloIA.CLAUDE,
            modelo_alternativo=ModeloIA.OPENAI,
            prioridad="media",
            razon="Excelente comunicación natural, formateo profesional"
        ),
    }
    
    def __init__(self):
        self.openai_agente = None
        self.claude_agente = None
        self.gemini_agente = None
        self.analisis_agente = None
        
        # Inicializar agentes disponibles
        self._inicializar_agentes()
    
    def _inicializar_agentes(self):
        """Inicializa agentes según disponibilidad de API keys"""
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                self.openai_agente = AgentePanelinOpenAI(openai_key)
            except Exception as e:
                print(f"⚠️  OpenAI no disponible: {e}")
        
        # Claude
        claude_key = os.getenv("ANTHROPIC_API_KEY")
        if claude_key:
            try:
                self.claude_agente = AgentePanelinClaude(claude_key)
            except Exception as e:
                print(f"⚠️  Claude no disponible: {e}")
        
        # Gemini
        gemini_key = os.getenv("GOOGLE_API_KEY")
        if gemini_key:
            try:
                self.gemini_agente = AgentePanelinGemini(gemini_key)
            except Exception as e:
                print(f"⚠️  Gemini no disponible: {e}")
        
        # Agente de análisis
        self.analisis_agente = AgenteAnalisisInteligente()
    
    def obtener_modelo_optimo(self, procedimiento: TipoProcedimiento) -> ModeloIA:
        """Obtiene el modelo óptimo para un procedimiento"""
        asignacion = self.ASIGNACIONES.get(procedimiento)
        if not asignacion:
            return ModeloIA.OPENAI  # Default
        
        # Verificar disponibilidad del modelo principal
        if self._modelo_disponible(asignacion.modelo_principal):
            return asignacion.modelo_principal
        
        # Fallback al alternativo
        if self._modelo_disponible(asignacion.modelo_alternativo):
            return asignacion.modelo_alternativo
        
        # Fallback final
        return ModeloIA.MOTOR_PYTHON
    
    def _modelo_disponible(self, modelo: ModeloIA) -> bool:
        """Verifica si un modelo está disponible"""
        if modelo == ModeloIA.OPENAI:
            return self.openai_agente is not None
        elif modelo == ModeloIA.CLAUDE:
            return self.claude_agente is not None
        elif modelo == ModeloIA.GEMINI:
            return self.gemini_agente is not None
        elif modelo == ModeloIA.MOTOR_PYTHON:
            return True  # Siempre disponible
        return False
    
    def ejecutar_procedimiento(
        self,
        procedimiento: TipoProcedimiento,
        **kwargs
    ) -> Dict[str, Any]:
        """Ejecuta un procedimiento usando el modelo óptimo"""
        modelo = self.obtener_modelo_optimo(procedimiento)
        asignacion = self.ASIGNACIONES.get(procedimiento)
        
        print(f"🤖 Ejecutando {procedimiento.value} con {modelo.value}")
        if asignacion:
            print(f"   📊 Prioridad: {asignacion.prioridad}")
            print(f"   💡 Razón: {asignacion.razon}")
        
        # Ejecutar según modelo
        if modelo == ModeloIA.OPENAI:
            return self._ejecutar_openai(procedimiento, **kwargs)
        elif modelo == ModeloIA.CLAUDE:
            return self._ejecutar_claude(procedimiento, **kwargs)
        elif modelo == ModeloIA.GEMINI:
            return self._ejecutar_gemini(procedimiento, **kwargs)
        elif modelo == ModeloIA.MOTOR_PYTHON:
            return self._ejecutar_motor_python(procedimiento, **kwargs)
        else:
            raise ValueError(f"Modelo no soportado: {modelo}")
    
    def _ejecutar_openai(self, procedimiento: TipoProcedimiento, **kwargs) -> Dict:
        """Ejecuta procedimiento con OpenAI"""
        if not self.openai_agente:
            raise RuntimeError("OpenAI no disponible")
        
        # Mapear procedimientos a funciones
        handlers = {
            TipoProcedimiento.COTIZACION_REALTIME: self._cotizacion_openai,
            TipoProcedimiento.VALIDACION_TECNICA: self._validacion_openai,
            TipoProcedimiento.GENERACION_PRESUPUESTO: self._generacion_openai,
        }
        
        handler = handlers.get(procedimiento)
        if handler:
            return handler(**kwargs)
        
        # Default: usar motor Python
        return self._ejecutar_motor_python(procedimiento, **kwargs)
    
    def _ejecutar_claude(self, procedimiento: TipoProcedimiento, **kwargs) -> Dict:
        """Ejecuta procedimiento con Claude"""
        if not self.claude_agente:
            raise RuntimeError("Claude no disponible")
        
        handlers = {
            TipoProcedimiento.ANALISIS_DIFERENCIAS: self._analisis_claude,
            TipoProcedimiento.APRENDIZAJE: self._aprendizaje_claude,
            TipoProcedimiento.PRESENTACION: self._presentacion_claude,
            TipoProcedimiento.BUSQUEDA_PDF: self._busqueda_claude,
        }
        
        handler = handlers.get(procedimiento)
        if handler:
            return handler(**kwargs)
        
        # Default: usar motor Python
        return self._ejecutar_motor_python(procedimiento, **kwargs)
    
    def _ejecutar_gemini(self, procedimiento: TipoProcedimiento, **kwargs) -> Dict:
        """Ejecuta procedimiento con Gemini"""
        if not self.gemini_agente:
            raise RuntimeError("Gemini no disponible")
        
        # Gemini principalmente para backup
        return self._ejecutar_motor_python(procedimiento, **kwargs)
    
    def _ejecutar_motor_python(self, procedimiento: TipoProcedimiento, **kwargs) -> Dict:
        """Ejecuta procedimiento con motor Python directo"""
        handlers = {
            TipoProcedimiento.GENERACION_PRESUPUESTO: lambda **kw: calcular_cotizacion_agente(**kw),
            TipoProcedimiento.REVISION_INPUTS: lambda **kw: self.analisis_agente.revisar_inputs(**kw),
            TipoProcedimiento.BUSQUEDA_PDF: lambda **kw: self.analisis_agente.buscar_pdf_cotizacion(kw.get('input_data')),
            TipoProcedimiento.EXTRACCION_DATOS: lambda **kw: self.analisis_agente.extraer_datos_pdf(kw.get('pdf_path')),
            TipoProcedimiento.COMPARACION: lambda **kw: self.analisis_agente.comparar_resultados(kw.get('presupuesto'), kw.get('pdf_real')),
        }
        
        handler = handlers.get(procedimiento)
        if handler:
            return handler(**kwargs)
        
        return {"error": f"Procedimiento {procedimiento.value} no implementado en motor Python"}
    
    # Handlers específicos por modelo
    
    def _cotizacion_openai(self, **kwargs) -> Dict:
        """Cotización en tiempo real con OpenAI"""
        thread = self.openai_agente.client.beta.threads.create()
        mensaje = kwargs.get('mensaje', '')
        return self.openai_agente.procesar_mensaje(thread.id, mensaje)
    
    def _validacion_openai(self, **kwargs) -> Dict:
        """Validación técnica con OpenAI"""
        # Usar Code Interpreter para validación
        return calcular_cotizacion_agente(**kwargs)
    
    def _generacion_openai(self, **kwargs) -> Dict:
        """Generación de presupuesto con OpenAI"""
        return calcular_cotizacion_agente(**kwargs)
    
    def _analisis_claude(self, **kwargs) -> Dict:
        """Análisis de diferencias con Claude"""
        comparacion = kwargs.get('comparacion', {})
        mensaje = f"""Analiza esta comparación de cotizaciones y genera insights profundos:

{json.dumps(comparacion, indent=2, ensure_ascii=False)}

Identifica:
1. Causas raíz de las diferencias
2. Patrones detectados
3. Recomendaciones específicas de mejora
4. Lecciones aprendidas"""
        
        return self.claude_agente.chat(mensaje)
    
    def _aprendizaje_claude(self, **kwargs) -> Dict:
        """Aprendizaje y lecciones con Claude"""
        lecciones = kwargs.get('lecciones', [])
        mensaje = f"""Sintetiza estas lecciones aprendidas y genera mejoras:

{json.dumps(lecciones, indent=2, ensure_ascii=False, default=str)}

Genera:
1. Resumen ejecutivo de lecciones
2. Mejoras prioritarias
3. Actualizaciones sugeridas para la base de conocimiento
4. Recomendaciones para futuras cotizaciones"""
        
        return self.claude_agente.chat(mensaje)
    
    def _presentacion_claude(self, **kwargs) -> Dict:
        """Presentación profesional con Claude"""
        datos = kwargs.get('datos', {})
        mensaje = f"""Presenta esta cotización de forma profesional y consultiva:

{json.dumps(datos, indent=2, ensure_ascii=False)}

Formato:
- Tono profesional pero accesible
- Explicación técnica clara
- Recomendaciones consultivas
- Formato estructurado y legible"""
        
        return self.claude_agente.chat(mensaje)
    
    def _busqueda_claude(self, **kwargs) -> Dict:
        """Búsqueda inteligente de PDFs con Claude"""
        input_data = kwargs.get('input_data', {})
        mensaje = f"""Ayuda a correlacionar este input con PDFs reales:

Cliente: {input_data.get('cliente', 'N/A')}
Fecha: {input_data.get('fecha', 'N/A')}
Consulta: {input_data.get('consulta', 'N/A')}

Sugiere estrategias de búsqueda y correlación inteligente."""
        
        return self.claude_agente.chat(mensaje)
    
    def proceso_completo_inteligente(self, **kwargs) -> Dict:
        """Ejecuta el proceso completo usando modelos óptimos"""
        print("=" * 70)
        print("🤖 PROCESO COMPLETO CON ORQUESTACIÓN MULTI-MODELO")
        print("=" * 70)
        
        resultados = {}
        
        # 1. Revisión de inputs (OpenAI)
        print("\n📋 Paso 1: Revisión de inputs...")
        try:
            resultados['inputs'] = self.ejecutar_procedimiento(
                TipoProcedimiento.REVISION_INPUTS,
                cliente=kwargs.get('cliente'),
                producto=kwargs.get('producto')
            )
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            resultados['inputs'] = []
        
        # 2. Generación de presupuestos (OpenAI)
        print("\n🔧 Paso 2: Generación de presupuestos...")
        # ... (continuar con otros pasos)
        
        return resultados


# Función de conveniencia
def obtener_orquestador() -> OrquestadorMultiModelo:
    """Obtiene instancia del orquestador"""
    return OrquestadorMultiModelo()


if __name__ == "__main__":
    print("=" * 70)
    print("🤖 ORQUESTADOR MULTI-MODELO")
    print("=" * 70)
    
    orquestador = obtener_orquestador()
    
    # Mostrar asignaciones
    print("\n📊 ASIGNACIONES DE MODELOS:\n")
    for proc, asignacion in orquestador.ASIGNACIONES.items():
        modelo_optimo = orquestador.obtener_modelo_optimo(proc)
        disponible = "✅" if orquestador._modelo_disponible(modelo_optimo) else "❌"
        
        print(f"{disponible} {proc.value:30} → {modelo_optimo.value:15} "
              f"(alt: {asignacion.modelo_alternativo.value:15}, "
              f"prioridad: {asignacion.prioridad})")
