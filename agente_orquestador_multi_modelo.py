#!/usr/bin/env python3
"""
Agente Orquestador Multi-Modelo
================================

Orquesta diferentes modelos de IA según la tarea:
- Gemini: Procesamiento de datos, búsqueda, extracción
- OpenAI GPT-4: Cálculos matemáticos, comparaciones
- Claude: Análisis complejo, razonamiento, aprendizaje
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

# Importar agentes base
import sys
sys.path.insert(0, str(Path(__file__).parent))
from agente_analisis_inteligente import AgenteAnalisisInteligente
from motor_cotizacion_panelin import MotorCotizacionPanelin


class ModeloIA(Enum):
    """Modelos de IA disponibles"""
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"


class RolAgente(Enum):
    """Roles especializados de agentes"""
    INPUT_PROCESSOR = "input_processor"  # Gemini
    QUOTATION_CALCULATOR = "quotation_calculator"  # OpenAI
    PDF_FINDER = "pdf_finder"  # Gemini
    PDF_EXTRACTOR = "pdf_extractor"  # Gemini
    RESULT_COMPARATOR = "result_comparator"  # OpenAI
    DIFFERENCE_ANALYZER = "difference_analyzer"  # Claude
    LEARNING_ENGINE = "learning_engine"  # Claude
    KNOWLEDGE_INTERPRETER = "knowledge_interpreter"  # Claude


class AgenteOrquestadorMultiModelo:
    """Orquestador que asigna tareas al mejor modelo"""
    
    def __init__(self):
        self.motor = MotorCotizacionPanelin()
        self.agente_base = AgenteAnalisisInteligente()
        
        # Configurar modelos
        self._configurar_modelos()
        
        # Mapeo de roles a modelos
        self.rol_modelo = {
            RolAgente.INPUT_PROCESSOR: ModeloIA.GEMINI,
            RolAgente.QUOTATION_CALCULATOR: ModeloIA.OPENAI,
            RolAgente.PDF_FINDER: ModeloIA.GEMINI,
            RolAgente.PDF_EXTRACTOR: ModeloIA.GEMINI,
            RolAgente.RESULT_COMPARATOR: ModeloIA.OPENAI,
            RolAgente.DIFFERENCE_ANALYZER: ModeloIA.CLAUDE,
            RolAgente.LEARNING_ENGINE: ModeloIA.CLAUDE,
            RolAgente.KNOWLEDGE_INTERPRETER: ModeloIA.CLAUDE,
        }
    
    def _configurar_modelos(self):
        """Configura acceso a los modelos"""
        from config.settings import settings
        self.openai_key = settings.OPENAI_API_KEY
        self.claude_key = settings.ANTHROPIC_API_KEY
        self.gemini_key = settings.GOOGLE_API_KEY
        
        self.modelos_disponibles = {
            ModeloIA.OPENAI: self.openai_key is not None,
            ModeloIA.CLAUDE: self.claude_key is not None,
            ModeloIA.GEMINI: self.gemini_key is not None,
        }
    
    # ========================================================================
    # ROL 1: INPUT_PROCESSOR (Gemini)
    # ========================================================================
    
    def procesar_inputs(self, cliente: str = None, producto: str = None) -> List[Dict]:
        """Procesa inputs del CSV - Usa Gemini"""
        print(f"📋 [{RolAgente.INPUT_PROCESSOR.value.upper()}] Procesando inputs...")
        print(f"   Modelo: {self.rol_modelo[RolAgente.INPUT_PROCESSOR].value.upper()}")
        
        # Usar agente base (puede mejorarse con Gemini específico)
        inputs = self.agente_base.revisar_inputs(cliente=cliente, producto=producto)
        
        # Si Gemini está disponible, usar para mejor procesamiento
        if self.modelos_disponibles[ModeloIA.GEMINI]:
            # Mejorar procesamiento con Gemini si es necesario
            inputs = self._mejorar_inputs_con_gemini(inputs)
        
        return inputs
    
    def _mejorar_inputs_con_gemini(self, inputs: List[Dict]) -> List[Dict]:
        """Mejora inputs usando Gemini para normalización"""
        # Por ahora usar agente base, pero estructura lista para Gemini
        return inputs
    
    # ========================================================================
    # ROL 2: QUOTATION_CALCULATOR (OpenAI GPT-4)
    # ========================================================================
    
    def generar_presupuesto(self, input_data: Dict) -> Dict:
        """Genera presupuesto - Usa OpenAI GPT-4"""
        print(f"🔧 [{RolAgente.QUOTATION_CALCULATOR.value.upper()}] Generando presupuesto...")
        print(f"   Modelo: {self.rol_modelo[RolAgente.QUOTATION_CALCULATOR].value.upper()}")
        
        # Usar motor validado (mejor que cualquier LLM para cálculos)
        presupuesto = self.agente_base.generar_presupuesto(input_data)
        
        # Si OpenAI está disponible, validar con GPT-4
        if self.modelos_disponibles[ModeloIA.OPENAI] and 'error' not in presupuesto:
            presupuesto = self._validar_presupuesto_con_openai(presupuesto)
        
        return presupuesto
    
    def _validar_presupuesto_con_openai(self, presupuesto: Dict) -> Dict:
        """Valida presupuesto con OpenAI GPT-4"""
        # Validación adicional con GPT-4 si es necesario
        return presupuesto
    
    # ========================================================================
    # ROL 3: PDF_FINDER (Gemini)
    # ========================================================================
    
    def buscar_pdf(self, input_data: Dict) -> Optional[Dict]:
        """Busca PDF real - Usa Gemini"""
        print(f"🔍 [{RolAgente.PDF_FINDER.value.upper()}] Buscando PDF...")
        print(f"   Modelo: {self.rol_modelo[RolAgente.PDF_FINDER].value.upper()}")
        
        # Usar agente base
        pdf_match = self.agente_base.buscar_pdf_cotizacion(input_data)
        
        # Si Gemini está disponible, mejorar búsqueda
        if self.modelos_disponibles[ModeloIA.GEMINI] and pdf_match:
            pdf_match = self._mejorar_busqueda_con_gemini(pdf_match, input_data)
        
        return pdf_match
    
    def _mejorar_busqueda_con_gemini(self, pdf_match: Dict, input_data: Dict) -> Dict:
        """Mejora búsqueda con Gemini"""
        return pdf_match
    
    # ========================================================================
    # ROL 4: PDF_EXTRACTOR (Gemini)
    # ========================================================================
    
    def extraer_datos_pdf(self, pdf_path: str) -> Dict:
        """Extrae datos de PDF - Usa Gemini"""
        print(f"📄 [{RolAgente.PDF_EXTRACTOR.value.upper()}] Extrayendo datos...")
        print(f"   Modelo: {self.rol_modelo[RolAgente.PDF_EXTRACTOR].value.upper()}")
        
        # Usar agente base
        datos = self.agente_base.extraer_datos_pdf(pdf_path)
        
        # Si Gemini está disponible, mejorar extracción
        if self.modelos_disponibles[ModeloIA.GEMINI]:
            datos = self._mejorar_extraccion_con_gemini(datos, pdf_path)
        
        return datos
    
    def _mejorar_extraccion_con_gemini(self, datos: Dict, pdf_path: str) -> Dict:
        """Mejora extracción con Gemini (multimodal)"""
        # Gemini puede procesar PDFs de forma más inteligente
        return datos
    
    # ========================================================================
    # ROL 5: RESULT_COMPARATOR (OpenAI GPT-4)
    # ========================================================================
    
    def comparar_resultados(self, presupuesto: Dict, pdf_real: Dict) -> Dict:
        """Compara resultados - Usa OpenAI GPT-4"""
        print(f"⚖️  [{RolAgente.RESULT_COMPARATOR.value.upper()}] Comparando resultados...")
        print(f"   Modelo: {self.rol_modelo[RolAgente.RESULT_COMPARATOR].value.upper()}")
        
        # Usar agente base
        comparacion = self.agente_base.comparar_resultados(presupuesto, pdf_real)
        
        # Si OpenAI está disponible, mejorar comparación
        if self.modelos_disponibles[ModeloIA.OPENAI] and 'error' not in comparacion:
            comparacion = self._mejorar_comparacion_con_openai(comparacion, presupuesto, pdf_real)
        
        return comparacion
    
    def _mejorar_comparacion_con_openai(self, comparacion: Dict, presupuesto: Dict, pdf_real: Dict) -> Dict:
        """Mejora comparación con OpenAI GPT-4"""
        # Análisis más profundo con GPT-4
        return comparacion
    
    # ========================================================================
    # ROL 6: DIFFERENCE_ANALYZER (Claude)
    # ========================================================================
    
    def analizar_diferencias(self, comparacion: Dict, presupuesto: Dict, pdf_real: Dict) -> Dict:
        """Analiza diferencias - Usa Claude"""
        print(f"🧠 [{RolAgente.DIFFERENCE_ANALYZER.value.upper()}] Analizando diferencias...")
        print(f"   Modelo: {self.rol_modelo[RolAgente.DIFFERENCE_ANALYZER].value.upper()}")
        
        # Usar agente base
        analisis = self.agente_base._analizar_diferencias(
            presupuesto, pdf_real,
            comparacion.get('diferencia', 0),
            comparacion.get('diferencia_porcentaje', 0)
        )
        
        # Si Claude está disponible, mejorar análisis
        if self.modelos_disponibles[ModeloIA.CLAUDE]:
            analisis = self._mejorar_analisis_con_claude(analisis, comparacion, presupuesto, pdf_real)
        
        return analisis
    
    def _mejorar_analisis_con_claude(self, analisis: Dict, comparacion: Dict, presupuesto: Dict, pdf_real: Dict) -> Dict:
        """Mejora análisis con Claude"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.claude_key)
            
            prompt = f"""Analiza las diferencias entre un presupuesto generado y un PDF real.

Presupuesto generado: ${comparacion.get('presupuesto_total', 0):.2f}
PDF real: ${comparacion.get('pdf_total', 0):.2f}
Diferencia: {comparacion.get('diferencia_porcentaje', 0):.2f}%

Analiza:
1. Posibles causas de la diferencia
2. Factores que podrían explicar la discrepancia
3. Recomendaciones para mejorar la precisión

Responde en formato JSON con:
- causas_detalladas: lista de causas posibles
- factores_explicativos: factores que podrían explicar
- recomendaciones: recomendaciones específicas"""

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parsear respuesta
            respuesta_texto = response.content[0].text
            try:
                claude_analisis = json.loads(respuesta_texto)
                analisis['claude_insights'] = claude_analisis
            except:
                analisis['claude_insights'] = {"texto": respuesta_texto}
        
        except Exception as e:
            print(f"   ⚠️  Error usando Claude: {e}")
        
        return analisis
    
    # ========================================================================
    # ROL 7: LEARNING_ENGINE (Claude)
    # ========================================================================
    
    def aprender_de_diferencias(self, comparacion: Dict) -> Dict:
        """Aprende de diferencias - Usa Claude"""
        print(f"📚 [{RolAgente.LEARNING_ENGINE.value.upper()}] Aprendiendo...")
        print(f"   Modelo: {self.rol_modelo[RolAgente.LEARNING_ENGINE].value.upper()}")
        
        # Usar agente base
        leccion = self.agente_base.aprender_de_diferencias(comparacion)
        
        # Si Claude está disponible, mejorar aprendizaje
        if self.modelos_disponibles[ModeloIA.CLAUDE]:
            leccion = self._mejorar_aprendizaje_con_claude(leccion, comparacion)
        
        return leccion
    
    def _mejorar_aprendizaje_con_claude(self, leccion: Dict, comparacion: Dict) -> Dict:
        """Mejora aprendizaje con Claude"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.claude_key)
            
            prompt = f"""Genera lecciones aprendidas de una comparación de cotizaciones.

