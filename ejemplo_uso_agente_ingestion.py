#!/usr/bin/env python3
"""
Ejemplo de Uso: Agente de Ingestion y Análisis
===============================================

Ejemplos de cómo usar el agente de ingestion y análisis.
"""

from agente_ingestion_analisis import AgenteIngestionAnalisis
import json
from pathlib import Path


def ejemplo_1_ingestion_completa():
    """Ejemplo 1: Ingestion completa desde todas las fuentes"""
    print("=" * 70)
    print("Ejemplo 1: Ingestion Completa")
    print("=" * 70)
    
    agente = AgenteIngestionAnalisis()
    
    # Generar tabla de ingestion
    resultado = agente.generar_tabla_ingestion()
    
    print("\n📊 Resumen de Ingestion:")
    print(f"   Total de registros: {resultado['total_records']}")
    print(f"   Por fuente: {resultado['by_source']}")
    print(f"   Por plataforma: {resultado['by_platform']}")
    print(f"   Base de datos: {resultado['database_path']}")


def ejemplo_2_analisis_cotizaciones():
    """Ejemplo 2: Análisis de cotizaciones"""
    print("\n" + "=" * 70)
    print("Ejemplo 2: Análisis de Cotizaciones")
    print("=" * 70)
    
    agente = AgenteIngestionAnalisis()
    
    # Primero hacer ingestion si no existe
    agente.generar_tabla_ingestion()
    
    # Analizar cotizaciones
    resultado = agente.analizar_cotizaciones()
    
    print("\n📊 Resumen de Análisis de Cotizaciones:")
    print(f"   Total de cotizaciones: {resultado['total_quotes']}")
    
    if resultado.get('summary'):
        summary = resultado['summary']
        print(f"   Completitud promedio: {summary.get('avg_completeness', 0):.2%}")
        print(f"   Distribución de productos: {summary.get('product_distribution', {})}")
        print(f"   Total de issues: {summary.get('total_issues', 0)}")


def ejemplo_3_analisis_redes_sociales():
    """Ejemplo 3: Análisis de redes sociales"""
    print("\n" + "=" * 70)
    print("Ejemplo 3: Análisis de Redes Sociales")
    print("=" * 70)
    
    agente = AgenteIngestionAnalisis()
    
    # Primero hacer ingestion si no existe
    agente.generar_tabla_ingestion()
    
    # Analizar redes sociales
    resultado = agente.analizar_redes_sociales()
    
    print("\n📱 Resumen de Análisis de Redes Sociales:")
    print(f"   Total de consultas: {resultado['total_queries']}")
    
    if resultado.get('summary'):
        summary = resultado['summary']
        print(f"   Por plataforma: {summary.get('by_platform', {})}")
        print(f"   Tasa de preguntas: {summary.get('question_rate', 0):.2%}")
        print(f"   Tasa de respuesta requerida: {summary.get('response_rate', 0):.2%}")
        print(f"   Score de engagement promedio: {summary.get('avg_engagement_score', 0):.2f}")


def ejemplo_4_analisis_respuestas():
    """Ejemplo 4: Análisis de respuestas del chatbot"""
    print("\n" + "=" * 70)
    print("Ejemplo 4: Análisis de Respuestas")
    print("=" * 70)
    
    agente = AgenteIngestionAnalisis()
    
    # Primero hacer ingestion si no existe
    agente.generar_tabla_ingestion()
    
    # Analizar respuestas
    resultado = agente.analizar_respuestas()
    
    print("\n💬 Resumen de Análisis de Respuestas:")
    print(f"   Total de respuestas: {resultado['total_responses']}")
    
    if resultado.get('summary'):
        summary = resultado['summary']
        print(f"   Relevancia promedio: {summary.get('avg_relevance_score', 0):.2f}")
        print(f"   Precisión promedio: {summary.get('avg_accuracy_score', 0):.2f}")
        print(f"   Completitud promedio: {summary.get('avg_completeness_score', 0):.2f}")
        print(f"   Tasa de coincidencia de sentimiento: {summary.get('sentiment_match_rate', 0):.2%}")
        print(f"   Total de issues: {summary.get('total_issues', 0)}")


def ejemplo_5_reporte_completo():
    """Ejemplo 5: Reporte completo"""
    print("\n" + "=" * 70)
    print("Ejemplo 5: Reporte Completo")
    print("=" * 70)
    
    agente = AgenteIngestionAnalisis()
    
    # Generar reporte completo
    reporte = agente.generar_reporte_completo()
    
    print("\n📋 Resumen del Reporte:")
    print(f"   Timestamp: {reporte['timestamp']}")
    print(f"   Total de registros: {reporte['ingestion_summary']['total_records']}")
    
    if reporte.get('recommendations'):
        print("\n💡 Recomendaciones:")
        for rec in reporte['recommendations']:
            print(f"   - {rec}")


def ejemplo_6_consulta_base_datos():
    """Ejemplo 6: Consultar base de datos directamente"""
    print("\n" + "=" * 70)
    print("Ejemplo 6: Consulta de Base de Datos")
    print("=" * 70)
    
    import sqlite3
    
    agente = AgenteIngestionAnalisis()
    
    # Conectar a la base de datos
    conn = sqlite3.connect(agente.db_path)
    cursor = conn.cursor()
    
    # Consulta 1: Contar por fuente
    print("\n📊 Registros por fuente:")
    cursor.execute("SELECT source, COUNT(*) FROM ingestion_table GROUP BY source")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]}")
    
    # Consulta 2: Últimos 5 registros
    print("\n📝 Últimos 5 registros:")
    cursor.execute("""
        SELECT id, source, platform, timestamp, user_query 
        FROM ingestion_table 
        ORDER BY timestamp DESC 
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"   [{row[1]}] {row[4][:50]}...")
    
    # Consulta 3: Cotizaciones incompletas
    print("\n⚠️  Cotizaciones incompletas:")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM quote_analysis 
        WHERE json_extract(analysis_result, '$.completeness_score') < 0.7
    """)
    count = cursor.fetchone()[0]
    print(f"   Total: {count}")
    
    conn.close()


if __name__ == "__main__":
    print("🚀 Ejemplos de Uso: Agente de Ingestion y Análisis")
    print("=" * 70)
    
    # Ejecutar ejemplos
    try:
        ejemplo_1_ingestion_completa()
        ejemplo_2_analisis_cotizaciones()
        ejemplo_3_analisis_redes_sociales()
        ejemplo_4_analisis_respuestas()
        ejemplo_5_reporte_completo()
        ejemplo_6_consulta_base_datos()
        
        print("\n" + "=" * 70)
        print("✅ Todos los ejemplos completados")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
