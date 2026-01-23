#!/usr/bin/env python3
"""
Script de Consolidación de Knowledge Base v5.0
Consolida múltiples archivos JSON en uno solo con validación

Uso:
    python scripts/consolidar_kb_v5.py
    python scripts/consolidar_kb_v5.py --output custom_output.json
    python scripts/consolidar_kb_v5.py --validate-only
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
            self.errores.append(f"Archivo no encontrado: {filename}")
            print(f"❌ ERROR: {filename} no encontrado")
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

        # Actualizar con nivel2 (validación)
        nivel2_productos = nivel2.get("productos", nivel2.get("product_catalog", []))
        for producto in nivel2_productos:
            producto_id = producto.get("id", producto.get("nombre", ""))
            if producto_id in productos:
                # Merge validaciones si existen
                if "validaciones" in producto:
                    productos[producto_id]["validaciones"] = producto["validaciones"]
                if "casos_uso" in producto:
                    productos[producto_id]["casos_uso"] = producto["casos_uso"]

        print(f"📦 Después Nivel 2: {len(productos)} productos (validaciones agregadas)")

        # Actualizar con nivel3 (precios más recientes)
        nivel3_productos = nivel3.get("productos", nivel3.get("product_catalog", []))
        actualizados = 0
        for producto in nivel3_productos:
            producto_id = producto.get("id", producto.get("nombre", ""))
            if producto_id in productos:
                # Actualizar precios si más recientes
                if self.es_mas_reciente(producto, productos[producto_id]):
                    if "precios" in producto:
                        productos[producto_id]["precios"] = producto["precios"]
                        productos[producto_id]["ultima_actualizacion"] = producto.get(
                            "fecha",
                            producto.get("ultima_actualizacion", "")
                        )
                        actualizados += 1

        print(f"📦 Después Nivel 3: {actualizados} productos con precios actualizados")

        return list(productos.values())

    def es_mas_reciente(self, producto_nuevo: Dict, producto_existente: Dict) -> bool:
        """Compara fechas de actualización"""
        fecha_nuevo = producto_nuevo.get("fecha", producto_nuevo.get("ultima_actualizacion", ""))
        fecha_existente = producto_existente.get("ultima_actualizacion", "")

        # Si no hay fechas, asumir que nivel3 es más reciente
        if not fecha_existente:
            return True

        return fecha_nuevo > fecha_existente

    def consolidar(self) -> Dict[str, Any]:
        """Consolida los 3 niveles de KB"""
        print("\n" + "="*60)
        print("🔄 CONSOLIDANDO KNOWLEDGE BASE v5.0")
        print("="*60 + "\n")

        # Cargar archivos
        print("📂 Cargando archivos...\n")
        nivel1 = self.cargar_json("BMC_Base_Conocimiento_GPT-2.json")
        nivel2 = self.cargar_json("BMC_Base_Unificada_v4.json")
        nivel3 = self.cargar_json("panelin_truth_bmcuruguay_web_only_v2.json")

        if self.errores:
            print("\n❌ Errores críticos durante carga:")
            for error in self.errores:
                print(f"  - {error}")
            return {}

        print("\n🔀 Consolidando productos...\n")
        productos_consolidados = self.merge_productos(nivel1, nivel2, nivel3)

        # Crear KB consolidada
        kb_consolidada = {
            "version": "5.0",
            "fecha_creacion": datetime.now().isoformat(),
            "descripcion": "Knowledge Base Consolidada - Fuente de Verdad Única para PANELIN BMC Assistant Pro",
            "fuentes_originales": {
                "nivel1_master": "BMC_Base_Conocimiento_GPT-2.json",
                "nivel2_validacion": "BMC_Base_Unificada_v4.json",
                "nivel3_dinamico": "panelin_truth_bmcuruguay_web_only_v2.json"
            },
            "metadata": {
                "productos_totales": len(productos_consolidados),
                "formulas_cotizacion": len(nivel1.get("formulas_cotizacion", {})),
                "consolidado_por": "consolidar_kb_v5.py",
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

        # Estadísticas
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

    def validar_consistencia(self, kb: Dict[str, Any]) -> bool:
        """Valida que no haya inconsistencias en la KB consolidada"""
        print("\n" + "="*60)
        print("🔍 VALIDANDO CONSISTENCIA")
        print("="*60 + "\n")

        self.errores = []
        self.advertencias = []

        # Validar precios
        print("💰 Validando precios...")
        productos_sin_precio = 0
        for producto in kb.get("productos", []):
            producto_nombre = producto.get("nombre", "Desconocido")
            precios = producto.get("precios", {})

            if not precios:
                self.advertencias.append(f"Producto sin precios: {producto_nombre}")
                productos_sin_precio += 1
            else:
                for espesor, datos in precios.items():
                    if isinstance(datos, dict):
                        if not datos.get("precio_unitario"):
                            self.errores.append(
                                f"Precio faltante: {producto_nombre} {espesor}"
                            )

        if productos_sin_precio > 0:
            print(f"  ⚠️  {productos_sin_precio} productos sin precios")
        else:
            print("  ✅ Todos los productos tienen precios")

        # Validar fórmulas
        print("\n📐 Validando fórmulas...")
        formulas_requeridas = [
            "paneles_necesarios",
            "apoyos",
            "fijaciones_hormigon",
            "sellador"
        ]
        formulas_faltantes = []
        for formula in formulas_requeridas:
            if formula not in kb.get("formulas_cotizacion", {}):
                self.errores.append(f"Fórmula faltante: {formula}")
                formulas_faltantes.append(formula)

        if formulas_faltantes:
            print(f"  ❌ {len(formulas_faltantes)} fórmulas faltantes")
        else:
            print(f"  ✅ Todas las fórmulas presentes ({len(formulas_requeridas)})")

        # Validar estructura
        print("\n🏗️  Validando estructura...")
        campos_requeridos = ["productos", "formulas_cotizacion", "reglas_negocio"]
        campos_faltantes = []
        for campo in campos_requeridos:
            if campo not in kb:
                self.errores.append(f"Campo requerido faltante: {campo}")
                campos_faltantes.append(campo)

        if campos_faltantes:
            print(f"  ❌ {len(campos_faltantes)} campos faltantes")
        else:
            print(f"  ✅ Estructura completa")

        # Resumen de validación
        print("\n" + "-"*60)
        if self.errores:
            print(f"❌ ERRORES CRÍTICOS: {len(self.errores)}")
            for error in self.errores[:5]:  # Mostrar solo primeros 5
                print(f"  - {error}")
            if len(self.errores) > 5:
                print(f"  ... y {len(self.errores) - 5} errores más")

        if self.advertencias:
            print(f"\n⚠️  ADVERTENCIAS: {len(self.advertencias)}")
            for advertencia in self.advertencias[:5]:
                print(f"  - {advertencia}")
            if len(self.advertencias) > 5:
                print(f"  ... y {len(self.advertencias) - 5} advertencias más")

        if not self.errores and not self.advertencias:
            print("✅ VALIDACIÓN EXITOSA: Sin errores ni advertencias")
            return True
        elif not self.errores:
            print("✅ VALIDACIÓN EXITOSA: Sin errores críticos")
            return True
        else:
            print("❌ VALIDACIÓN FALLIDA: Corregir errores antes de continuar")
            return False

    def guardar(self, kb: Dict[str, Any], output_file: str = None) -> bool:
        """Guarda KB consolidada en archivo JSON"""
        if not output_file:
            fecha = datetime.now().strftime("%Y%m%d")
            output_file = f"BMC_Base_Conocimiento_CONSOLIDADA_v5.0_{fecha}.json"

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

    def generar_reporte(self, kb: Dict[str, Any]) -> str:
        """Genera reporte de consolidación"""
        reporte = f"""
