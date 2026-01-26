#!/usr/bin/env python3
"""
Ejemplos de uso del GPT Correction Agent
=========================================

Este script muestra cómo usar el agente para aplicar correcciones
a la base de conocimientos del GPT.
"""

from pathlib import Path
from correction_agent import GPTCorrectionAgent
import json

# Inicializar agente
agent = GPTCorrectionAgent(
    project_root=str(Path(__file__).parent.parent),
    backup_enabled=True
)


def ejemplo_correccion_institucional():
    """Ejemplo: Corregir información institucional."""
    print("\n=== Ejemplo 1: Corrección Institucional ===")
    
    result = agent.apply_correction(
        correction_id="KB-001",
        correction_type="institucional",
        description="Actualizar descripción institucional - BMC no fabrica",
        priority="P0",
        changes={
            "descripcion": "BMC Uruguay no fabrica. Suministra/comercializa sistemas constructivos y brinda asesoramiento técnico-comercial para definir la solución correcta según la obra.",
            "diferencial": "Soluciones técnicas optimizadas para generar confort, ahorrar presupuesto, optimizar estructura, reducir tiempos de obra y evitar problemas a futuro."
        }
    )
    
    print(f"Resultado: {'✓ Éxito' if result['success'] else '✗ Error'}")
    print(f"Archivos modificados: {len(result['affected_files'])}")
    for file, file_result in result['results'].items():
        print(f"  - {file}: {len(file_result.get('changes_applied', []))} cambios")


def ejemplo_correccion_producto():
    """Ejemplo: Agregar nuevo producto al catálogo."""
    print("\n=== Ejemplo 2: Agregar Producto ===")
    
    result = agent.apply_correction(
        correction_id="KB-003",
        correction_type="producto",
        description="Agregar producto Isofrig PIR para cámaras frigoríficas",
        priority="P1",
        changes={
            "product_id": "ISOFRIG_PIR",
            "nombre_comercial": "Isofrig (PIR)",
            "tipo": "pared_frigorifica",
            "ignifugo": "Excelente (PIR - Alta resistencia al fuego)",
            "aplicacion": "Cámaras frigoríficas, cuartos fríos, industria alimenticia",
            "espesores": {
                "50": {
                    "autoportancia": 3.0,
                    "precio": 55.0,
                    "coeficiente_termico": 0.022,
                    "resistencia_termica": 2.27
                },
                "80": {
                    "autoportancia": 4.5,
                    "precio": 60.0,
                    "coeficiente_termico": 0.022,
                    "resistencia_termica": 3.64
                },
                "100": {
                    "autoportancia": 5.5,
                    "precio": 65.0,
                    "coeficiente_termico": 0.022,
                    "resistencia_termica": 4.55
                }
            },
            "lineas_mencionadas": {
                "paredes_y_fachadas": ["Isopanel EPS", "Isowall PIR", "Isofrig PIR"]
            }
        }
    )
    
    print(f"Resultado: {'✓ Éxito' if result['success'] else '✗ Error'}")
    if result['success']:
        print("Producto ISOFRIG_PIR agregado correctamente")


def ejemplo_correccion_precio():
    """Ejemplo: Actualizar precio de un producto."""
    print("\n=== Ejemplo 3: Actualizar Precio ===")
    
    result = agent.apply_correction(
        correction_id="KB-PRICE-001",
        correction_type="precio",
        description="Actualizar precio de ISODEC EPS 100mm",
        priority="P0",
        changes={
            "product_id": "ISODEC_EPS",
            "espesor": "100",
            "nuevo_precio": 47.50
        }
    )
    
    print(f"Resultado: {'✓ Éxito' if result['success'] else '✗ Error'}")
    if result['success']:
        for file, file_result in result['results'].items():
            for change in file_result.get('changes_applied', []):
                print(f"  {change}")


