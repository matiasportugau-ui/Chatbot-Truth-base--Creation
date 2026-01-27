#!/usr/bin/env python3
"""
GPT Configuration Verification Script
====================================

Verifica que la configuración del GPT Panelin esté correcta:
- Archivos de Knowledge Base existen y están bien formateados
- Instrucciones del sistema contienen elementos críticos
- Estructura de datos es válida
- Fórmulas están presentes
- Productos tienen datos completos
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import sys


@dataclass
class VerificationResult:
    """Resultado de una verificación"""
    check_name: str
    status: str  # "PASS", "FAIL", "WARNING"
    message: str
    details: List[str] = None


class GPTConfigurationVerifier:
    """Verificador de configuración del GPT"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.results: List[VerificationResult] = []
        self.kb_files = {
            "level_1_master": ["BMC_Base_Conocimiento_GPT.json", "BMC_Base_Conocimiento_GPT-2.json"],
            "level_2_validation": "BMC_Base_Unificada_v4.json",
            "level_3_dynamic": "panelin_truth_bmcuruguay_web_only_v2.json",
            "sop": "panelin_context_consolidacion_sin_backend.md",
            "technical_rules": ["Aleros.rtf", "Aleros -2.rtf"],
            "catalog_index": "panelin_truth_bmcuruguay_catalog_v2_index.csv"
        }
        self.instructions_file = "Instrucciones_Sistema_Panelin_CopiarPegar.txt"
    
    def verify_all(self) -> List[VerificationResult]:
        """Ejecuta todas las verificaciones"""
        print("🔍 Iniciando verificación de configuración GPT Panelin...\n")
        
        # 1. Verificar archivos de KB
        self._verify_kb_files_exist()
        
        # 2. Verificar formato JSON
        self._verify_json_format()
        
        # 3. Verificar estructura de datos
        self._verify_data_structure()
        
        # 4. Verificar fórmulas
        self._verify_formulas()
        
        # 5. Verificar productos
        self._verify_products()
        
        # 6. Verificar instrucciones del sistema
        self._verify_system_instructions()
        
        # 7. Verificar jerarquía de fuentes
        self._verify_source_hierarchy()
        
        # 8. Verificar reglas de negocio
        self._verify_business_rules()
        
        return self.results
    
    def _verify_kb_files_exist(self):
        """Verifica que los archivos de KB existan"""
        print("📁 Verificando archivos de Knowledge Base...")
        
        for level, filenames in self.kb_files.items():
            # Si es lista, buscar cualquiera de las variaciones
            if isinstance(filenames, list):
                found = False
                for filename in filenames:
                    filepath = self._find_file(filename)
                    if filepath:
                        self._add_result("PASS", f"Archivo {filename} existe", 
                                      [f"Ruta: {filepath}"])
                        found = True
                        break
                if not found:
                    self._add_result("FAIL", f"Archivo {level} NO encontrado",
                                   [f"Buscado: {', '.join(filenames)}"])
            else:
                filename = filenames
                filepath = self._find_file(filename)
                if filepath:
                    self._add_result("PASS", f"Archivo {filename} existe", 
                                  [f"Ruta: {filepath}"])
                else:
                    self._add_result("FAIL", f"Archivo {filename} NO encontrado",
                                   [f"Buscado en: {self.base_path / filename}"])
    
    def _verify_json_format(self):
        """Verifica que los JSONs estén bien formateados"""
        print("\n📄 Verificando formato JSON...")
        
        json_files = [
            "BMC_Base_Conocimiento_GPT.json",
            "BMC_Base_Unificada_v4.json",
            "panelin_truth_bmcuruguay_web_only_v2.json"
        ]
        
        for filename in json_files:
            filepath = self._find_file(filename)
            if not filepath:
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._add_result("PASS", f"{filename} tiene formato JSON válido",
                                [f"Tamaño: {len(json.dumps(data))} caracteres"])
            except json.JSONDecodeError as e:
                self._add_result("FAIL", f"{filename} tiene errores de formato JSON",
                               [f"Error: {str(e)}"])
            except Exception as e:
                self._add_result("WARNING", f"No se pudo verificar {filename}",
                               [f"Error: {str(e)}"])
    
    def _verify_data_structure(self):
        """Verifica la estructura de datos del archivo master"""
        print("\n🏗️  Verificando estructura de datos...")
        
        # Buscar archivo master (puede tener variaciones en el nombre)
        master_file = None
        for alt_name in ["BMC_Base_Conocimiento_GPT.json", "BMC_Base_Conocimiento_GPT-2.json"]:
            master_file = self._find_file(alt_name)
            if master_file:
                break
        
        if not master_file:
            self._add_result("FAIL", "No se puede verificar estructura: archivo master no encontrado",
                           ["Buscado: BMC_Base_Conocimiento_GPT.json y variaciones"])
            return
        
        try:
            with open(master_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            required_sections = [
                "meta",
                "products",
                "formulas_cotizacion",
                "reglas_negocio"
            ]
            
            for section in required_sections:
                if section in data:
                    self._add_result("PASS", f"Sección '{section}' presente",
                                   [f"Tipo: {type(data[section]).__name__}"])
                else:
                    self._add_result("FAIL", f"Sección '{section}' FALTANTE")
            
            # Verificar estructura de meta
            if "meta" in data:
                meta_required = ["nombre", "version", "fecha"]
                for field in meta_required:
                    if field in data["meta"]:
                        self._add_result("PASS", f"Campo meta.{field} presente")
                    else:
                        self._add_result("WARNING", f"Campo meta.{field} faltante")
        
        except Exception as e:
            self._add_result("FAIL", f"Error al verificar estructura: {str(e)}")
    
    def _verify_formulas(self):
        """Verifica que las fórmulas estén presentes y correctas"""
        print("\n🧮 Verificando fórmulas de cotización...")
        
        master_file = self._find_file("BMC_Base_Conocimiento_GPT.json")
        if not master_file:
            return
        
        try:
            with open(master_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "formulas_cotizacion" not in data:
                self._add_result("FAIL", "Sección 'formulas_cotizacion' no encontrada")
                return
            
            formulas = data["formulas_cotizacion"]
            required_formulas = [
                "costo_panel",
                "calculo_apoyos",
                "puntos_fijacion_techo",
                "varilla_cantidad",
                "tuercas_metal",
                "tuercas_hormigon",
                "tacos_hormigon",
                "gotero_frontal",
                "gotero_lateral"
            ]
            
            for formula_name in required_formulas:
                if formula_name in formulas:
                    formula_value = formulas[formula_name]
                    self._add_result("PASS", f"Fórmula '{formula_name}' presente",
                                   [f"Valor: {formula_value}"])
                else:
                    self._add_result("FAIL", f"Fórmula '{formula_name}' FALTANTE")
            
            # Verificar que las fórmulas contengan ROUNDUP donde corresponde
            formulas_requiring_roundup = [
                "calculo_apoyos",
                "puntos_fijacion_techo",
                "varilla_cantidad",
                "gotero_frontal",
                "gotero_lateral"
            ]
            
            for formula_name in formulas_requiring_roundup:
                if formula_name in formulas:
                    formula_value = str(formulas[formula_name]).upper()
                    if "ROUNDUP" in formula_value or "CEIL" in formula_value:
                        self._add_result("PASS", f"Fórmula '{formula_name}' usa redondeo")
                    else:
                        self._add_result("WARNING", 
                                       f"Fórmula '{formula_name}' podría necesitar ROUNDUP")
        
        except Exception as e:
            self._add_result("FAIL", f"Error al verificar fórmulas: {str(e)}")
    
    def _verify_products(self):
        """Verifica que los productos tengan datos completos"""
        print("\n📦 Verificando productos...")
        
        master_file = self._find_file("BMC_Base_Conocimiento_GPT.json")
        if not master_file:
            return
        
        try:
            with open(master_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "products" not in data:
                self._add_result("FAIL", "Sección 'products' no encontrada")
                return
            
            products = data["products"]
            required_products = [
                "ISODEC_EPS",
                "ISODEC_PIR",
                "ISOROOF_3G",
                "ISOPANEL_EPS",
                "ISOWALL_PIR"
            ]
            
            for product_id in required_products:
                if product_id in products:
                    product = products[product_id]
                    
                    # Verificar campos requeridos
                    required_fields = ["nombre_comercial", "tipo", "ancho_util", "espesores"]
                    missing_fields = []
                    
                    for field in required_fields:
                        if field not in product:
                            missing_fields.append(field)
                    
                    if not missing_fields:
                        self._add_result("PASS", f"Producto '{product_id}' completo",
                                       [f"Nombre: {product.get('nombre_comercial', 'N/A')}",
                                        f"Espesores: {len(product.get('espesores', {}))}"])
                    else:
                        self._add_result("WARNING", f"Producto '{product_id}' tiene campos faltantes",
                                       missing_fields)
                else:
                    self._add_result("FAIL", f"Producto '{product_id}' NO encontrado")
            
            # Verificar que los productos tengan precios
            for product_id, product in products.items():
                espesores = product.get("espesores", {})
                if not espesores:
                    self._add_result("WARNING", f"Producto '{product_id}' no tiene espesores definidos")
                else:
                    espesores_sin_precio = []
                    for espesor, data in espesores.items():
                        if "precio" not in data:
                            espesores_sin_precio.append(espesor)
                    
                    if espesores_sin_precio:
                        self._add_result("WARNING", 
                                       f"Producto '{product_id}' tiene espesores sin precio",
                                       espesores_sin_precio)
        
        except Exception as e:
            self._add_result("FAIL", f"Error al verificar productos: {str(e)}")
    
    def _verify_system_instructions(self):
        """Verifica que las instrucciones del sistema contengan elementos críticos"""
        print("\n📝 Verificando instrucciones del sistema...")
        
        instructions_file = self.base_path / self.instructions_file
        if not instructions_file.exists():
            self._add_result("FAIL", f"Archivo de instrucciones '{self.instructions_file}' no encontrado")
            return
        
        try:
            with open(instructions_file, 'r', encoding='utf-8') as f:
                instructions = f.read()
            
            critical_elements = {
                "Source of Truth": [
                    "BMC_Base_Conocimiento_GPT.json",
                    "SIEMPRE usar este archivo primero",
                    "NIVEL 1 - MASTER"
                ],
                "Personalización": [
                    "Mauro",
                    "Martin",
                    "Rami"
                ],
                "Guardrails": [
                    "NO inventes precios",
                    "No tengo esa información"
                ],
                "Fórmulas": [
                    "formulas_cotizacion",
                    "ROUNDUP"
                ],
                "Comandos SOP": [
                    "/estado",
                    "/checkpoint",
                    "/consolidar"
                ],
                "Reglas de Negocio": [
                    "IVA: 22%",
                    "USD",
                    "pendiente mínima"
                ]
            }
            
            for element_name, keywords in critical_elements.items():
                found_keywords = [kw for kw in keywords if kw.upper() in instructions.upper()]
                if len(found_keywords) >= len(keywords) * 0.7:  # Al menos 70% de keywords
                    self._add_result("PASS", f"Instrucciones contienen '{element_name}'",
                                   [f"Keywords encontradas: {len(found_keywords)}/{len(keywords)}"])
                else:
                    self._add_result("WARNING", 
                                   f"Instrucciones podrían necesitar más '{element_name}'",
                                   [f"Keywords encontradas: {len(found_keywords)}/{len(keywords)}"])
        
        except Exception as e:
            self._add_result("FAIL", f"Error al verificar instrucciones: {str(e)}")
    
    def _verify_source_hierarchy(self):
        """Verifica que la jerarquía de fuentes esté clara"""
        print("\n🔝 Verificando jerarquía de fuentes...")
        
        instructions_file = self.base_path / self.instructions_file
        if not instructions_file.exists():
            return
        
        try:
            with open(instructions_file, 'r', encoding='utf-8') as f:
                instructions = f.read().upper()
            
            hierarchy_levels = [
                "NIVEL 1 - MASTER",
                "NIVEL 2 - VALIDACIÓN",
                "NIVEL 3 - DINÁMICO",
                "NIVEL 4 - SOPORTE"
            ]
            
            for level in hierarchy_levels:
                if level in instructions:
                    self._add_result("PASS", f"Jerarquía '{level}' documentada")
                else:
                    self._add_result("WARNING", f"Jerarquía '{level}' no encontrada en instrucciones")
        
        except Exception as e:
            self._add_result("WARNING", f"Error al verificar jerarquía: {str(e)}")
    
    def _verify_business_rules(self):
        """Verifica que las reglas de negocio estén presentes"""
        print("\n💼 Verificando reglas de negocio...")
        
        master_file = self._find_file("BMC_Base_Conocimiento_GPT.json")
        if not master_file:
            return
        
        try:
            with open(master_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "reglas_negocio" not in data:
                self._add_result("FAIL", "Sección 'reglas_negocio' no encontrada")
                return
            
            rules = data["reglas_negocio"]
            required_rules = ["iva", "moneda", "pendiente_minima_techo"]
            
            for rule_name in required_rules:
                if rule_name in rules:
                    value = rules[rule_name]
                    self._add_result("PASS", f"Regla '{rule_name}' presente",
                                   [f"Valor: {value}"])
                else:
                    self._add_result("FAIL", f"Regla '{rule_name}' FALTANTE")
            
            # Verificar IVA específicamente
            if "iva" in rules:
                iva_value = rules["iva"]
                if isinstance(iva_value, (int, float)) and 0.20 <= iva_value <= 0.25:
                    self._add_result("PASS", f"IVA tiene valor razonable: {iva_value}")
                else:
                    self._add_result("WARNING", f"IVA tiene valor inusual: {iva_value}")
        
        except Exception as e:
            self._add_result("FAIL", f"Error al verificar reglas de negocio: {str(e)}")
    
    def _find_file(self, filename: str) -> Path:
        """Busca un archivo en el directorio base y subdirectorios"""
        # Buscar en directorio base
        filepath = self.base_path / filename
        if filepath.exists():
            return filepath
        
        # Buscar en subdirectorios comunes (incluyendo "Files " con espacio)
        for subdir in ["Files", "Files ", "files", "."]:
            alt_path = self.base_path / subdir.strip() / filename
            if alt_path.exists():
                return alt_path
        
        # Buscar recursivamente en todos los subdirectorios
        for root, dirs, files in os.walk(self.base_path):
            if filename in files:
                return Path(root) / filename
        
        return None
    
    def _add_result(self, status: str, message: str, details: List[str] = None):
        """Agrega un resultado de verificación"""
        self.results.append(VerificationResult(
            check_name=message,
            status=status,
            message=message,
            details=details or []
        ))
    
    def print_report(self):
        """Imprime un reporte de verificación"""
        print("\n" + "="*70)
        print("📊 REPORTE DE VERIFICACIÓN")
        print("="*70 + "\n")
        
        # Contar resultados
        pass_count = sum(1 for r in self.results if r.status == "PASS")
        fail_count = sum(1 for r in self.results if r.status == "FAIL")
        warn_count = sum(1 for r in self.results if r.status == "WARNING")
        
        print(f"✅ PASS: {pass_count}")
        print(f"❌ FAIL: {fail_count}")
        print(f"⚠️  WARNING: {warn_count}")
        print(f"📊 TOTAL: {len(self.results)}\n")
        
        # Agrupar por status
        fails = [r for r in self.results if r.status == "FAIL"]
        warnings = [r for r in self.results if r.status == "WARNING"]
        passes = [r for r in self.results if r.status == "PASS"]
        
        if fails:
            print("❌ ERRORES CRÍTICOS:")
            print("-" * 70)
            for result in fails:
                print(f"  • {result.message}")
                if result.details:
                    for detail in result.details:
                        print(f"    - {detail}")
            print()
        
        if warnings:
            print("⚠️  ADVERTENCIAS:")
            print("-" * 70)
            for result in warnings:
                print(f"  • {result.message}")
                if result.details:
                    for detail in result.details:
                        print(f"    - {detail}")
            print()
        
        if passes:
            print("✅ VERIFICACIONES EXITOSAS:")
            print("-" * 70)
            for result in passes[:10]:  # Mostrar solo las primeras 10
                print(f"  ✓ {result.message}")
            if len(passes) > 10:
                print(f"  ... y {len(passes) - 10} más")
            print()
        
        # Resumen final
        print("="*70)
        if fail_count == 0:
            if warn_count == 0:
                print("🎉 ¡CONFIGURACIÓN PERFECTA! Todos los checks pasaron.")
            else:
                print("✅ Configuración válida con algunas advertencias menores.")
        else:
            print("⚠️  Configuración tiene errores que deben corregirse.")
        print("="*70)


def main():
    """Función principal"""
    # Determinar directorio base
    script_dir = Path(__file__).parent
    base_path = script_dir
    
    verifier = GPTConfigurationVerifier(base_path=str(base_path))
    results = verifier.verify_all()
    verifier.print_report()
    
    # Exit code basado en resultados
    fail_count = sum(1 for r in results if r.status == "FAIL")
    sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    main()
