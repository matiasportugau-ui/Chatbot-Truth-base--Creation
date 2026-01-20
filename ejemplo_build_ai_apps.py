#!/usr/bin/env python3
"""
Ejemplo de Uso: Agente Build AI Apps
====================================

Ejemplos prácticos de cómo usar el agente especialista en Build AI Apps
"""

from agente_build_ai_apps import (
    diseñar_ai_app,
    listar_plantillas_ai_apps,
    usar_plantilla_ai_app,
    AgenteBuildAIApps
)


def ejemplo_1_diseñar_workflow_desde_cero():
    """Ejemplo 1: Diseñar un workflow desde cero"""
    print("=" * 70)
    print("📝 EJEMPLO 1: Diseñar Workflow desde Cero")
    print("=" * 70)
    
    descripcion = """Crea un app que tome una dirección de bienes raíces, 
    investigue el vecindario usando búsqueda web, escriba una descripción 
    profesional de listado, y genere tres captions diferentes para Instagram"""
    
    resultado = diseñar_ai_app(
        descripcion=descripcion,
        tipo="automation",
        optimizar=True,
        exportar_formato="json"
    )
    
    print(f"\n✅ Workflow diseñado: {resultado['workflow']['nombre']}")
    print(f"📊 Total de pasos: {len(resultado['workflow']['pasos'])}")
    print(f"✅ Válido: {resultado['valido']}")
    
    print("\n📋 Pasos del workflow:")
    for paso in resultado['workflow']['pasos']:
        print(f"  {paso['orden']}. {paso['nombre']} ({paso['tipo']})")
    
    print("\n📝 Descripción para Google Labs:")
    print("-" * 70)
    print(resultado['descripcion_gem'])
    
    print("\n📚 Instrucciones paso a paso:")
    print("-" * 70)
    for i, instruccion in enumerate(resultado['instrucciones'], 1):
        print(f"{i}. {instruccion}")
    
    return resultado


def ejemplo_2_usar_plantilla():
    """Ejemplo 2: Usar una plantilla predefinida"""
    print("\n\n" + "=" * 70)
    print("📝 EJEMPLO 2: Usar Plantilla Predefinida")
    print("=" * 70)
    
    # Listar plantillas disponibles
    print("\n📚 Plantillas disponibles:")
    plantillas = listar_plantillas_ai_apps()
    for plantilla in plantillas['plantillas']:
        print(f"  - {plantilla['id']}: {plantilla['nombre']}")
        print(f"    Descripción: {plantilla['descripcion']}")
        print(f"    Pasos: {plantilla['total_pasos']}")
    
    # Usar una plantilla
    print("\n🎨 Usando plantilla 'research_assistant'...")
    resultado = usar_plantilla_ai_app(
        id_plantilla="research_assistant",
        personalizar_nombre="Mi Asistente de Investigación Personalizado"
    )
    
    print(f"\n✅ Workflow creado: {resultado['workflow']['nombre']}")
    print(f"📊 Basado en plantilla: {resultado['workflow'].get('basado_en_plantilla', 'N/A')}")
    
    print("\n📝 Descripción para Google Labs:")
    print("-" * 70)
    print(resultado['descripcion_gem'])
    
    return resultado


def ejemplo_3_remix_workflow():
    """Ejemplo 3: Remix de un workflow existente"""
    print("\n\n" + "=" * 70)
    print("📝 EJEMPLO 3: Remix de Workflow")
    print("=" * 70)
    
    agente = AgenteBuildAIApps()
    
    # Crear workflow base
    print("\n🎨 Creando workflow base...")
    workflow_base = agente.diseñar_workflow(
        descripcion="Crea un app que genere recetas basadas en ingredientes disponibles",
        tipo="content"
    )
    
    print(f"✅ Workflow base creado: {workflow_base['nombre']}")
    print(f"📊 Pasos originales: {len(workflow_base['pasos'])}")
    
    # Remix con modificaciones
    print("\n🔄 Remixeando workflow...")
    workflow_remix = agente.remix_workflow(
        workflow_base=workflow_base,
        modificaciones="Agrega un paso para traducir las recetas al español y generar una lista de compras"
    )
    
    print(f"✅ Workflow remix creado: {workflow_remix['nombre']}")
    print(f"📊 Pasos después del remix: {len(workflow_remix['pasos'])}")
    print(f"🔄 Remix de: {workflow_remix.get('remix_de', 'N/A')}")
    
    print("\n📋 Nuevos pasos:")
    for paso in workflow_remix['pasos']:
        print(f"  {paso['orden']}. {paso['nombre']}")
    
    return workflow_remix


