#!/usr/bin/env python3
"""
Comprehensive Diagnostic Report Generator

Generates a consolidated PDF report from all diagnostic results:
- Agent Extraction results
- Gap Analysis results
- KB Evaluation results

Usage:
    python generar_reporte_diagnostico.py --output diagnostico_20260123.pdf
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Any, List

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.platypus import Image as RLImage
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️  Warning: reportlab not installed. Install with: pip install reportlab")


class DiagnosticReportGenerator:
    """Generate comprehensive diagnostic PDF report"""
    
    def __init__(self, output_path: str, project_root: str):
        """
        Initialize report generator
        
        Args:
            output_path: Path for output PDF file
            project_root: Root directory of the project
        """
        self.output_path = Path(output_path)
        self.project_root = Path(project_root)
        self.styles = None
        
    def _load_diagnostic_data(self) -> Dict[str, Any]:
        """Load all diagnostic data files"""
        data = {}
        
        # Load extraction results
        extraction_file = self.project_root / "diagnostico_extraction.json"
        if extraction_file.exists():
            with open(extraction_file, 'r', encoding='utf-8') as f:
                data['extraction'] = json.load(f)
        
        # Load gap analysis results
        gap_file = self.project_root / "diagnostico_gap_analysis.json"
        if gap_file.exists():
            with open(gap_file, 'r', encoding='utf-8') as f:
                data['gap_analysis'] = json.load(f)
        
        # Load KB evaluation results
        kb_file = self.project_root / "diagnostico_kb_evaluation.json"
        if kb_file.exists():
            with open(kb_file, 'r', encoding='utf-8') as f:
                data['kb_evaluation'] = json.load(f)
        
        return data
    
    def generate_markdown_report(self, data: Dict[str, Any]) -> str:
        """Generate Markdown version of the report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# Reporte de Diagnóstico Completo del Sistema
**Fecha:** {timestamp}

---

## 📊 Resumen Ejecutivo

### Estado General del Sistema
"""
        
        # Extraction summary
        if 'extraction' in data:
            extraction = data['extraction']
            scores = extraction.get('confidence_scores', {})
            overall_score = scores.get('overall', 0) * 100
            
            report += f"""
### Extracción de Conocimiento
- **Confianza General:** {overall_score:.1f}%
- **Identidad:** {'✅ Extraída' if scores.get('identity', 0) > 0.8 else '⚠️ Incompleta'}
- **Knowledge Base:** {'✅ Detectada' if scores.get('knowledge_base', 0) > 0.8 else '⚠️ Incompleta'}
- **Instrucciones:** {'✅ Extraídas' if scores.get('instructions', 0) > 0.8 else '⚠️ Incompletas'}
- **Productos:** {len(extraction.get('products', {}))} productos encontrados
- **Fórmulas:** {len(extraction.get('formulas', {}))} fórmulas encontradas

#### Scores de Confianza Detallados:
"""
            for key, score in scores.items():
                bar = "█" * int(score * 20)
                report += f"- **{key}:** {bar} {score:.2%}\n"
        
        # Gap analysis summary
        if 'gap_analysis' in data:
            gap = data['gap_analysis']
            completion = gap.get('completion_percentage', 0)
            
            report += f"""
### Análisis de Brechas
- **Completitud:** {completion:.1f}%
- **Campos Extraídos:** {len(gap.get('extracted_fields', []))}
- **Campos Faltantes:** {len(gap.get('missing_fields', []))}

#### Solicitudes de Extracción:
"""
            requests = gap.get('extraction_requests', {})
            report += f"- **Auto-extraíbles:** {len(requests.get('auto_extractable', []))}\n"
            report += f"- **Semi-automáticos:** {len(requests.get('semi_automatic', []))}\n"
            report += f"- **Manuales requeridos:** {len(requests.get('manual_required', []))}\n"
        
        # KB evaluation summary
        if 'kb_evaluation' in data:
            kb = data['kb_evaluation']
            metrics = kb.get('metrics', {})
            
            report += f"""
### Evaluación de Knowledge Base
- **Total de Evaluaciones:** {kb.get('total_evaluations', 0)}
- **Relevancia Promedio:** {metrics.get('average_relevance', 0):.3f}
- **Groundedness Promedio:** {metrics.get('average_groundedness', 0):.3f}
- **Coherencia Promedio:** {metrics.get('average_coherence', 0):.3f}
- **Precisión Promedio:** {metrics.get('average_accuracy', 0):.3f}
- **Tasa de Cumplimiento de Fuente:** {metrics.get('source_compliance_rate', 0):.1%}
- **Tasa de Fugas:** {metrics.get('leak_rate', 0):.2f} fugas por consulta
- **Cobertura de KB:** {metrics.get('kb_coverage_score', 0):.1%}
- **Efectividad de Instrucciones:** {metrics.get('instruction_effectiveness', 0):.3f}

