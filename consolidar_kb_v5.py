#!/usr/bin/env python3
"""
Knowledge Base Consolidation - Version 5.0

Consolidates all knowledge base files into a unified, optimized structure.

Features:
- Merges multiple KB files while preserving hierarchy
- Deduplicates information
- Validates data integrity
- Creates backup of current KB
- Generates migration report

Usage:
    python consolidar_kb_v5.py --backup --validate
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import json
import shutil
from typing import Dict, Any, List, Set
from collections import defaultdict


class KnowledgeBaseConsolidator:
    """Consolidate knowledge base to v5.0"""
    
    def __init__(self, project_root: str, backup: bool = True):
        """
        Initialize consolidator
        
        Args:
            project_root: Root directory of the project
            backup: Whether to create backup before consolidation
        """
        self.project_root = Path(project_root)
        self.backup_enabled = backup
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # KB file paths
        self.kb_files = self._discover_kb_files()
        
        # Consolidated data structure
        self.consolidated_kb = {
            "metadata": {
                "version": "5.0",
                "created_at": datetime.now().isoformat(),
                "source_files": [],
                "consolidation_method": "automated_merge_v5"
            },
            "identity": {},
            "products": {},
            "formulas": {},
            "business_rules": {},
            "instructions": {},
            "catalog": {},
            "hierarchies": {
                "nivel_1_master": [],
                "nivel_2_derivado": [],
                "nivel_3_documentacion": [],
                "nivel_4_soporte": []
            },
            "validation": {}
        }
    
    def _discover_kb_files(self) -> List[Path]:
        """Discover all KB-related files in the project"""
        kb_files = []
        
        # Known KB file patterns
        patterns = [
            "BMC_Base_Conocimiento*.json",
            "BMC_Base_Unificada*.json",
            "panelin_truth*.json",
            "BMC_Catalogo*.json",
            "*_config.json",
        ]
        
        for pattern in patterns:
            kb_files.extend(self.project_root.glob(pattern))
        
        # Also check gpt_configs directory
        gpt_configs = self.project_root / "gpt_configs"
        if gpt_configs.exists():
            kb_files.extend(gpt_configs.glob("*.json"))
        
        return sorted(set(kb_files))
    
    def create_backup(self) -> Path:
        """Create backup of current KB files"""
        backup_dir = self.project_root / ".kb_backups" / f"backup_{self.timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📦 Creando backup en: {backup_dir}")
        
        for kb_file in self.kb_files:
            if kb_file.exists():
                dest = backup_dir / kb_file.name
                shutil.copy2(kb_file, dest)
                print(f"  ✓ {kb_file.name}")
        
        # Create backup manifest
        manifest = {
            "timestamp": self.timestamp,
            "files_backed_up": [f.name for f in self.kb_files],
            "total_files": len(self.kb_files)
        }
        
        with open(backup_dir / "manifest.json", 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Backup creado: {len(self.kb_files)} archivos")
        return backup_dir
    
    def _merge_identity(self, source_data: Dict) -> None:
        """Merge identity information"""
        identity_fields = [
            'nombre_bot', 'name', 'rol', 'role', 'tono', 'tone',
            'objetivo', 'objective', 'personalidad', 'personality'
        ]
        
        for field in identity_fields:
            if field in source_data and source_data[field]:
                # Normalize field name
                normalized_field = field
                if field in ['nombre_bot', 'name']:
                    normalized_field = 'name'
                elif field in ['rol', 'role']:
                    normalized_field = 'role'
                elif field in ['tono', 'tone']:
                    normalized_field = 'tone'
                elif field in ['objetivo', 'objective']:
                    normalized_field = 'objective'
                elif field in ['personalidad', 'personality']:
                    normalized_field = 'personality'
                
                # Keep most detailed version
                if normalized_field not in self.consolidated_kb['identity']:
                    self.consolidated_kb['identity'][normalized_field] = source_data[field]
                elif len(str(source_data[field])) > len(str(self.consolidated_kb['identity'][normalized_field])):
                    self.consolidated_kb['identity'][normalized_field] = source_data[field]
    
    def _merge_products(self, source_data: Dict) -> None:
        """Merge product information"""
        if 'productos' in source_data:
            products = source_data['productos']
        elif 'products' in source_data:
            products = source_data['products']
        else:
            return
        
        for product_id, product_data in products.items():
            if product_id not in self.consolidated_kb['products']:
                self.consolidated_kb['products'][product_id] = product_data
            else:
                # Merge product data (keep most complete)
                existing = self.consolidated_kb['products'][product_id]
                if isinstance(product_data, dict):
                    for key, value in product_data.items():
                        if key not in existing or not existing[key]:
                            existing[key] = value
    
    def _merge_formulas(self, source_data: Dict) -> None:
        """Merge formula information"""
        if 'formulas' in source_data:
            formulas = source_data['formulas']
        elif 'fórmulas' in source_data:
            formulas = source_data['fórmulas']
        else:
            return
        
        for formula_id, formula_data in formulas.items():
            if formula_id not in self.consolidated_kb['formulas']:
                self.consolidated_kb['formulas'][formula_id] = formula_data
    
    def _merge_business_rules(self, source_data: Dict) -> None:
        """Merge business rules"""
        if 'reglas_negocio' in source_data:
            rules = source_data['reglas_negocio']
        elif 'business_rules' in source_data:
            rules = source_data['business_rules']
        else:
            return
        
        for rule_id, rule_data in rules.items():
            if rule_id not in self.consolidated_kb['business_rules']:
                self.consolidated_kb['business_rules'][rule_id] = rule_data
    
    def _classify_file_hierarchy(self, file_path: Path, data: Dict) -> str:
        """Classify file into hierarchy level"""
        file_name = file_path.name.lower()
        
        # Level 1 (Master) - Source of Truth
        if any(pattern in file_name for pattern in [
            'base_conocimiento_gpt',
            'base_unificada',
            'master',
            'truth_base'
        ]):
            return 'nivel_1_master'
        
        # Level 2 (Derived) - Validated derivatives
        if any(pattern in file_name for pattern in [
            'truth_',
            '_v2',
            '_validated',
            'derivado'
        ]):
            return 'nivel_2_derivado'
        
        # Level 3 (Documentation) - Supporting docs
        if any(pattern in file_name for pattern in [
            'catalogo',
            'catalog',
            'guide',
            'guia',
            'index'
        ]):
            return 'nivel_3_documentacion'
        
        # Level 4 (Support) - Config and support
        if any(pattern in file_name for pattern in [
            'config',
            'settings',
            'setup'
        ]):
            return 'nivel_4_soporte'
        
        return 'nivel_3_documentacion'  # Default
    
    def consolidate(self) -> Dict[str, Any]:
        """Perform KB consolidation"""
        print("\n" + "=" * 70)
        print("CONSOLIDACIÓN DE KNOWLEDGE BASE - VERSION 5.0")
        print("=" * 70)
        
        # Create backup if enabled
        if self.backup_enabled:
            backup_dir = self.create_backup()
        
        print(f"\n📊 Procesando {len(self.kb_files)} archivos...")
        
        stats = {
            "files_processed": 0,
            "files_skipped": 0,
            "products_merged": 0,
            "formulas_merged": 0,
            "rules_merged": 0,
            "duplicates_found": 0
        }
        
        for kb_file in self.kb_files:
            try:
                print(f"\n  📄 Procesando: {kb_file.name}")
                
                with open(kb_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Add to source files
                self.consolidated_kb['metadata']['source_files'].append({
                    "file": kb_file.name,
                    "size": kb_file.stat().st_size,
                    "modified": datetime.fromtimestamp(kb_file.stat().st_mtime).isoformat()
                })
                
                # Classify file
                hierarchy_level = self._classify_file_hierarchy(kb_file, data)
                self.consolidated_kb['hierarchies'][hierarchy_level].append(kb_file.name)
                print(f"    ℹ️  Clasificado como: {hierarchy_level}")
                
                # Merge different sections
                self._merge_identity(data)
                
                products_before = len(self.consolidated_kb['products'])
                self._merge_products(data)
                products_after = len(self.consolidated_kb['products'])
                products_added = products_after - products_before
                stats['products_merged'] += products_added
                if products_added > 0:
                    print(f"    ✓ {products_added} productos agregados")
                
                formulas_before = len(self.consolidated_kb['formulas'])
                self._merge_formulas(data)
                formulas_after = len(self.consolidated_kb['formulas'])
                formulas_added = formulas_after - formulas_before
                stats['formulas_merged'] += formulas_added
                if formulas_added > 0:
                    print(f"    ✓ {formulas_added} fórmulas agregadas")
                
                rules_before = len(self.consolidated_kb['business_rules'])
                self._merge_business_rules(data)
                rules_after = len(self.consolidated_kb['business_rules'])
                rules_added = rules_after - rules_before
                stats['rules_merged'] += rules_added
                if rules_added > 0:
                    print(f"    ✓ {rules_added} reglas agregadas")
                
                stats['files_processed'] += 1
                
            except json.JSONDecodeError as e:
                print(f"    ⚠️  Error de JSON en {kb_file.name}: {e}")
                stats['files_skipped'] += 1
            except Exception as e:
                print(f"    ⚠️  Error procesando {kb_file.name}: {e}")
                stats['files_skipped'] += 1
        
        # Add statistics to metadata
        self.consolidated_kb['metadata']['consolidation_stats'] = stats
        
        print("\n" + "=" * 70)
        print("RESUMEN DE CONSOLIDACIÓN")
        print("=" * 70)
        print(f"\n📊 Estadísticas:")
        print(f"  • Archivos procesados: {stats['files_processed']}")
        print(f"  • Archivos omitidos: {stats['files_skipped']}")
        print(f"  • Productos consolidados: {len(self.consolidated_kb['products'])}")
        print(f"  • Fórmulas consolidadas: {len(self.consolidated_kb['formulas'])}")
        print(f"  • Reglas de negocio: {len(self.consolidated_kb['business_rules'])}")
        
        print(f"\n📁 Jerarquía de fuentes:")
        for level, files in self.consolidated_kb['hierarchies'].items():
            print(f"  • {level}: {len(files)} archivos")
        
        return stats
    
    def validate(self) -> Dict[str, Any]:
        """Validate consolidated KB"""
        print("\n🔍 Validando KB consolidada...")
        
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "checks_passed": 0,
            "checks_failed": 0
        }
        
        # Check 1: Identity information
        if not self.consolidated_kb['identity']:
            validation['errors'].append("No identity information found")
            validation['checks_failed'] += 1
            validation['valid'] = False
        else:
            validation['checks_passed'] += 1
        
        # Check 2: Products
        if not self.consolidated_kb['products']:
            validation['warnings'].append("No products found")
        else:
            validation['checks_passed'] += 1
        
        # Check 3: Formulas
        if not self.consolidated_kb['formulas']:
            validation['warnings'].append("No formulas found")
        else:
            validation['checks_passed'] += 1
        
        # Check 4: Hierarchy levels
        nivel_1 = self.consolidated_kb['hierarchies'].get('nivel_1_master', [])
        if not nivel_1:
            validation['errors'].append("No Level 1 (Master) sources identified")
            validation['checks_failed'] += 1
            validation['valid'] = False
        else:
            validation['checks_passed'] += 1
        
        # Check 5: Source files
        if not self.consolidated_kb['metadata']['source_files']:
            validation['errors'].append("No source files recorded")
            validation['checks_failed'] += 1
            validation['valid'] = False
        else:
            validation['checks_passed'] += 1
        
        self.consolidated_kb['validation'] = validation
        
        print(f"  ✓ Validación completada")
        print(f"  • Checks pasados: {validation['checks_passed']}")
        print(f"  • Checks fallidos: {validation['checks_failed']}")
        print(f"  • Warnings: {len(validation['warnings'])}")
        print(f"  • Errors: {len(validation['errors'])}")
        
        if validation['errors']:
            print("\n  ⚠️  Errores encontrados:")
            for error in validation['errors']:
                print(f"    - {error}")
        
        if validation['warnings']:
            print("\n  ℹ️  Advertencias:")
            for warning in validation['warnings']:
                print(f"    - {warning}")
        
        return validation
    
    def save(self, output_path: Path = None) -> Path:
        """Save consolidated KB"""
        if output_path is None:
            output_path = self.project_root / "BMC_Base_Conocimiento_v5.0.json"
        
        print(f"\n💾 Guardando KB consolidada: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.consolidated_kb, f, indent=2, ensure_ascii=False)
        
        file_size = output_path.stat().st_size / 1024  # KB
        print(f"  ✓ Archivo guardado ({file_size:.1f} KB)")
        
        return output_path
    
    def generate_report(self, output_path: Path = None) -> Path:
        """Generate consolidation report"""
        if output_path is None:
            output_path = self.project_root / f"consolidacion_report_{self.timestamp}.md"
        
        stats = self.consolidated_kb['metadata'].get('consolidation_stats', {})
        validation = self.consolidated_kb.get('validation', {})
        
        report = f"""# Reporte de Consolidación KB v5.0
