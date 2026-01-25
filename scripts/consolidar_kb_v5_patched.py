#!/usr/bin/env python3
"""
Script de Consolidación de Knowledge Base v5.0 (Patched)
Consolida múltiples archivos JSON en uno solo con validación, omitiendo Level 2 si falta.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import argparse


class KBConsolidator:
    """Consolidador de Knowledge Base"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.errores = []
        self.advertencias = []
        self.estadisticas = {}

    def cargar_json(self, filename: str) -> Dict[str, Any]:
        """Carga archivo JSON con manejo de errores"""
        filepath = self.base_path / filename
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ Cargado: {filename} ({filepath.stat().st_size / 1024:.1f} KB)")
                return data
        except FileNotFoundError:
            self.advertencias.append(f"Archivo no encontrado (omitido): {filename}")
            print(f"⚠️  ADVERTENCIA: {filename} no encontrado. Se omitirá.")
            return {}
        except json.JSONDecodeError as e:
            self.errores.append(f"Error JSON en {filename}: {e}")
            print(f"❌ ERROR: {filename} tiene JSON inválido")
            return {}

    def merge_productos(self, nivel1: Dict, nivel2: Dict, nivel3: Dict) -> List[Dict]:
        """
        Merge productos de 3 niveles
        Prioridad: nivel3 (precios más recientes) > nivel2 > nivel1
        """
        productos = {}

        # Base: nivel1 (estructura completa)
        for producto in nivel1.get("productos", nivel1.get("product_catalog", [])):
            producto_id = producto.get("id", producto.get("nombre", ""))
            if producto_id:
                productos[producto_id] = producto.copy()

        print(f"📦 Base Nivel 1: {len(productos)} productos")

        # Actualizar con nivel2 (validación) - Si existe
        if nivel2:
            nivel2_productos = nivel2.get("productos", nivel2.get("product_catalog", []))
            for producto in nivel2_productos:
                producto_id = producto.get("id", producto.get("nombre", ""))
                if producto_id in productos:
                    if "validaciones" in producto:
                        productos[producto_id]["validaciones"] = producto["validaciones"]
                    if "casos_uso" in producto:
                        productos[producto_id]["casos_uso"] = producto["casos_uso"]
            print(f"📦 Después Nivel 2: {len(productos)} productos (validaciones agregadas)")
        else:
            print("📦 Nivel 2 omitido (vacío)")

        # Actualizar con nivel3 (precios más recientes)
        if nivel3:
            nivel3_productos = nivel3.get("productos", nivel3.get("product_catalog", []))
            actualizados = 0
            for producto in nivel3_productos:
                producto_id = producto.get("id", producto.get("nombre", ""))
                if producto_id in productos:
                    if self.es_mas_reciente(producto, productos[producto_id]):
                        if "precios" in producto:
                            productos[producto_id]["precios"] = producto["precios"]
                            productos[producto_id]["ultima_actualizacion"] = producto.get(
                                "fecha",
                                producto.get("ultima_actualizacion", "")
                            )
                            actualizados += 1
            print(f"📦 Después Nivel 3: {actualizados} productos con precios actualizados")
        else:
            print("📦 Nivel 3 omitido (vacío)")

        return list(productos.values())

    def es_mas_reciente(self, producto_nuevo: Dict, producto_existente: Dict) -> bool:
        """Compara fechas de actualización"""
        fecha_nuevo = producto_nuevo.get("fecha", producto_nuevo.get("ultima_actualizacion", ""))
        fecha_existente = producto_existente.get("ultima_actualizacion", "")

        if not fecha_existente:
            return True

        return fecha_nuevo > fecha_existente

    def consolidar(self) -> Dict[str, Any]:
        """Consolida los niveles disponibles"""
        print("\n" + "="*60)
        print("🔄 CONSOLIDANDO KNOWLEDGE BASE v5.0 (PATCHED)")
        print("="*60 + "\n")

        print("📂 Cargando archivos...\n")
        nivel1 = self.cargar_json("BMC_Base_Conocimiento_GPT-2.json")
        nivel2 = self.cargar_json("BMC_Base_Unificada_v4.json") # Puede faltar
        nivel3 = self.cargar_json("panelin_truth_bmcuruguay_web_only_v2.json")

        if self.errores:
            print("\n❌ Errores críticos durante carga:")
            for error in self.errores:
                print(f"  - {error}")
            return {}

        if not nivel1:
             print("\n❌ Error crítico: Falta Nivel 1 (Master)")
             return {}

        print("\n🔀 Consolidando productos...\n")
        productos_consolidados = self.merge_productos(nivel1, nivel2, nivel3)

        kb_consolidada = {
            "version": "5.0",
            "fecha_creacion": datetime.now().isoformat(),
            "descripcion": "Knowledge Base Consolidada - Fuente de Verdad Única para PANELIN BMC Assistant Pro",
            "fuentes_originales": {
                "nivel1_master": "BMC_Base_Conocimiento_GPT-2.json",
                "nivel2_validacion": "BMC_Base_Unificada_v4.json (Omitido)" if not nivel2 else "BMC_Base_Unificada_v4.json",
                "nivel3_dinamico": "panelin_truth_bmcuruguay_web_only_v2.json"
            },
            "metadata": {
                "productos_totales": len(productos_consolidados),
                "formulas_cotizacion": len(nivel1.get("formulas_cotizacion", {})),
                "consolidado_por": "consolidar_kb_v5_patched.py",
                "consolidado_en": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "productos": productos_consolidados,
            "formulas_cotizacion": nivel1.get("formulas_cotizacion", {}),
            "formulas_ahorro_energetico": nivel1.get("formulas_ahorro_energetico", {}),
            "reglas_negocio": {
                "moneda": "USD",
                "iva_porcentaje": 22,
                "pendiente_minima_techo": 7,
                "fuente_precios": "Shopify",
                **nivel1.get("reglas_negocio", {})
            }
        }

        self.estadisticas = {
            "productos": len(productos_consolidados),
            "formulas": len(kb_consolidada.get("formulas_cotizacion", {})),
            "reglas": len(kb_consolidada.get("reglas_negocio", {}))
        }

        print("\n✅ Consolidación completada!")
        print(f"📊 Productos consolidados: {self.estadisticas['productos']}")
        print(f"📐 Fórmulas incluidas: {self.estadisticas['formulas']}")
        print(f"📋 Reglas de negocio: {self.estadisticas['reglas']}")

        return kb_consolidada

    def guardar(self, kb: Dict[str, Any], output_file: str = None) -> bool:
        """Guarda KB consolidada en archivo JSON"""
        if not output_file:
            output_file = "BMC_Base_Conocimiento_CONSOLIDADA_v5.0.json"

        output_path = self.base_path / output_file

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(kb, f, indent=2, ensure_ascii=False)

            size_kb = output_path.stat().st_size / 1024
            print(f"\n✅ Archivo guardado: {output_file}")
            print(f"📦 Tamaño: {size_kb:.1f} KB")
            print(f"📍 Ruta: {output_path}")

            return True
        except Exception as e:
            print(f"\n❌ ERROR al guardar: {e}")
            return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="BMC_Base_Conocimiento_CONSOLIDADA_v5.0.json")
    parser.add_argument("--base-path", default=".")
    args = parser.parse_args()

    consolidador = KBConsolidator(base_path=args.base_path)
    kb_consolidada = consolidador.consolidar()

    if kb_consolidada:
        consolidador.guardar(kb_consolidada, args.output)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
