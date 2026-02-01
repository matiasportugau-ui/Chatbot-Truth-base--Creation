#!/usr/bin/env python3
"""
Script para aplicar las correcciones pendientes de ejemplo_correcciones.json
"""

import json
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gpt_kb_config_agent.correction_agent import GPTCorrectionAgent


def main():
    # Initialize the correction agent
    agent = GPTCorrectionAgent(
        project_root=str(project_root),
        backup_enabled=True
    )
    
    # Load the pending corrections
    corrections_file = project_root / "docs" / "corrections" / "ejemplo_correcciones.json"
    with open(corrections_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    corrections = data['corrections']
    
    print(f"🔧 Aplicando {len(corrections)} correcciones pendientes...\n")
    
    # Apply each correction
    results = []
    for correction in corrections:
        print(f"📝 Aplicando {correction['correction_id']}: {correction['description']}")
        print(f"   Prioridad: {correction['priority']}")
        
        try:
            result = agent.apply_correction(
                correction_id=correction['correction_id'],
                correction_type=correction['correction_type'],
                description=correction['description'],
                priority=correction['priority'],
                changes=correction['changes']
            )
            
            if result['success']:
                print(f"   ✅ ÉXITO - Archivos afectados: {len(result['affected_files'])}")
            else:
                print(f"   ❌ ERROR - {len(result['errors'])} errores")
                for error in result['errors']:
                    print(f"      - {error}")
            
            results.append(result)
            print()
            
        except Exception as e:
            print(f"   ❌ EXCEPCIÓN: {str(e)}\n")
            results.append({
                'correction_id': correction['correction_id'],
                'success': False,
                'error': str(e)
            })
    
    # Summary
    successful = sum(1 for r in results if r.get('success', False))
    failed = len(results) - successful
    
    print("\n" + "="*60)
    print(f"📊 RESUMEN:")
    print(f"   Total: {len(results)}")
    print(f"   Exitosas: {successful}")
    print(f"   Fallidas: {failed}")
    print("="*60)
    
    if failed == 0:
        print("\n✅ Todas las correcciones se aplicaron exitosamente!")
        return 0
    else:
        print(f"\n⚠️  {failed} correcciones fallaron. Revisar logs para detalles.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