**Fecha:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Resumen Ejecutivo

### Estadísticas de Consolidación
- **Archivos procesados:** {stats.get('files_processed', 0)}
- **Archivos omitidos:** {stats.get('files_skipped', 0)}
- **Productos consolidados:** {len(self.consolidated_kb['products'])}
- **Fórmulas consolidadas:** {len(self.consolidated_kb['formulas'])}
- **Reglas de negocio:** {len(self.consolidated_kb['business_rules'])}

### Validación
- **Estado:** {'✅ VÁLIDA' if validation.get('valid', False) else '❌ INVÁLIDA'}
- **Checks pasados:** {validation.get('checks_passed', 0)}
- **Checks fallidos:** {validation.get('checks_failed', 0)}
- **Warnings:** {len(validation.get('warnings', []))}
- **Errors:** {len(validation.get('errors', []))}

## Jerarquía de Fuentes

### Nivel 1 (Master - Source of Truth):
"""
        
        for file in self.consolidated_kb['hierarchies'].get('nivel_1_master', []):
            report += f"- `{file}`\n"
        
        report += "\n### Nivel 2 (Derivado - Validado):\n"
        for file in self.consolidated_kb['hierarchies'].get('nivel_2_derivado', []):
            report += f"- `{file}`\n"
        
        report += "\n### Nivel 3 (Documentación):\n"
        for file in self.consolidated_kb['hierarchies'].get('nivel_3_documentacion', []):
            report += f"- `{file}`\n"
        
        report += "\n### Nivel 4 (Soporte):\n"
        for file in self.consolidated_kb['hierarchies'].get('nivel_4_soporte', []):
            report += f"- `{file}`\n"
        
        report += f"""