#### Métricas Detalladas:
"""
            for metric_name, metric_value in metrics.items():
                if isinstance(metric_value, float):
                    bar = "█" * int(metric_value * 20) if metric_value <= 1.0 else "█" * 20
                    report += f"- **{metric_name}:** {bar} {metric_value:.3f}\n"
        
        report += """
---

## 🔍 Análisis Detallado

### 1. Extracción de Conocimiento
"""
        
        if 'extraction' in data:
            extraction = data['extraction']
            
            # Identity info
            identity = extraction.get('identity', {})
            if identity:
                report += "\n#### Identidad del Bot:\n"
                for key, value in identity.items():
                    report += f"- **{key}:** {value}\n"
            
            # KB files
            kb_files = extraction.get('knowledge_base', {}).get('files', [])
            report += f"\n#### Archivos de Knowledge Base ({len(kb_files)}):\n"
            for i, file_path in enumerate(kb_files[:20], 1):
                report += f"{i}. `{Path(file_path).name}`\n"
            if len(kb_files) > 20:
                report += f"... y {len(kb_files) - 20} archivos más\n"
        
        report += """
### 2. Brechas y Campos Faltantes
"""
        
        if 'gap_analysis' in data:
            gap = data['gap_analysis']
            
            # Missing fields
            missing = gap.get('missing_fields', [])
            if missing:
                report += f"\n#### Campos Faltantes ({len(missing)}):\n"
                for i, field in enumerate(missing[:15], 1):
                    report += f"{i}. `{field.get('path', 'unknown')}` - {field.get('description', '')}\n"
                if len(missing) > 15:
                    report += f"... y {len(missing) - 15} campos más\n"
            
            # Extraction requests
            requests = gap.get('extraction_requests', {})
            
            auto = requests.get('auto_extractable', [])
            if auto:
                report += f"\n#### Auto-Extraíbles ({len(auto)}):\n"
                for i, req in enumerate(auto[:10], 1):
                    report += f"{i}. `{req.get('field', 'unknown')}` - {req.get('source', '')}\n"
            
            semi = requests.get('semi_automatic', [])
            if semi:
                report += f"\n#### Semi-Automáticos ({len(semi)}):\n"
                for i, req in enumerate(semi[:10], 1):
                    report += f"{i}. `{req.get('field', 'unknown')}` - {req.get('guidance', '')}\n"
            
            manual = requests.get('manual_required', [])
            if manual:
                report += f"\n#### Manuales Requeridos ({len(manual)}):\n"
                for i, req in enumerate(manual[:10], 1):
                    report += f"{i}. `{req.get('field', 'unknown')}` - {req.get('description', '')}\n"
        
        report += """
### 3. Evaluación de Knowledge Base
"""
        
        if 'kb_evaluation' in data:
            kb = data['kb_evaluation']
            detailed = kb.get('detailed_metrics', {})
            
            # Leak types
            leak_types = detailed.get('leak_types', {})
            if leak_types:
                report += "\n#### Tipos de Fugas de Conocimiento:\n"
                for leak_type, count in leak_types.items():
                    report += f"- **{leak_type}:** {count} ocurrencias\n"
            
            # Source usage
            source_usage = detailed.get('source_usage', {})
            if source_usage:
                report += "\n#### Uso de Fuentes:\n"
                for source, count in sorted(source_usage.items(), key=lambda x: x[1], reverse=True)[:10]:
                    report += f"- `{source}`: {count} veces\n"
        
        report += """
---

## 🎯 Recomendaciones Prioritarias

### Acción Inmediata (Hoy):
1. ✅ **Corregir campos faltantes auto-extraíbles**
   - Ejecutar extracción automática de campos identificados
   - Validar resultados

2. ⚠️ **Mejorar cumplimiento de Source of Truth**
   - Revisar que todas las respuestas usen fuentes de Nivel 1 (Master)
   - Actualizar instrucciones si es necesario

3. 📊 **Revisar fugas de conocimiento detectadas**
   - Analizar las categorías con más fugas
   - Planificar actualización de KB

### Corto Plazo (Esta Semana):
1. **Completar extracción semi-automática**
   - Revisar campos que requieren confirmación
   - Documentar decisiones

2. **Optimizar instrucciones del sistema**
   - Mejorar claridad en áreas con baja coherencia
   - Agregar ejemplos donde sea necesario

3. **Actualizar Knowledge Base**
   - Agregar información faltante identificada
   - Consolidar fuentes duplicadas

### Mediano Plazo (Este Mes):
1. **Implementar KB v5.0 Consolidada**
   - Ejecutar script de consolidación
   - Validar integridad de datos
   - Migrar a nueva estructura

2. **Establecer sistema de monitoreo continuo**
   - Configurar métricas automáticas
   - Implementar alertas para fugas de conocimiento

3. **Mejorar training pipeline**
   - Optimizar flujo de entrenamiento
   - Incrementar frecuencia de evaluaciones

---

## 📈 Métricas de Éxito

### Objetivos Actuales vs. Target:

