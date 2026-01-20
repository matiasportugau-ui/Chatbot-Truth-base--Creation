#!/usr/bin/env python3
"""
Agente Especialista en Build AI Apps (Google Labs Gems)
========================================================

Agente especializado en ayudar a crear y diseñar AI mini-apps y workflows
personalizados usando Google Labs Gems (Opal).

Capacidades:
- Diseñar workflows multi-paso
- Generar descripciones de Gems
- Crear estructuras de nodos para workflows
- Validar y optimizar workflows
- Proporcionar guías paso a paso
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class TipoWorkflow(Enum):
    """Tipos de workflows soportados"""
    AUTOMATION = "automation"  # Automatización multi-paso
    RESEARCH = "research"  # Investigación y análisis
    CONTENT = "content"  # Generación de contenido
    DATA_PROCESSING = "data_processing"  # Procesamiento de datos
    ANALYSIS = "analysis"  # Análisis y reportes
    CUSTOM = "custom"  # Workflow personalizado


class TipoNodo(Enum):
    """Tipos de nodos en un workflow"""
    INPUT = "input"  # Entrada de datos
    SEARCH = "search"  # Búsqueda web
    PROCESS = "process"  # Procesamiento con IA
    TRANSFORM = "transform"  # Transformación de datos
    GENERATE = "generate"  # Generación de contenido
    ANALYZE = "analyze"  # Análisis
    OUTPUT = "output"  # Salida final
    CONDITION = "condition"  # Condición/bifurcación
    LOOP = "loop"  # Iteración


class AgenteBuildAIApps:
    """Agente especialista en construir AI apps y workflows"""
    
    def __init__(self):
        self.workflows_guardados = []
        self.plantillas = self._cargar_plantillas()
        
    def _cargar_plantillas(self) -> Dict:
        """Carga plantillas predefinidas de workflows"""
        return {
            "recipe_genie": {
                "nombre": "Recipe Genie",
                "descripcion": "Crea recetas basadas en ingredientes disponibles",
                "tipo": TipoWorkflow.CONTENT.value,
                "pasos": [
                    {"tipo": "input", "descripcion": "Recibe lista de ingredientes"},
                    {"tipo": "search", "descripcion": "Busca recetas similares"},
                    {"tipo": "process", "descripcion": "Genera receta personalizada"},
                    {"tipo": "generate", "descripcion": "Crea instrucciones paso a paso"},
                    {"tipo": "output", "descripcion": "Presenta receta completa"}
                ]
            },
            "marketing_maven": {
                "nombre": "Marketing Maven",
                "descripcion": "Genera estrategias y contenido de marketing",
                "tipo": TipoWorkflow.CONTENT.value,
                "pasos": [
                    {"tipo": "input", "descripcion": "Recibe brief de marketing"},
                    {"tipo": "analyze", "descripcion": "Analiza audiencia y competencia"},
                    {"tipo": "generate", "descripcion": "Genera estrategias"},
                    {"tipo": "generate", "descripcion": "Crea contenido para múltiples canales"},
                    {"tipo": "output", "descripcion": "Presenta estrategia completa"}
                ]
            },
            "research_assistant": {
                "nombre": "Research Assistant",
                "descripcion": "Investiga un tema y genera reporte completo",
                "tipo": TipoWorkflow.RESEARCH.value,
                "pasos": [
                    {"tipo": "input", "descripcion": "Recibe tema de investigación"},
                    {"tipo": "search", "descripcion": "Busca información relevante"},
                    {"tipo": "process", "descripcion": "Sintetiza información"},
                    {"tipo": "analyze", "descripcion": "Analiza y extrae insights"},
                    {"tipo": "generate", "descripcion": "Genera reporte estructurado"},
                    {"tipo": "output", "descripcion": "Presenta reporte final"}
                ]
            }
        }
    
    # ========================================================================
    # DISEÑO DE WORKFLOWS
    # ========================================================================
    
    def diseñar_workflow(self, descripcion: str, tipo: Optional[str] = None) -> Dict:
        """
        Diseña un workflow completo basado en una descripción
        
        Args:
            descripcion: Descripción en lenguaje natural del workflow deseado
            tipo: Tipo de workflow (opcional, se infiere si no se proporciona)
        
        Returns:
            Dict con el diseño completo del workflow
        """
        print(f"🎨 Diseñando workflow: {descripcion[:50]}...")
        
        # Analizar descripción
        analisis = self._analizar_descripcion(descripcion)
        
        # Determinar tipo si no se proporciona
        if not tipo:
            tipo = self._inferir_tipo(descripcion)
        
        # Generar estructura de pasos
        pasos = self._generar_pasos(analisis, tipo)
        
        # Crear estructura de nodos
        nodos = self._crear_nodos(pasos)
        
        # Validar workflow
        validacion = self._validar_workflow(nodos)
        
        workflow = {
            "nombre": analisis.get("nombre", "Workflow Personalizado"),
            "descripcion": descripcion,
            "tipo": tipo,
            "analisis": analisis,
            "pasos": pasos,
            "nodos": nodos,
            "validacion": validacion,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        self.workflows_guardados.append(workflow)
        
        return workflow
    
    def _analizar_descripcion(self, descripcion: str) -> Dict:
        """Analiza la descripción para extraer componentes clave"""
        descripcion_lower = descripcion.lower()
        
        # Detectar acciones clave
        acciones = []
        if any(palabra in descripcion_lower for palabra in ["buscar", "investigar", "research"]):
            acciones.append("search")
        if any(palabra in descripcion_lower for palabra in ["generar", "crear", "escribir"]):
            acciones.append("generate")
        if any(palabra in descripcion_lower for palabra in ["analizar", "comparar", "evaluar"]):
            acciones.append("analyze")
        if any(palabra in descripcion_lower for palabra in ["resumir", "sintetizar"]):
            acciones.append("process")
        if any(palabra in descripcion_lower for palabra in ["traducir", "convertir"]):
            acciones.append("transform")
        
        # Detectar entradas
        entradas = []
        if "dirección" in descripcion_lower or "address" in descripcion_lower:
            entradas.append("direccion")
        if "ingredientes" in descripcion_lower or "ingredients" in descripcion_lower:
            entradas.append("ingredientes")
        if "tema" in descripcion_lower or "topic" in descripcion_lower:
            entradas.append("tema")
        if "texto" in descripcion_lower or "text" in descripcion_lower:
            entradas.append("texto")
        
        # Detectar salidas
        salidas = []
        if "receta" in descripcion_lower or "recipe" in descripcion_lower:
            salidas.append("receta")
        if "reporte" in descripcion_lower or "report" in descripcion_lower:
            salidas.append("reporte")
        if "descripción" in descripcion_lower or "description" in descripcion_lower:
            salidas.append("descripcion")
        if "post" in descripcion_lower or "caption" in descripcion_lower:
            salidas.append("contenido_social")
        
        # Extraer nombre sugerido
        palabras_clave = descripcion.split()[:3]
        nombre = " ".join(palabras_clave).title()
        
        return {
            "acciones": acciones,
            "entradas": entradas,
            "salidas": salidas,
            "nombre": nombre,
            "complejidad": "alta" if len(acciones) > 4 else "media" if len(acciones) > 2 else "baja"
        }
    
    def _inferir_tipo(self, descripcion: str) -> str:
        """Infiere el tipo de workflow basado en la descripción"""
        descripcion_lower = descripcion.lower()
        
        if any(palabra in descripcion_lower for palabra in ["investigar", "research", "buscar información"]):
            return TipoWorkflow.RESEARCH.value
        elif any(palabra in descripcion_lower for palabra in ["generar", "crear contenido", "escribir"]):
            return TipoWorkflow.CONTENT.value
        elif any(palabra in descripcion_lower for palabra in ["procesar datos", "analizar datos", "transformar"]):
            return TipoWorkflow.DATA_PROCESSING.value
        elif any(palabra in descripcion_lower for palabra in ["automatizar", "workflow", "proceso"]):
            return TipoWorkflow.AUTOMATION.value
        elif any(palabra in descripcion_lower for palabra in ["analizar", "reporte", "evaluar"]):
            return TipoWorkflow.ANALYSIS.value
        else:
            return TipoWorkflow.CUSTOM.value
    
    def _generar_pasos(self, analisis: Dict, tipo: str) -> List[Dict]:
        """Genera los pasos del workflow basado en el análisis"""
        pasos = []
        acciones = analisis.get("acciones", [])
        entradas = analisis.get("entradas", [])
        salidas = analisis.get("salidas", [])
        
        # Paso 1: Entrada
        if entradas:
            pasos.append({
                "orden": 1,
                "tipo": TipoNodo.INPUT.value,
                "nombre": f"Recibir {', '.join(entradas)}",
                "descripcion": f"Recibe como entrada: {', '.join(entradas)}",
                "configuracion": {
                    "campos": entradas
                }
            })
        
        # Pasos intermedios basados en acciones
        orden = 2
        for accion in acciones:
            if accion == "search":
                pasos.append({
                    "orden": orden,
                    "tipo": TipoNodo.SEARCH.value,
                    "nombre": "Búsqueda de información",
                    "descripcion": "Busca información relevante usando web search",
                    "configuracion": {
                        "query_template": "{{input.tema}}",
                        "max_results": 5
                    }
                })
                orden += 1
            elif accion == "process":
                pasos.append({
                    "orden": orden,
                    "tipo": TipoNodo.PROCESS.value,
                    "nombre": "Procesamiento con IA",
                    "descripcion": "Procesa y sintetiza la información",
                    "configuracion": {
                        "modelo": "gemini-pro",
                        "prompt_template": "Sintetiza la siguiente información: {{previous_output}}"
                    }
                })
                orden += 1
            elif accion == "analyze":
                pasos.append({
                    "orden": orden,
                    "tipo": TipoNodo.ANALYZE.value,
                    "nombre": "Análisis",
                    "descripcion": "Analiza la información y extrae insights",
                    "configuracion": {
                        "analisis_tipo": "completo",
                        "extraer": ["insights", "patrones", "conclusiones"]
                    }
                })
                orden += 1
            elif accion == "generate":
                pasos.append({
                    "orden": orden,
                    "tipo": TipoNodo.GENERATE.value,
                    "nombre": "Generación de contenido",
                    "descripcion": "Genera contenido basado en la información procesada",
                    "configuracion": {
                        "formato": salidas[0] if salidas else "texto",
                        "estilo": "profesional"
                    }
                })
                orden += 1
            elif accion == "transform":
                pasos.append({
                    "orden": orden,
                    "tipo": TipoNodo.TRANSFORM.value,
                    "nombre": "Transformación",
                    "descripcion": "Transforma el contenido al formato deseado",
                    "configuracion": {
                        "formato_origen": "texto",
                        "formato_destino": salidas[0] if salidas else "texto"
                    }
                })
                orden += 1
        
        # Paso final: Salida
        if salidas:
            pasos.append({
                "orden": orden,
                "tipo": TipoNodo.OUTPUT.value,
                "nombre": f"Generar {salidas[0]}",
                "descripcion": f"Presenta el resultado final: {salidas[0]}",
                "configuracion": {
                    "formato": salidas[0],
                    "presentacion": "estructurada"
                }
            })
        else:
            pasos.append({
                "orden": orden,
                "tipo": TipoNodo.OUTPUT.value,
                "nombre": "Resultado final",
                "descripcion": "Presenta el resultado del workflow",
                "configuracion": {
                    "formato": "texto"
                }
            })
        
        return pasos
    
    def _crear_nodos(self, pasos: List[Dict]) -> List[Dict]:
        """Crea la estructura de nodos para el workflow"""
        nodos = []
        
        for paso in pasos:
            nodo = {
                "id": f"nodo_{paso['orden']}",
                "tipo": paso["tipo"],
                "nombre": paso["nombre"],
                "descripcion": paso["descripcion"],
                "configuracion": paso.get("configuracion", {}),
                "conexiones": []
            }
            
            # Agregar conexión al siguiente nodo
            if paso["orden"] < len(pasos):
                nodo["conexiones"].append({
                    "target": f"nodo_{paso['orden'] + 1}",
                    "tipo": "secuencial"
                })
            
            nodos.append(nodo)
        
        return nodos
    
    def _validar_workflow(self, nodos: List[Dict]) -> Dict:
        """Valida que el workflow esté bien estructurado"""
        errores = []
        advertencias = []
        
        # Validar que tenga entrada
        tiene_input = any(nodo["tipo"] == TipoNodo.INPUT.value for nodo in nodos)
        if not tiene_input:
            errores.append("El workflow debe tener al menos un nodo de entrada")
        
        # Validar que tenga salida
        tiene_output = any(nodo["tipo"] == TipoNodo.OUTPUT.value for nodo in nodos)
        if not tiene_output:
            errores.append("El workflow debe tener al menos un nodo de salida")
        
        # Validar conexiones
        for nodo in nodos:
            if nodo["tipo"] != TipoNodo.OUTPUT.value and not nodo["conexiones"]:
                advertencias.append(f"El nodo {nodo['id']} no tiene conexiones de salida")
        
        # Validar que no haya ciclos (simplificado)
        ids_visitados = set()
        for nodo in nodos:
            for conexion in nodo["conexiones"]:
                if conexion["target"] in ids_visitados:
                    advertencias.append(f"Posible ciclo detectado en {nodo['id']}")
                ids_visitados.add(conexion["target"])
        
        return {
            "valido": len(errores) == 0,
            "errores": errores,
            "advertencias": advertencias,
            "total_nodos": len(nodos),
            "complejidad": "alta" if len(nodos) > 6 else "media" if len(nodos) > 3 else "baja"
        }
    
    # ========================================================================
    # GENERACIÓN DE DESCRIPCIONES PARA GEMS
    # ========================================================================
    
    def generar_descripcion_gem(self, workflow: Dict) -> str:
        """
        Genera una descripción optimizada para crear un Gem en Google Labs
        
        Args:
            workflow: Diccionario con el diseño del workflow
        
        Returns:
            Descripción lista para usar en Google Labs
        """
        nombre = workflow.get("nombre", "Workflow")
        pasos = workflow.get("pasos", [])
        
        descripcion = f"Crea un app que {workflow.get('descripcion', 'ejecuta un workflow personalizado')}.\n\n"
        descripcion += "El workflow debe:\n"
        
        for paso in pasos:
            descripcion += f"- {paso['descripcion']}\n"
        
        # Agregar instrucciones adicionales
        descripcion += "\nEl app debe presentar el resultado final de forma clara y estructurada."
        
        return descripcion
    
    def generar_instrucciones_paso_a_paso(self, workflow: Dict) -> List[str]:
        """Genera instrucciones paso a paso para crear el Gem"""
        instrucciones = [
            "1. Accede a gemini.google.com y haz clic en 'Gems' en la barra lateral",
            "2. Haz clic en 'New Gem' en la sección 'My Gems from Labs'",
            "3. Si es tu primera vez, acepta unirte al experimento Opal",
            f"4. En el cuadro de texto, pega la siguiente descripción:",
            "",
            self.generar_descripcion_gem(workflow),
            "",
            "5. Espera a que Gemini genere el workflow (puede tomar unos minutos)",
            "6. Revisa los pasos generados en el editor visual",
            "7. Haz clic en 'Start app' para probar el workflow",
            "8. Si necesitas ajustes, usa comandos conversacionales o edita los nodos manualmente",
            "9. Guarda el Gem cuando esté listo"
        ]
        
        return instrucciones
    
    # ========================================================================
    # OPTIMIZACIÓN Y MEJORA
    # ========================================================================
    
    def optimizar_workflow(self, workflow: Dict) -> Dict:
        """Optimiza un workflow existente"""
        print("⚡ Optimizando workflow...")
        
        nodos = workflow.get("nodos", [])
        optimizaciones = []
        
        # Detectar nodos redundantes
        tipos_nodos = [nodo["tipo"] for nodo in nodos]
        if tipos_nodos.count(TipoNodo.PROCESS.value) > 2:
            optimizaciones.append({
                "tipo": "redundancia",
                "descripcion": "Múltiples nodos de procesamiento detectados, considerar consolidar",
                "accion": "Combinar nodos de procesamiento similares"
            })
        
        # Detectar secuencias innecesarias
        for i in range(len(nodos) - 1):
            if nodos[i]["tipo"] == TipoNodo.TRANSFORM.value and nodos[i+1]["tipo"] == TipoNodo.TRANSFORM.value:
                optimizaciones.append({
                    "tipo": "secuencia",
                    "descripcion": f"Secuencia de transformaciones en {nodos[i]['id']} y {nodos[i+1]['id']}",
                    "accion": "Considerar combinar transformaciones en un solo paso"
                })
        
        # Sugerir mejoras
        if len(nodos) > 8:
            optimizaciones.append({
                "tipo": "complejidad",
                "descripcion": "Workflow muy complejo",
                "accion": "Considerar dividir en sub-workflows más pequeños"
            })
        
        workflow["optimizaciones"] = optimizaciones
        workflow["optimizado"] = len(optimizaciones) == 0
        
        return workflow
    
    def remix_workflow(self, workflow_base: Dict, modificaciones: str) -> Dict:
        """
        Crea una versión remix de un workflow con modificaciones
        
        Args:
            workflow_base: Workflow base a remixear
            modificaciones: Descripción de las modificaciones deseadas
        
        Returns:
            Nuevo workflow remixado
        """
        print(f"🔄 Remixeando workflow: {modificaciones[:50]}...")
        
        # Analizar modificaciones
        modificaciones_lower = modificaciones.lower()
        
        nuevo_workflow = workflow_base.copy()
        pasos = nuevo_workflow.get("pasos", [])
        
        # Agregar paso de traducción
        if "traducir" in modificaciones_lower or "translate" in modificaciones_lower:
            nuevo_paso = {
                "orden": len(pasos),
                "tipo": TipoNodo.TRANSFORM.value,
                "nombre": "Traducir resultado",
                "descripcion": "Traduce el resultado al idioma especificado",
                "configuracion": {
                    "idioma_destino": "español" if "español" in modificaciones_lower else "inglés"
                }
            }
            pasos.insert(-1, nuevo_paso)  # Insertar antes del output
        
        # Agregar paso de análisis adicional
        if "analizar más" in modificaciones_lower or "análisis adicional" in modificaciones_lower:
            nuevo_paso = {
                "orden": len(pasos),
                "tipo": TipoNodo.ANALYZE.value,
                "nombre": "Análisis adicional",
                "descripcion": "Realiza un análisis más profundo",
                "configuracion": {
                    "profundidad": "alta"
                }
            }
            pasos.insert(-1, nuevo_paso)
        
        # Recrear nodos con los nuevos pasos
        nuevo_workflow["pasos"] = pasos
        nuevo_workflow["nodos"] = self._crear_nodos(pasos)
        nuevo_workflow["validacion"] = self._validar_workflow(nuevo_workflow["nodos"])
        nuevo_workflow["timestamp"] = datetime.now().isoformat()
        nuevo_workflow["version"] = "2.0"
        nuevo_workflow["remix_de"] = workflow_base.get("nombre", "Unknown")
        
        return nuevo_workflow
    
    # ========================================================================
    # PLANTILLAS Y EJEMPLOS
    # ========================================================================
    
    def listar_plantillas(self) -> List[Dict]:
        """Lista todas las plantillas disponibles"""
        return [
            {
                "id": key,
                "nombre": value["nombre"],
                "descripcion": value["descripcion"],
                "tipo": value["tipo"],
                "total_pasos": len(value["pasos"])
            }
            for key, value in self.plantillas.items()
        ]
    
    def usar_plantilla(self, id_plantilla: str, personalizaciones: Optional[Dict] = None) -> Dict:
        """
        Crea un workflow basado en una plantilla
        
        Args:
            id_plantilla: ID de la plantilla a usar
            personalizaciones: Diccionario con personalizaciones opcionales
        
        Returns:
            Workflow basado en la plantilla
        """
        if id_plantilla not in self.plantillas:
            raise ValueError(f"Plantilla '{id_plantilla}' no encontrada")
        
        plantilla = self.plantillas[id_plantilla]
        
        workflow = {
            "nombre": plantilla["nombre"],
            "descripcion": plantilla["descripcion"],
            "tipo": plantilla["tipo"],
            "pasos": plantilla["pasos"].copy(),
            "timestamp": datetime.now().isoformat(),
            "version": "1.0",
            "basado_en_plantilla": id_plantilla
        }
        
        # Aplicar personalizaciones
        if personalizaciones:
            if "nombre" in personalizaciones:
                workflow["nombre"] = personalizaciones["nombre"]
            if "agregar_paso" in personalizaciones:
                workflow["pasos"].extend(personalizaciones["agregar_paso"])
        
        # Crear nodos
        workflow["nodos"] = self._crear_nodos(workflow["pasos"])
        workflow["validacion"] = self._validar_workflow(workflow["nodos"])
        
        return workflow
    
    # ========================================================================
    # EXPORTACIÓN Y GUARDADO
    # ========================================================================
    
    def exportar_workflow(self, workflow: Dict, formato: str = "json") -> str:
        """
        Exporta un workflow en diferentes formatos
        
        Args:
            workflow: Workflow a exportar
            formato: Formato de exportación ('json', 'markdown', 'gem_description')
        
        Returns:
            Contenido exportado como string
        """
        if formato == "json":
            return json.dumps(workflow, indent=2, ensure_ascii=False)
        
        elif formato == "markdown":
            md = f"# {workflow.get('nombre', 'Workflow')}\n\n"
            md += f"**Descripción:** {workflow.get('descripcion', 'N/A')}\n\n"
            md += f"**Tipo:** {workflow.get('tipo', 'N/A')}\n\n"
            md += "## Pasos del Workflow\n\n"
            
            for paso in workflow.get("pasos", []):
                md += f"### {paso['orden']}. {paso['nombre']}\n"
                md += f"{paso['descripcion']}\n\n"
            
            md += "## Nodos\n\n"
            for nodo in workflow.get("nodos", []):
                md += f"- **{nodo['id']}**: {nodo['nombre']} ({nodo['tipo']})\n"
            
            return md
        
        elif formato == "gem_description":
            return self.generar_descripcion_gem(workflow)
        
        else:
            raise ValueError(f"Formato '{formato}' no soportado")
    
    def guardar_workflow(self, workflow: Dict, nombre_archivo: Optional[str] = None) -> str:
        """Guarda un workflow en un archivo JSON"""
        if not nombre_archivo:
            nombre_safe = workflow.get("nombre", "workflow").lower().replace(" ", "_")
            nombre_archivo = f"{nombre_safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        ruta = Path(__file__).parent / "workflows" / nombre_archivo
        ruta.parent.mkdir(exist_ok=True)
        
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        
        return str(ruta)


# ============================================================================
# FUNCIONES PARA AGENTES DE IA (Function Calling)
# ============================================================================

def get_build_ai_apps_function_schema() -> Dict:
    """Retorna el schema de función para agentes de IA"""
    return {
        "name": "diseñar_ai_app",
        "description": "Diseña un AI app (Gem) completo para Google Labs. Analiza la descripción del usuario, genera la estructura de workflow con pasos y nodos, valida el diseño, y proporciona instrucciones para crearlo en Google Labs. Soporta múltiples tipos de workflows: automatización, investigación, generación de contenido, procesamiento de datos, y análisis.",
        "parameters": {
            "type": "object",
            "properties": {
                "descripcion": {
                    "type": "string",
                    "description": "Descripción en lenguaje natural del AI app que se desea crear (ej: 'Crea un app que tome una dirección de bienes raíces, investigue el vecindario, escriba una descripción de listado, y genere tres captions para Instagram')"
                },
                "tipo": {
                    "type": "string",
                    "enum": ["automation", "research", "content", "data_processing", "analysis", "custom"],
                    "description": "Tipo de workflow (opcional, se infiere automáticamente si no se proporciona)"
                },
                "optimizar": {
                    "type": "boolean",
                    "description": "Si se debe optimizar el workflow después de diseñarlo",
                    "default": True
                },
                "exportar_formato": {
                    "type": "string",
                    "enum": ["json", "markdown", "gem_description"],
                    "description": "Formato para exportar el resultado",
                    "default": "json"
                }
            },
            "required": ["descripcion"]
        }
    }


def diseñar_ai_app(
    descripcion: str,
    tipo: Optional[str] = None,
    optimizar: bool = True,
    exportar_formato: str = "json"
) -> Dict[str, Any]:
    """
    Diseña un AI app completo - Función para agentes de IA
    
    Args:
        descripcion: Descripción del AI app a crear
        tipo: Tipo de workflow (opcional)
        optimizar: Si se debe optimizar el workflow
        exportar_formato: Formato de exportación
    
    Returns:
        Dict con el diseño completo del AI app
    """
    agente = AgenteBuildAIApps()
    
    # Diseñar workflow
    workflow = agente.diseñar_workflow(descripcion, tipo)
    
    # Optimizar si se solicita
    if optimizar:
        workflow = agente.optimizar_workflow(workflow)
    
    # Generar descripción para Gem
    descripcion_gem = agente.generar_descripcion_gem(workflow)
    
    # Generar instrucciones
    instrucciones = agente.generar_instrucciones_paso_a_paso(workflow)
    
    # Exportar en formato solicitado
    contenido_exportado = agente.exportar_workflow(workflow, exportar_formato)
    
    return {
        "workflow": workflow,
        "descripcion_gem": descripcion_gem,
        "instrucciones": instrucciones,
        "exportado": contenido_exportado,
        "formato_exportado": exportar_formato,
        "valido": workflow.get("validacion", {}).get("valido", False)
    }


def get_listar_plantillas_function_schema() -> Dict:
    """Schema para listar plantillas disponibles"""
    return {
        "name": "listar_plantillas_ai_apps",
        "description": "Lista todas las plantillas disponibles de AI apps que se pueden usar como punto de partida",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }


def listar_plantillas_ai_apps() -> Dict[str, Any]:
    """Lista plantillas disponibles - Función para agentes de IA"""
    agente = AgenteBuildAIApps()
    plantillas = agente.listar_plantillas()
    
    return {
        "plantillas": plantillas,
        "total": len(plantillas),
        "descripcion": "Plantillas predefinidas que puedes usar como punto de partida para crear tus propios AI apps"
    }


def get_usar_plantilla_function_schema() -> Dict:
    """Schema para usar una plantilla"""
    return {
        "name": "usar_plantilla_ai_app",
        "description": "Crea un AI app basado en una plantilla predefinida. Útil para empezar rápidamente con un workflow conocido.",
        "parameters": {
            "type": "object",
            "properties": {
                "id_plantilla": {
                    "type": "string",
                    "enum": ["recipe_genie", "marketing_maven", "research_assistant"],
                    "description": "ID de la plantilla a usar"
                },
                "personalizar_nombre": {
                    "type": "string",
                    "description": "Nombre personalizado para el workflow (opcional)"
                }
            },
            "required": ["id_plantilla"]
        }
    }


def usar_plantilla_ai_app(id_plantilla: str, personalizar_nombre: Optional[str] = None) -> Dict[str, Any]:
    """Usa una plantilla para crear un AI app - Función para agentes de IA"""
    agente = AgenteBuildAIApps()
    
    personalizaciones = {}
    if personalizar_nombre:
        personalizaciones["nombre"] = personalizar_nombre
    
    workflow = agente.usar_plantilla(id_plantilla, personalizaciones if personalizaciones else None)
    descripcion_gem = agente.generar_descripcion_gem(workflow)
    instrucciones = agente.generar_instrucciones_paso_a_paso(workflow)
    
    return {
        "workflow": workflow,
        "descripcion_gem": descripcion_gem,
        "instrucciones": instrucciones,
        "valido": workflow.get("validacion", {}).get("valido", False)
    }


if __name__ == "__main__":
    # Ejemplo de uso
    print("=" * 70)
    print("🤖 AGENTE ESPECIALISTA EN BUILD AI APPS")
    print("=" * 70)
    
    agente = AgenteBuildAIApps()
    
    # Ejemplo 1: Diseñar workflow desde cero
    print("\n📝 Ejemplo 1: Diseñar workflow personalizado")
    print("-" * 70)
    
    descripcion = "Crea un app que tome una dirección de bienes raíces, investigue el vecindario, escriba una descripción de listado, y genere tres captions para Instagram"
    
    resultado = diseñar_ai_app(descripcion, optimizar=True)
    
    print(f"\n✅ Workflow diseñado: {resultado['workflow']['nombre']}")
    print(f"📊 Total de pasos: {len(resultado['workflow']['pasos'])}")
    print(f"✅ Válido: {resultado['valido']}")
    
    print("\n📋 Descripción para Google Labs:")
    print(resultado['descripcion_gem'])
    
    # Ejemplo 2: Usar plantilla
    print("\n\n📝 Ejemplo 2: Usar plantilla")
    print("-" * 70)
    
    plantillas = listar_plantillas_ai_apps()
    print(f"\n📚 Plantillas disponibles: {plantillas['total']}")
    for plantilla in plantillas['plantillas']:
        print(f"  - {plantilla['id']}: {plantilla['nombre']}")
    
    if plantillas['plantillas']:
        resultado_plantilla = usar_plantilla_ai_app("research_assistant", "Mi Asistente de Investigación")
        print(f"\n✅ Workflow creado desde plantilla: {resultado_plantilla['workflow']['nombre']}")
    
    # Guardar ejemplo
    print("\n\n💾 Guardando workflow de ejemplo...")
    ruta = agente.guardar_workflow(resultado['workflow'])
    print(f"✅ Guardado en: {ruta}")