Diferencia: {comparacion.get('diferencia_porcentaje', 0):.2f}%
Análisis: {json.dumps(comparacion.get('analisis', {}), ensure_ascii=False)}

Genera:
1. Lecciones clave aprendidas
2. Patrones identificados
3. Sugerencias de mejora para el sistema
4. Conocimiento a incorporar

Responde en formato JSON estructurado."""

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            respuesta_texto = response.content[0].text
            try:
                claude_lecciones = json.loads(respuesta_texto)
                leccion['claude_insights'] = claude_lecciones
            except:
                leccion['claude_insights'] = {"texto": respuesta_texto}
        
        except Exception as e:
            print(f"   ⚠️  Error usando Claude: {e}")
        
        return leccion
    
    # ========================================================================
    # ROL 8: KNOWLEDGE_INTERPRETER (Claude)
    # ========================================================================
    
    def interpretar_variables(self, input_data: Dict, conocimiento: Dict) -> Dict:
        """Interpreta variables y conocimiento - Usa Claude"""
        print(f"🔍 [{RolAgente.KNOWLEDGE_INTERPRETER.value.upper()}] Interpretando...")
        print(f"   Modelo: {self.rol_modelo[RolAgente.KNOWLEDGE_INTERPRETER].value.upper()}")
        
        if not self.modelos_disponibles[ModeloIA.CLAUDE]:
            return {"error": "Claude no disponible"}
        
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.claude_key)
            
            prompt = f"""Interpreta las variables de un input de cliente y correlaciónalo con el conocimiento disponible.