| Métrica | Actual | Target | Estado |
|---------|--------|--------|--------|
"""
        
        if 'kb_evaluation' in data:
            kb = data['kb_evaluation']
            metrics = kb.get('metrics', {})
            
            metrics_targets = [
                ('Relevancia', metrics.get('average_relevance', 0), 0.85),
                ('Groundedness', metrics.get('average_groundedness', 0), 0.90),
                ('Coherencia', metrics.get('average_coherence', 0), 0.85),
                ('Precisión', metrics.get('average_accuracy', 0), 0.80),
                ('Source Compliance', metrics.get('source_compliance_rate', 0), 0.95),
                ('KB Coverage', metrics.get('kb_coverage_score', 0), 0.90),
            ]
            
            for metric_name, current, target in metrics_targets:
                status = "✅" if current >= target else "⚠️" if current >= target * 0.7 else "❌"
                report += f"| {metric_name} | {current:.3f} | {target:.3f} | {status} |\n"
        
        report += """
---

## 📅 Plan de Seguimiento

### Revisión Semanal:
- Ejecutar diagnósticos de métricas
- Verificar mejora en scores
- Ajustar estrategia si es necesario

### Testing Quincenal:
- Ejecutar test suite completo
- Validar todas las categorías de conocimiento
- Documentar casos edge encontrados

### Actualización Mensual:
- Consolidar aprendizajes del mes
- Actualizar KB con nuevo conocimiento validado
- Generar snapshot de versión

### Auditoría Trimestral:
- Evaluación completa del sistema
- Benchmark contra mejores prácticas
- Planificación de mejoras para próximo trimestre

---

## 📊 Apéndices

### A. Archivos de Diagnóstico Generados:
- `diagnostico_extraction.json` - Resultados de extracción
- `diagnostico_gap_analysis.json` - Análisis de brechas
- `diagnostico_kb_evaluation.json` - Evaluación de KB
- `diagnostico_kb_evaluation.md` - Reporte detallado de evaluación

### B. Scripts Disponibles:
- `run_extraction.py` - Ejecutar extracción de conocimiento
- `run_gap_analysis.py` - Ejecutar análisis de brechas
- `run_kb_evaluator.py` - Ejecutar evaluación de KB
- `generar_reporte_diagnostico.py` - Generar este reporte
- `consolidar_kb_v5.py` - Consolidar KB a v5.0

### C. Próximos Scripts a Implementar:
- Sistema de versionado de KB
- Dashboard de monitoreo en tiempo real
- Validador post-respuesta automático

---

**Reporte generado:** {timestamp}  
**Sistema:** Chatbot Truth Base Creation - Panelin Knowledge System
"""
        
        return report
    
    def generate(self) -> str:
        """Generate the diagnostic report"""
        print("=" * 70)
        print("GENERANDO REPORTE DE DIAGNÓSTICO COMPLETO")
        print("=" * 70)
        
        # Load diagnostic data
        print("\n📂 Cargando datos de diagnóstico...")
        data = self._load_diagnostic_data()
        
        if not data:
            print("❌ Error: No se encontraron archivos de diagnóstico.")
            print("   Ejecute primero los scripts de diagnóstico:")
            print("   - python3 run_extraction.py")
            print("   - python3 run_gap_analysis.py")
            print("   - python3 run_kb_evaluator.py")
            return ""
        
        print(f"✅ Cargados {len(data)} conjuntos de datos")
        
        # Generate Markdown report
        print("\n📝 Generando reporte Markdown...")
        markdown_report = self.generate_markdown_report(data)
        
        # Save Markdown version
        md_path = self.output_path.with_suffix('.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        print(f"✅ Reporte Markdown guardado: {md_path}")
        
        # Generate PDF if reportlab is available
        if REPORTLAB_AVAILABLE and self.output_path.suffix == '.pdf':
            print("\n📄 Generando reporte PDF...")
            print("⚠️  Nota: La generación de PDF desde Markdown complejo requiere")
            print("   herramientas adicionales. Se ha generado la versión Markdown.")
            print("   Para convertir a PDF, use:")
            print(f"   pandoc {md_path} -o {self.output_path}")
        
        print("\n" + "=" * 70)
        print("✅ REPORTE DE DIAGNÓSTICO GENERADO EXITOSAMENTE")
        print("=" * 70)
        print(f"\nReporte Markdown: {md_path}")
        if self.output_path.suffix == '.pdf':
            print(f"Para PDF: pandoc {md_path} -o {self.output_path}")
        print()
        
        return str(md_path)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Generate comprehensive diagnostic report'
    )
    parser.add_argument(
        '--output',
        default=f"diagnostico_{datetime.now().strftime('%Y%m%d')}.md",
        help='Output file path (default: diagnostico_YYYYMMDD.md)'
    )
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent
    generator = DiagnosticReportGenerator(args.output, str(project_root))
    
    try:
        report_path = generator.generate()
        return 0
    except Exception as e:
        print(f"\n❌ Error generando reporte: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