def ejemplo_correccion_formula():
    """Ejemplo: Actualizar fórmula de cálculo."""
    print("\n=== Ejemplo 4: Actualizar Fórmula ===")
    
    result = agent.apply_correction(
        correction_id="KB-FORMULA-001",
        correction_type="formula",
        description="Corregir fórmula de cálculo de apoyos",
        priority="P1",
        changes={
            "tipo_formula": "cotizacion",
            "nombre_formula": "calculo_apoyos",
            "nueva_formula": "ROUNDUP((LARGO / AUTOPORTANCIA) + 1)"
        }
    )
    
    print(f"Resultado: {'✓ Éxito' if result['success'] else '✗ Error'}")


def ejemplo_correccion_capabilities():
    """Ejemplo: Actualizar políticas de capabilities."""
    print("\n=== Ejemplo 5: Actualizar Capabilities ===")
    
    result = agent.apply_correction(
        correction_id="KB-CAP-001",
        correction_type="capabilities",
        description="Actualizar política de transcripción de audio",
        priority="P1",
        changes={
            "audio": {
                "policy": "No transcribir ni afirmar contenido literal de audios si no existe un flujo/herramienta de transcripción disponible. Si el usuario comparte un audio (por ejemplo WhatsApp .ogg), solicitar transcripción o un resumen textual, y recién entonces analizar y dar feedback."
            }
        }
    )
    
    print(f"Resultado: {'✓ Éxito' if result['success'] else '✗ Error'}")


def ejemplo_lote_correcciones():
    """Ejemplo: Aplicar múltiples correcciones en lote."""
    print("\n=== Ejemplo 6: Lote de Correcciones ===")
    
    corrections = [
        {
            "correction_id": "KB-BATCH-001",
            "correction_type": "institucional",
            "description": "Actualizar diferencial competitivo",
            "priority": "P0",
            "changes": {
                "diferencial": "Soluciones técnicas optimizadas para generar confort, ahorrar presupuesto, optimizar estructura, reducir tiempos de obra y evitar problemas a futuro."
            }
        },
        {
            "correction_id": "KB-BATCH-002",
            "correction_type": "precio",
            "description": "Actualizar precio ISODEC EPS 150mm",
            "priority": "P1",
            "changes": {
                "product_id": "ISODEC_EPS",
                "espesor": "150",
                "nuevo_precio": 52.00
            }
        }
    ]
    
    summary = agent.batch_apply_corrections(corrections)
    
    print(f"Total correcciones: {summary['total_corrections']}")
    print(f"Exitosas: {summary['successful']}")
    print(f"Fallidas: {summary['failed']}")


def ejemplo_validacion():
    """Ejemplo: Validar cambios aplicados."""
    print("\n=== Ejemplo 7: Validación de Cambios ===")
    
    kb_file = Path(__file__).parent.parent / "BMC_Base_Conocimiento_GPT-2.json"
    
    if kb_file.exists():
        validation = agent.validate_changes(kb_file)
        
        print(f"Archivo válido: {'✓ Sí' if validation['valid'] else '✗ No'}")
        if validation.get('errors'):
            print("Errores:")
            for error in validation['errors']:
                print(f"  - {error}")
        if validation.get('warnings'):
            print("Advertencias:")
            for warning in validation['warnings']:
                print(f"  - {warning}")
    else:
        print("Archivo no encontrado para validar")


if __name__ == "__main__":
    print("=" * 60)
    print("GPT Correction Agent - Ejemplos de Uso")
    print("=" * 60)
    
    # Descomentar los ejemplos que quieras ejecutar
    # ejemplo_correccion_institucional()
    # ejemplo_correccion_producto()
    # ejemplo_correccion_precio()
    # ejemplo_correccion_formula()
    # ejemplo_correccion_capabilities()
    # ejemplo_lote_correcciones()
    # ejemplo_validacion()
    
    print("\n" + "=" * 60)
    print("Para ejecutar ejemplos, descomenta las funciones en el script")
    print("=" * 60)
