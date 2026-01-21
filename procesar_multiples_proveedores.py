#!/usr/bin/env python3
"""
Procesador de Múltiples Proveedores
Analiza múltiples archivos CSV (cada uno representa una pestaña/proveedor)
y genera una base de conocimiento unificada
"""

import json
import csv
from pathlib import Path
from typing import Dict, List
from analizar_matriz_costos import AnalizadorMatrizCostos


def buscar_archivos_proveedores(directorio: str = ".") -> List[tuple]:
    """
    Busca archivos CSV que representen diferentes proveedores
    Retorna lista de tuplas (nombre_proveedor, ruta_archivo)
    """
    directorio_path = Path(directorio)
    archivos_proveedores = []
    
    # Buscar archivos CSV que contengan "MATRIZ" o "COSTOS"
    for archivo in directorio_path.glob("*.csv"):
        nombre = archivo.stem
        
        # Intentar extraer nombre del proveedor del nombre del archivo
        # Formato esperado: "MATRIZ de COSTOS y VENTAS 2026.xlsx - PROVEEDOR.csv"
        if "MATRIZ" in nombre.upper() or "COSTOS" in nombre.upper():
            # Extraer nombre del proveedor (después del último " - ")
            partes = nombre.split(" - ")
            if len(partes) > 1:
                proveedor = partes[-1]
            else:
                # Si no hay separador, usar parte del nombre
                proveedor = nombre.replace("MATRIZ de COSTOS y VENTAS 2026.xlsx", "").strip()
                if not proveedor:
                    proveedor = archivo.stem
            
            archivos_proveedores.append((proveedor, str(archivo)))
    
    return archivos_proveedores


def procesar_todos_proveedores(directorio: str = ".") -> Dict:
    """
    Procesa todos los archivos de proveedores encontrados
    """
    archivos = buscar_archivos_proveedores(directorio)
    
    if not archivos:
        print("⚠️  No se encontraron archivos de proveedores")
        print("   Buscando archivos con formato: 'MATRIZ de COSTOS y VENTAS 2026.xlsx - PROVEEDOR.csv'")
        return {}
    
    print(f"📋 Encontrados {len(archivos)} archivo(s) de proveedor(es):")
    for proveedor, archivo in archivos:
        print(f"   - {proveedor}: {archivo}")
    
    # Procesar cada proveedor
    kb_unificada = {
        "meta": {
            "nombre": "Base de Conocimiento Unificada - Costos y Precios por Proveedor",
            "version": "1.0",
            "fecha_creacion": None,
            "fuente": "MATRIZ de COSTOS y VENTAS 2026.xlsx",
            "descripcion": "Costos y precios organizados por proveedor y tipo de compra",
            "total_proveedores": len(archivos)
        },
        "estructura_precios": {
            "compras_fabrica_directo": {
                "descripcion": "Precios para compras directas a fábrica",
                "campos": [
                    "costo_base_usd_iva",
                    "costo_con_aumento_usd_iva",
                    "costo_proximo_aumento_usd_iva"
                ]
            },
            "compras_web_stock": {
                "descripcion": "Precios para compras web o desde stock",
                "campos": [
                    "venta_iva_usd",
                    "consumidor_iva_inc_usd",
                    "web_venta_iva_usd",
                    "web_venta_iva_inc_usd"
                ]
            }
        },
        "proveedores": {}
    }
    
    resumen_unificado = {
        "total_proveedores": len(archivos),
        "proveedores": {}
    }
    
    for proveedor, archivo_path in archivos:
        print(f"\n📊 Procesando proveedor: {proveedor}")
        print(f"   Archivo: {archivo_path}")
        
        try:
            analizador = AnalizadorMatrizCostos(archivo_path)
            productos = analizador.analizar_csv(proveedor)
            
            # Agregar a KB unificada
            kb_unificada["proveedores"][proveedor] = {
                "nombre": proveedor,
                "archivo_origen": archivo_path,
                "secciones": {}
            }
            
            for seccion, productos_lista in productos.items():
                kb_unificada["proveedores"][proveedor]["secciones"][seccion] = {
                    "nombre": seccion,
                    "total_productos": len(productos_lista),
                    "productos": productos_lista
                }
            
            # Generar resumen del proveedor
            resumen = analizador.generar_resumen()
            resumen_unificado["proveedores"][proveedor] = resumen["proveedores"][proveedor]
            
            print(f"   ✅ Procesado: {len(productos)} secciones, {sum(len(p) for p in productos.values())} productos")
            
        except Exception as e:
            print(f"   ❌ Error procesando {proveedor}: {e}")
            continue
    
    # Actualizar fecha de creación
    from datetime import datetime
    kb_unificada["meta"]["fecha_creacion"] = datetime.now().isoformat()
    
    return {
        "kb": kb_unificada,
        "resumen": resumen_unificado
    }


def main():
    """Función principal"""
    print("🔍 Buscando archivos de proveedores...\n")
    
    resultado = procesar_todos_proveedores(".")
    
    if not resultado or not resultado.get("kb"):
        print("\n❌ No se pudo procesar ningún proveedor")
        return
    
    # Guardar KB unificada
    output_kb = "BMC_Base_Costos_Precios_UNIFICADA.json"
    with open(output_kb, 'w', encoding='utf-8') as f:
        json.dump(resultado["kb"], f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Base de conocimiento unificada guardada en: {output_kb}")
    
    # Guardar resumen unificado
    output_resumen = "resumen_analisis_costos_UNIFICADO.json"
    with open(output_resumen, 'w', encoding='utf-8') as f:
        json.dump(resultado["resumen"], f, ensure_ascii=False, indent=2)
    
    print(f"📄 Resumen unificado guardado en: {output_resumen}")
    
    # Mostrar resumen final
    print("\n📈 RESUMEN FINAL:")
    print(json.dumps(resultado["resumen"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