def ejemplo_4_optimizacion():
    """Ejemplo 4: Optimización de workflow"""
    print("\n\n" + "=" * 70)
    print("📝 EJEMPLO 4: Optimización de Workflow")
    print("=" * 70)
    
    agente = AgenteBuildAIApps()
    
    # Crear workflow complejo
    print("\n🎨 Creando workflow complejo...")
    workflow = agente.diseñar_workflow(
        descripcion="""Crea un app que procese un texto, lo analice, busque información adicional, 
        lo procese de nuevo, lo transforme, genere contenido, y lo analice una vez más""",
        tipo="data_processing"
    )
    
    print(f"✅ Workflow creado: {workflow['nombre']}")
    print(f"📊 Pasos antes de optimizar: {len(workflow['pasos'])}")
    
    # Optimizar
    print("\n⚡ Optimizando workflow...")
    workflow_optimizado = agente.optimizar_workflow(workflow)
    
    print(f"✅ Workflow optimizado: {workflow_optimizado.get('optimizado', False)}")
    
    optimizaciones = workflow_optimizado.get('optimizaciones', [])
    if optimizaciones:
        print(f"\n💡 Optimizaciones sugeridas: {len(optimizaciones)}")
        for opt in optimizaciones:
            print(f"  - [{opt['tipo']}] {opt['descripcion']}")
            print(f"    Acción: {opt['accion']}")
    else:
        print("\n✅ No se encontraron optimizaciones necesarias")
    
    return workflow_optimizado


def ejemplo_5_exportacion():
    """Ejemplo 5: Exportación en diferentes formatos"""
    print("\n\n" + "=" * 70)
    print("📝 EJEMPLO 5: Exportación de Workflow")
    print("=" * 70)
    
    agente = AgenteBuildAIApps()
    
    # Crear workflow
    workflow = agente.diseñar_workflow(
        descripcion="Crea un app que analice tweets y genere un reporte de sentimientos",
        tipo="analysis"
    )
    
    print(f"✅ Workflow creado: {workflow['nombre']}")
    
    # Exportar en diferentes formatos
    formatos = ["json", "markdown", "gem_description"]
    
    for formato in formatos:
        print(f"\n📄 Exportando en formato: {formato}")
        print("-" * 70)
        contenido = agente.exportar_workflow(workflow, formato)
        
        if formato == "json":
            print("(JSON completo - mostrando primeros 500 caracteres)")
            print(contenido[:500] + "...")
        elif formato == "markdown":
            print(contenido[:500] + "...")
        else:  # gem_description
            print(contenido)
    
    # Guardar workflow
    print("\n💾 Guardando workflow...")
    ruta = agente.guardar_workflow(workflow, "ejemplo_workflow.json")
    print(f"✅ Guardado en: {ruta}")
    
    return workflow


def main():
    """Ejecuta todos los ejemplos"""
    print("\n" + "=" * 70)
    print("🚀 EJEMPLOS: Agente Build AI Apps")
    print("=" * 70)
    
    try:
        # Ejemplo 1
        resultado1 = ejemplo_1_diseñar_workflow_desde_cero()
        
        # Ejemplo 2
        resultado2 = ejemplo_2_usar_plantilla()
        
        # Ejemplo 3
        resultado3 = ejemplo_3_remix_workflow()
        
        # Ejemplo 4
        resultado4 = ejemplo_4_optimizacion()
        
        # Ejemplo 5
        resultado5 = ejemplo_5_exportacion()
        
        print("\n\n" + "=" * 70)
        print("✅ TODOS LOS EJEMPLOS COMPLETADOS")
        print("=" * 70)
        
        print("\n📊 Resumen:")
        print(f"  - Workflows diseñados: 5")
        print(f"  - Plantillas usadas: 1")
        print(f"  - Workflows remixeados: 1")
        print(f"  - Workflows optimizados: 1")
        print(f"  - Workflows exportados: 1")
        
    except Exception as e:
        print(f"\n❌ Error ejecutando ejemplos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
