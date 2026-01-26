#!/usr/bin/env python3
"""
Script CLI para aplicar correcciones al GPT
============================================

Uso:
    python apply_corrections.py --file correcciones.json
    python apply_corrections.py --interactive
    python apply_corrections.py --validate
"""

import argparse
import json
import sys
from pathlib import Path
from correction_agent import GPTCorrectionAgent
from loguru import logger

def load_corrections_from_file(file_path: Path) -> list:
    """Carga correcciones desde un archivo JSON."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "corrections" in data:
        return data["corrections"]
    else:
        return [data]


def interactive_mode(agent: GPTCorrectionAgent):
    """Modo interactivo para aplicar correcciones."""
    print("=" * 60)
    print("GPT Correction Agent - Modo Interactivo")
    print("=" * 60)
    print()
    
    print("Tipos de corrección disponibles:")
    print("  1. institucional")
    print("  2. producto")
    print("  3. precio")
    print("  4. formula")
    print("  5. catalogo")
    print("  6. capabilities")
    print("  7. reglas_negocio")
    print("  8. instrucciones")
    print()
    
    correction_type = input("Tipo de corrección (1-8): ").strip()
    type_map = {
        "1": "institucional",
        "2": "producto",
        "3": "precio",
        "4": "formula",
        "5": "catalogo",
        "6": "capabilities",
        "7": "reglas_negocio",
        "8": "instrucciones"
    }
    
    if correction_type not in type_map:
        print("Tipo inválido")
        return
    
    correction_type = type_map[correction_type]
    correction_id = input("ID de corrección (ej: KB-001): ").strip()
    description = input("Descripción: ").strip()
    priority = input("Prioridad (P0/P1/P2) [P1]: ").strip() or "P1"
    
    print("\nIngresa los cambios en formato JSON (una línea):")
    print("Ejemplo para precio: {\"product_id\": \"ISODEC_EPS\", \"espesor\": \"100\", \"nuevo_precio\": 47.50}")
    changes_input = input("Cambios: ").strip()
    
    try:
        changes = json.loads(changes_input)
    except json.JSONDecodeError as e:
        print(f"Error parseando JSON: {e}")
        return
    
    print("\n¿Aplicar corrección? (s/n): ", end="")
    confirm = input().strip().lower()
    
    if confirm != 's':
        print("Cancelado")
        return
    
    result = agent.apply_correction(
        correction_id=correction_id,
        correction_type=correction_type,
        description=description,
        priority=priority,
        changes=changes
    )
    
    print("\n" + "=" * 60)
    if result['success']:
        print("✓ Corrección aplicada exitosamente")
        print(f"Archivos modificados: {len(result['affected_files'])}")
        for file in result['affected_files']:
            print(f"  - {file}")
    else:
        print("✗ Error aplicando corrección")
        for error in result.get('errors', []):
            print(f"  - {error}")
    print("=" * 60)


def validate_mode(agent: GPTCorrectionAgent):
    """Modo de validación de archivos KB."""
    print("=" * 60)
    print("Validación de Archivos KB")
    print("=" * 60)
    print()
    
    kb_file = Path(__file__).parent.parent / "BMC_Base_Conocimiento_GPT-2.json"
    
    if not kb_file.exists():
        print(f"✗ Archivo no encontrado: {kb_file}")
        return
    
    print(f"Validando: {kb_file.name}")
    validation = agent.validate_changes(kb_file)
    
    print()
    if validation['valid']:
        print("✓ Archivo válido")
    else:
        print("✗ Archivo inválido")
        print("\nErrores:")
        for error in validation.get('errors', []):
            print(f"  - {error}")
    
    if validation.get('warnings'):
        print("\nAdvertencias:")
        for warning in validation['warnings']:
            print(f"  - {warning}")


def main():
    parser = argparse.ArgumentParser(
        description="Aplicar correcciones a la base de conocimientos del GPT"
    )
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Archivo JSON con correcciones a aplicar'
    )
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Modo interactivo'
    )
    parser.add_argument(
        '--validate', '-v',
        action='store_true',
        help='Validar archivos KB'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Deshabilitar creación de backups'
    )
    parser.add_argument(
        '--project-root',
        type=str,
        help='Ruta raíz del proyecto'
    )
    
    args = parser.parse_args()
    
    # Inicializar agente
    agent = GPTCorrectionAgent(
        project_root=args.project_root,
        backup_enabled=not args.no_backup
    )
    
    if args.validate:
        validate_mode(agent)
    elif args.interactive:
        interactive_mode(agent)
    elif args.file:
        # Cargar correcciones desde archivo
        corrections_file = Path(args.file)
        if not corrections_file.exists():
            print(f"Error: Archivo no encontrado: {corrections_file}")
            sys.exit(1)
        
        corrections = load_corrections_from_file(corrections_file)
        
        print(f"Cargadas {len(corrections)} corrección(es)")
        print("¿Aplicar todas? (s/n): ", end="")
        confirm = input().strip().lower()
        
        if confirm != 's':
            print("Cancelado")
            sys.exit(0)
        
        if len(corrections) == 1:
            result = agent.apply_correction(**corrections[0])
            if result['success']:
                print("✓ Corrección aplicada exitosamente")
            else:
                print("✗ Error aplicando corrección")
                sys.exit(1)
        else:
            summary = agent.batch_apply_corrections(corrections)
            print(f"\nResumen:")
            print(f"  Total: {summary['total_corrections']}")
            print(f"  Exitosas: {summary['successful']}")
            print(f"  Fallidas: {summary['failed']}")
            
            if summary['failed'] > 0:
                sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
