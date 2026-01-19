#!/usr/bin/env python3
"""
Validador JSON para Training Bundle
===================================

Valida bundles de entrenamiento contra el schema JSON Schema.
Incluye validación de schema, mapeo de roles y cálculo de KPIs.

Uso:
    python bundle_validator.py bundle.json
    python bundle_validator.py bundle.json --fix-roles
    python bundle_validator.py bundle.json --full-report
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import jsonschema
from jsonschema import validate, ValidationError

# Importar módulos locales
try:
    from role_mapper import RoleMapper
    from kpi_calculator import KPICalculator
except ImportError:
    print("⚠️  Advertencia: No se encontraron role_mapper.py o kpi_calculator.py")
    print("   Asegúrate de que estén en el mismo directorio.")
    RoleMapper = None
    KPICalculator = None


class BundleValidator:
    """Validador completo para bundles de entrenamiento."""
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Inicializa el validador.
        
        Args:
            schema_path: Ruta al archivo schema JSON. Si None, busca en el mismo directorio.
        """
        if schema_path is None:
            schema_path = Path(__file__).parent / 'training_bundle_schema.json'
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)
        
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate_schema(self, bundle: Dict) -> bool:
        """
        Valida el bundle contra el schema JSON Schema.
        
        Args:
            bundle: Bundle a validar
            
        Returns:
            True si es válido, False si hay errores
        """
        try:
            validate(instance=bundle, schema=self.schema)
            self.info.append("✅ Schema válido")
            return True
        except ValidationError as e:
            self.errors.append({
                'type': 'schema_validation',
                'path': '/'.join(str(p) for p in e.path),
                'message': e.message,
                'severity': 'error'
            })
            return False
        except Exception as e:
            self.errors.append({
                'type': 'schema_error',
                'message': str(e),
                'severity': 'error'
            })
            return False
    
    def validate_structure(self, bundle: Dict) -> bool:
        """
        Valida la estructura básica del bundle.
        
        Args:
            bundle: Bundle a validar
            
        Returns:
            True si la estructura es válida
        """
        is_valid = True
        
        # Validar campos requeridos
        required_fields = ['meta', 'instructions', 'conversations']
        for field in required_fields:
            if field not in bundle:
                self.errors.append({
                    'type': 'missing_field',
                    'field': field,
                    'message': f"Campo requerido '{field}' no encontrado",
                    'severity': 'error'
                })
                is_valid = False
        
        # Validar meta
        if 'meta' in bundle:
            meta = bundle['meta']
            required_meta = ['version', 'created_at', 'training_type', 'locale']
            for field in required_meta:
                if field not in meta:
                    self.errors.append({
                        'type': 'missing_meta_field',
                        'field': f'meta.{field}',
                        'message': f"Campo requerido 'meta.{field}' no encontrado",
                        'severity': 'error'
                    })
                    is_valid = False
        
        # Validar conversations
        if 'conversations' in bundle:
            conversations = bundle['conversations']
            if not isinstance(conversations, list):
                self.errors.append({
                    'type': 'invalid_type',
                    'field': 'conversations',
                    'message': "'conversations' debe ser una lista",
                    'severity': 'error'
                })
                is_valid = False
            elif len(conversations) == 0:
                self.warnings.append({
                    'type': 'empty_conversations',
                    'message': "No hay conversaciones en el bundle",
                    'severity': 'warning'
                })
            else:
                # Validar cada conversación
                for i, conv in enumerate(conversations):
                    if not isinstance(conv, dict):
                        self.errors.append({
                            'type': 'invalid_conversation',
                            'index': i,
                            'message': f"Conversación {i} no es un objeto válido",
                            'severity': 'error'
                        })
                        is_valid = False
                    elif 'id' not in conv:
                        self.errors.append({
                            'type': 'missing_conversation_id',
                            'index': i,
                            'message': f"Conversación {i} no tiene 'id'",
                            'severity': 'error'
                        })
                        is_valid = False
                    elif 'messages' not in conv:
                        self.errors.append({
                            'type': 'missing_messages',
                            'index': i,
                            'conversation_id': conv.get('id', 'unknown'),
                            'message': f"Conversación {conv.get('id', i)} no tiene 'messages'",
                            'severity': 'error'
                        })
                        is_valid = False
        
        return is_valid
    
    def validate_roles(self, bundle: Dict) -> bool:
        """
        Valida el mapeo de roles en las conversaciones.
        
        Args:
            bundle: Bundle a validar
            
        Returns:
            True si los roles son válidos
        """
        if RoleMapper is None:
            self.warnings.append({
                'type': 'role_mapper_unavailable',
                'message': "RoleMapper no disponible, saltando validación de roles"
            })
            return True
        
        is_valid = True
        conversations = bundle.get('conversations', [])
        
        for conv in conversations:
            messages = conv.get('messages', [])
            previous_role = None
            
            for i, msg in enumerate(messages):
                role = msg.get('role', '').lower()
                
                # Validar que el rol sea válido
                if role not in ['user', 'assistant', 'system']:
                    self.errors.append({
                        'type': 'invalid_role',
                        'conversation_id': conv.get('id', 'unknown'),
                        'message_index': i,
                        'role': role,
                        'message': f"Rol inválido '{role}' en mensaje {i}",
                        'severity': 'error'
                    })
                    is_valid = False
                
                # Validar alternancia (excepto system)
                if role in ['user', 'assistant']:
                    if previous_role and previous_role == role:
                        self.warnings.append({
                            'type': 'role_alternation',
                            'conversation_id': conv.get('id', 'unknown'),
                            'message_index': i,
                            'message': f"Rol '{role}' se repite después de '{previous_role}'",
                            'severity': 'warning'
                        })
                    previous_role = role
        
        return is_valid
    
    def validate_all(self, bundle: Dict, fix_roles: bool = False) -> Dict:
        """
        Ejecuta todas las validaciones.
        
        Args:
            bundle: Bundle a validar
            fix_roles: Si True, intenta corregir roles automáticamente
            
        Returns:
            Reporte de validación completo
        """
        self.errors = []
        self.warnings = []
        self.info = []
        
        # 1. Validar estructura
        structure_valid = self.validate_structure(bundle)
        
        # 2. Validar schema JSON Schema
        schema_valid = False
        if structure_valid:
            schema_valid = self.validate_schema(bundle)
        
        # 3. Validar roles
        roles_valid = False
        if structure_valid:
            if fix_roles and RoleMapper:
                # Mapear roles automáticamente
                mapper = RoleMapper(strict_mode=True)
                bundle = mapper.map_bundle(bundle)
                self.info.append("✅ Roles mapeados automáticamente")
                roles_valid = True
            else:
                roles_valid = self.validate_roles(bundle)
        
        # 4. Calcular KPIs si está disponible
        kpis = None
        if KPICalculator:
            try:
                calculator = KPICalculator()
                kpis = calculator.calculate_all(bundle)
                self.info.append("✅ KPIs calculados")
            except Exception as e:
                self.warnings.append({
                    'type': 'kpi_calculation_error',
                    'message': f"Error calculando KPIs: {str(e)}",
                    'severity': 'warning'
                })
        
        # Determinar validez general
        is_valid = structure_valid and schema_valid and roles_valid and len(self.errors) == 0
        
        return {
            'valid': is_valid,
            'structure_valid': structure_valid,
            'schema_valid': schema_valid,
            'roles_valid': roles_valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'kpis': kpis,
            'summary': {
                'total_errors': len(self.errors),
                'total_warnings': len(self.warnings),
                'total_info': len(self.info)
            }
        }
    
    def print_report(self, report: Dict, format: str = 'human'):
        """
        Imprime el reporte de validación.
        
        Args:
            report: Reporte de validación
            format: 'human' o 'json'
        """
        if format == 'json':
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            # Formato humano
            print("\n" + "="*60)
            print("REPORTE DE VALIDACIÓN - TRAINING BUNDLE")
            print("="*60)
            
            # Estado general
            status = "✅ VÁLIDO" if report['valid'] else "❌ INVÁLIDO"
            print(f"\nEstado: {status}")
            
            # Resumen
            summary = report['summary']
            print(f"\n📊 Resumen:")
            print(f"   - Errores: {summary['total_errors']}")
            print(f"   - Advertencias: {summary['total_warnings']}")
            print(f"   - Info: {summary['total_info']}")
            
            # Validaciones específicas
            print(f"\n🔍 Validaciones:")
            print(f"   - Estructura: {'✅' if report['structure_valid'] else '❌'}")
            print(f"   - Schema JSON: {'✅' if report['schema_valid'] else '❌'}")
            print(f"   - Roles: {'✅' if report['roles_valid'] else '❌'}")
            
            # Errores
            if report['errors']:
                print(f"\n❌ Errores ({len(report['errors'])}):")
                for error in report['errors'][:10]:  # Mostrar primeros 10
                    print(f"   - [{error.get('type', 'unknown')}] {error.get('message', '')}")
                if len(report['errors']) > 10:
                    print(f"   ... y {len(report['errors']) - 10} más")
            
            # Advertencias
            if report['warnings']:
                print(f"\n⚠️  Advertencias ({len(report['warnings'])}):")
                for warning in report['warnings'][:10]:  # Mostrar primeros 10
                    print(f"   - [{warning.get('type', 'unknown')}] {warning.get('message', '')}")
                if len(report['warnings']) > 10:
                    print(f"   ... y {len(report['warnings']) - 10} más")
            
            # Info
            if report['info']:
                print(f"\nℹ️  Información:")
                for info in report['info']:
                    print(f"   - {info}")
            
            # KPIs (si están disponibles)
            if report.get('kpis'):
                kpis = report['kpis']
                exec_summary = kpis.get('kpis', {}).get('executive_summary', {})
                if exec_summary:
                    print(f"\n📈 KPIs:")
                    print(f"   - Score General: {exec_summary.get('overall_score', 0)}/100")
                    print(f"   - Nivel: {exec_summary.get('level', 'unknown')}")
            
            print("\n" + "="*60)


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Valida bundles de entrenamiento contra el schema JSON Schema'
    )
    parser.add_argument('input_file', type=str, help='Archivo JSON del bundle a validar')
    parser.add_argument('-s', '--schema', type=str, help='Ruta al schema JSON (opcional)')
    parser.add_argument('--fix-roles', action='store_true', help='Corregir roles automáticamente')
    parser.add_argument('--full-report', action='store_true', help='Incluir KPIs en el reporte')
    parser.add_argument('-o', '--output', type=str, help='Guardar reporte en archivo JSON')
    parser.add_argument('--format', choices=['human', 'json'], default='human', help='Formato de salida')
    
    args = parser.parse_args()
    
    # Leer bundle
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            bundle = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{args.input_file}'")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: JSON inválido en '{args.input_file}': {e}")
        sys.exit(1)
    
    # Validar
    validator = BundleValidator(schema_path=args.schema)
    report = validator.validate_all(bundle, fix_roles=args.fix_roles)
    
    # Si se corrigieron roles, guardar bundle actualizado
    if args.fix_roles and report['roles_valid']:
        output_bundle = args.input_file.replace('.json', '_validated.json')
        with open(output_bundle, 'w', encoding='utf-8') as f:
            json.dump(bundle, f, indent=2, ensure_ascii=False)
        print(f"✅ Bundle con roles corregidos guardado en: {output_bundle}")
    
    # Mostrar reporte
    validator.print_report(report, format=args.format)
    
    # Guardar reporte si se solicita
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Reporte guardado en: {args.output}")
    
    # Exit code basado en validez
    sys.exit(0 if report['valid'] else 1)


if __name__ == '__main__':
    main()