## Archivos Fuente

Total: {len(self.consolidated_kb['metadata']['source_files'])} archivos

"""
        for source in self.consolidated_kb['metadata']['source_files']:
            report += f"- `{source['file']}` ({source['size']} bytes)\n"
        
        if validation.get('errors'):
            report += "\n## ⚠️ Errores de Validación\n\n"
            for error in validation['errors']:
                report += f"- {error}\n"
        
        if validation.get('warnings'):
            report += "\n## ℹ️ Advertencias\n\n"
            for warning in validation['warnings']:
                report += f"- {warning}\n"
        
        report += """
## Próximos Pasos

1. **Revisar KB consolidada:** Verificar manualmente la información clave
2. **Testing:** Ejecutar test suite contra nueva KB
3. **Deployment:** Reemplazar KB actual con v5.0 después de validación
4. **Monitoreo:** Observar métricas de evaluación post-migración

## Backup

"""
        if self.backup_enabled:
            report += f"Backup creado en: `.kb_backups/backup_{self.timestamp}/`\n\n"
            report += "Para restaurar backup si es necesario, consultar documentación.\n"
        else:
            report += "⚠️ No se creó backup. Se recomienda hacer backup manual.\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 Reporte generado: {output_path}")
        
        return output_path


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Consolidate Knowledge Base to v5.0'
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        default=True,
        help='Create backup before consolidation (default: True)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip backup creation'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        default=True,
        help='Validate consolidated KB (default: True)'
    )
    parser.add_argument(
        '--output',
        help='Output path for consolidated KB (default: BMC_Base_Conocimiento_v5.0.json)'
    )
    
    args = parser.parse_args()
    
    # Handle backup flag
    backup = args.backup and not args.no_backup
    
    project_root = Path(__file__).parent
    consolidator = KnowledgeBaseConsolidator(str(project_root), backup=backup)
    
    try:
        # Perform consolidation
        stats = consolidator.consolidate()
        
        # Validate if requested
        if args.validate:
            validation = consolidator.validate()
            if not validation['valid']:
                print("\n⚠️  Advertencia: La KB consolidada tiene errores de validación")
                print("   Revise el reporte antes de usar esta KB.")
        
        # Save consolidated KB
        output_path = Path(args.output) if args.output else None
        kb_path = consolidator.save(output_path)
        
        # Generate report
        report_path = consolidator.generate_report()
        
        print("\n" + "=" * 70)
        print("✅ CONSOLIDACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print(f"\nKB Consolidada: {kb_path}")
        print(f"Reporte: {report_path}")
        if backup:
            print(f"Backup: .kb_backups/backup_{consolidator.timestamp}/")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error durante consolidación: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