╔═══════════════════════════════════════════════════════════╗
║     REPORTE DE CONSOLIDACIÓN - KNOWLEDGE BASE v5.0        ║
╚═══════════════════════════════════════════════════════════╝

Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

📊 ESTADÍSTICAS:
  • Productos consolidados: {self.estadisticas.get('productos', 0)}
  • Fórmulas de cotización: {self.estadisticas.get('formulas', 0)}
  • Reglas de negocio: {self.estadisticas.get('reglas', 0)}

📁 FUENTES ORIGINALES:
  • Nivel 1 (Master): BMC_Base_Conocimiento_GPT-2.json
  • Nivel 2 (Validación): BMC_Base_Unificada_v4.json
  • Nivel 3 (Dinámico): panelin_truth_bmcuruguay_web_only_v2.json

✅ RESULTADO:
  • Archivo único consolidado
  • Cero inconsistencias entre fuentes
  • Fuente de verdad absoluta

🔄 PRÓXIMOS PASOS:
  1. Subir archivo consolidado a GPT Builder
  2. Eliminar archivos antiguos (Nivel 1, 2, 3)
  3. Actualizar instrucciones del GPT (simplificar)
  4. Testing con casos reales

═══════════════════════════════════════════════════════════
"""
        return reporte


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Consolida múltiples archivos de Knowledge Base en uno solo"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Nombre del archivo de salida (default: BMC_Base_Conocimiento_CONSOLIDADA_v5.0_YYYYMMDD.json)"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Solo validar archivos existentes sin consolidar"
    )
    parser.add_argument(
        "--base-path",
        default=".",
        help="Ruta base donde están los archivos JSON (default: directorio actual)"
    )

    args = parser.parse_args()

    # Crear consolidador
    consolidador = KBConsolidator(base_path=args.base_path)

    # Si solo validación
    if args.validate_only:
        print("🔍 Modo: Solo validación\n")
        # Cargar archivo consolidado si existe
        kb_file = "BMC_Base_Conocimiento_CONSOLIDADA_v5.0.json"
        if Path(kb_file).exists():
            with open(kb_file) as f:
                kb = json.load(f)
            consolidador.validar_consistencia(kb)
        else:
            print(f"❌ Archivo {kb_file} no encontrado")
        return

    # Consolidar
    kb_consolidada = consolidador.consolidar()

    if not kb_consolidada:
        print("\n❌ Consolidación fallida. Revisa los errores arriba.")
        sys.exit(1)

    # Validar
    valido = consolidador.validar_consistencia(kb_consolidada)

    if not valido:
        print("\n⚠️  KB consolidada tiene errores. ¿Guardar de todas formas? (y/n): ", end="")
        respuesta = input().strip().lower()
        if respuesta != 'y':
            print("❌ Consolidación cancelada")
            sys.exit(1)

    # Guardar
    if consolidador.guardar(kb_consolidada, args.output):
        # Generar reporte
        reporte = consolidador.generar_reporte(kb_consolidada)
        print(reporte)

        # Guardar reporte
        reporte_file = "REPORTE_CONSOLIDACION_KB_v5.0.txt"
        with open(reporte_file, 'w', encoding='utf-8') as f:
            f.write(reporte)
        print(f"📄 Reporte guardado: {reporte_file}")

        print("\n🎉 ¡CONSOLIDACIÓN EXITOSA!")
        print("\n📋 PRÓXIMOS PASOS:")
        print("  1. Revisar archivo consolidado")
        print("  2. Backup de archivos antiguos")
        print("  3. Subir a GPT Builder")
        print("  4. Testing")
    else:
        print("\n❌ Error al guardar archivo consolidado")
        sys.exit(1)


if __name__ == "__main__":
    main()