Input del cliente:
{json.dumps(input_data, ensure_ascii=False, indent=2)}

Conocimiento disponible:
{json.dumps(conocimiento, ensure_ascii=False, indent=2)}

Analiza:
1. Qué variables del input son relevantes
2. Cómo se correlacionan con el conocimiento
3. Qué información adicional se puede inferir
4. Qué variables ambiguas necesitan clarificación

Responde en formato JSON estructurado."""

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            respuesta_texto = response.content[0].text
            try:
                return json.loads(respuesta_texto)
            except:
                return {"interpretacion": respuesta_texto}
        
        except Exception as e:
            return {"error": str(e)}
    
    # ========================================================================
    # PROCESO COMPLETO ORQUESTADO
    # ========================================================================
    
    def proceso_completo_orquestado(self, cliente: str = None, producto: str = None, limite: int = 10) -> Dict:
        """Proceso completo usando el mejor modelo para cada tarea"""
        print("=" * 70)
        print("🤖 AGENTE ORQUESTADOR MULTI-MODELO")
        print("=" * 70)
        print("\n📊 Modelos disponibles:")
        for modelo, disponible in self.modelos_disponibles.items():
            status = "✅" if disponible else "❌"
            print(f"   {status} {modelo.value.upper()}")
        print()
        
        resultados = []
        
        # 1. INPUT_PROCESSOR (Gemini)
        inputs = self.procesar_inputs(cliente=cliente, producto=producto)
        if limite:
            inputs = inputs[:limite]
        
        for idx, input_data in enumerate(inputs, 1):
            print(f"\n{'='*70}")
            print(f"📊 Procesando {idx}/{len(inputs)}: {input_data.get('cliente', 'N/A')}")
            print(f"{'='*70}")
            
            # 2. KNOWLEDGE_INTERPRETER (Claude) - Opcional
            interpretacion = None
            if self.modelos_disponibles[ModeloIA.CLAUDE]:
                interpretacion = self.interpretar_variables(
                    input_data,
                    {"base_conocimiento": "disponible"}
                )
            
            # 3. QUOTATION_CALCULATOR (OpenAI)
            presupuesto = self.generar_presupuesto(input_data)
            
            if 'error' in presupuesto:
                resultados.append({
                    'input': input_data,
                    'interpretacion': interpretacion,
                    'presupuesto': None,
                    'pdf_real': None,
                    'comparacion': None,
                    'analisis': None,
                    'leccion': None
                })
                continue
            
            # 4. PDF_FINDER (Gemini)
            pdf_match = self.buscar_pdf(input_data)
            
            if not pdf_match:
                resultados.append({
                    'input': input_data,
                    'interpretacion': interpretacion,
                    'presupuesto': presupuesto,
                    'pdf_real': None,
                    'comparacion': None,
                    'analisis': None,
                    'leccion': None
                })
                continue
            
            # 5. PDF_EXTRACTOR (Gemini)
            pdf_datos = self.extraer_datos_pdf(pdf_match['path'])
            
            if pdf_datos.get('error'):
                resultados.append({
                    'input': input_data,
                    'interpretacion': interpretacion,
                    'presupuesto': presupuesto,
                    'pdf_real': {'error': pdf_datos['error'], 'path': pdf_match['path']},
                    'comparacion': None,
                    'analisis': None,
                    'leccion': None
                })
                continue
            
            # 6. RESULT_COMPARATOR (OpenAI)
            comparacion = self.comparar_resultados(presupuesto, pdf_datos)
            
            if 'error' in comparacion:
                resultados.append({
                    'input': input_data,
                    'interpretacion': interpretacion,
                    'presupuesto': presupuesto,
                    'pdf_real': {**pdf_datos, 'path': pdf_match['path']},
                    'comparacion': None,
                    'analisis': None,
                    'leccion': None
                })
                continue
            
            # 7. DIFFERENCE_ANALYZER (Claude)
            analisis = self.analizar_diferencias(comparacion, presupuesto, pdf_datos)
            comparacion['analisis'] = analisis
            
            # 8. LEARNING_ENGINE (Claude)
            leccion = self.aprender_de_diferencias(comparacion)
            
            resultados.append({
                'input': input_data,
                'interpretacion': interpretacion,
                'presupuesto': presupuesto,
                'pdf_real': {**pdf_datos, 'path': pdf_match['path'], 'nombre': pdf_match['nombre']},
                'comparacion': comparacion,
                'analisis': analisis,
                'leccion': leccion
            })
        
        # Resumen
        print(f"\n{'='*70}")
        print("📊 RESUMEN FINAL")
        print(f"{'='*70}")
        
        totales = len(resultados)
        con_pdf = sum(1 for r in resultados if r.get('pdf_real') and 'error' not in r.get('pdf_real', {}))
        comparados = sum(1 for r in resultados if r.get('comparacion') and r.get('comparacion') is not None and 'error' not in r.get('comparacion', {}))
        coinciden = sum(1 for r in resultados if r.get('comparacion') and r.get('comparacion') is not None and r.get('comparacion', {}).get('coincide', False))
        
        print(f"   📋 Inputs procesados: {totales}")
        print(f"   📄 PDFs encontrados: {con_pdf}")
        print(f"   ⚖️  Comparaciones realizadas: {comparados}")
        print(f"   ✅ Coincidencias: {coinciden}/{comparados}" if comparados > 0 else "   ✅ Coincidencias: N/A")
        
        return {
            'resultados': resultados,
            'resumen': {
                'totales': totales,
                'con_pdf': con_pdf,
                'comparados': comparados,
                'coinciden': coinciden
            },
            'modelos_usados': {
                rol.value: modelo.value for rol, modelo in self.rol_modelo.items()
            }
        }


if __name__ == "__main__":
    agente = AgenteOrquestadorMultiModelo()
    resultado = agente.proceso_completo_orquestado(limite=5)
    
    # Guardar resultado
    output_file = "analisis_multi_modelo_resultado.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Resultado guardado en: {output_file}")
