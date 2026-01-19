#!/usr/bin/env python3
"""
Ejecuta los ejemplos de la guía de uso
Basado en GUIA_USO.md
"""

import tempfile
import subprocess
from pathlib import Path
from ai_files_organizer import FileOrganizerAgent

def ejemplo_1_basico():
    """Ejemplo 1: Uso Básico - Organizar Archivos"""
    print("\n" + "="*60)
    print("EJEMPLO 1: Uso Básico - Organizar Archivos")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        
        # Crear archivos de ejemplo
        (workspace / "documento.md").write_text("# Documentación del Proyecto")
        (workspace / "script.py").write_text("print('Hola mundo')")
        (workspace / "config.json").write_text('{"version": "1.0"}')
        (workspace / "README.txt").write_text("Este es un README")
        
        print(f"\n📁 Proyecto temporal creado en: {workspace}")
        print("   Archivos creados: documento.md, script.py, config.json, README.txt")
        
        # Inicializar el agente
        organizer = FileOrganizerAgent(
            workspace_path=str(workspace),
            require_approval=False  # Sin aprobación para el ejemplo
        )
        
        # Organizar archivos existentes
        result = organizer.organize_existing_files(interactive=False)
        
        if result.get("success"):
            successful = result['results']['successful']
            failed = result['results']['failed']
            print(f"\n✅ Organizados {len(successful)} archivos")
            print(f"❌ Fallaron {len(failed)} archivos")
            
            if successful:
                print("\n📋 Archivos organizados:")
                for item in successful[:3]:  # Mostrar primeros 3
                    print(f"   - {Path(item['file']).name} → {Path(item['new_location']).name}")
        else:
            print("❌ La organización no fue aprobada")


def ejemplo_2_sugerir_ubicacion():
    """Ejemplo 2: Sugerir Ubicación para un Archivo Nuevo"""
    print("\n" + "="*60)
    print("EJEMPLO 2: Sugerir Ubicación para un Archivo Nuevo")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        
        organizer = FileOrganizerAgent(workspace_path=str(workspace))
        
        # Sugerir dónde debería ir un archivo nuevo
        proposal = organizer.suggest_new_file_location(str(workspace / "mi_documento.md"))
        
        if "error" not in proposal:
            print(f"\n📁 Ubicación sugerida: {proposal['proposed_location']}")
            print(f"📝 Nombre sugerido: {proposal['proposed_name']}")
            print(f"📂 Categoría: {proposal.get('category', 'N/A')}")
        else:
            print(f"❌ Error: {proposal['error']}")


def ejemplo_3_detectar_obsoletos():
    """Ejemplo 3: Detectar Archivos Obsoletos"""
    print("\n" + "="*60)
    print("EJEMPLO 3: Detectar Archivos Obsoletos")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        
        # Crear archivos de ejemplo
        (workspace / "nuevo.py").write_text("# Archivo nuevo")
        (workspace / "viejo.py").write_text("# Archivo viejo")
        
        organizer = FileOrganizerAgent(workspace_path=str(workspace))
        
        # Detectar archivos obsoletos
        outdated = organizer.detect_outdated_files()
        
        print(f"\n⚠️  Encontrados {len(outdated)} archivos obsoletos:")
        if outdated:
            for file_info in outdated[:5]:  # Mostrar primeros 5
                print(f"  - {Path(file_info['file']).name}: {file_info.get('reason', 'Sin razón especificada')}")
        else:
            print("  ✅ No se encontraron archivos obsoletos (normal en proyecto nuevo)")


def ejemplo_4_git_integracion():
    """Ejemplo 4: Integración con Git"""
    print("\n" + "="*60)
    print("EJEMPLO 4: Integración con Git")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        
        # Inicializar Git
        try:
            subprocess.run(["git", "init"], cwd=workspace, check=True, capture_output=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=workspace,
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=workspace,
                check=True,
                capture_output=True
            )
            print(f"\n📁 Repositorio Git inicializado en: {workspace}")
        except Exception as e:
            print(f"⚠️  No se pudo inicializar Git: {e}")
            return
        
        # Crear archivos
        (workspace / "test1.md").write_text("# Test 1")
        (workspace / "test2.py").write_text("print('test')")
        
        organizer = FileOrganizerAgent(
            workspace_path=str(workspace),
            require_approval=False
        )
        
        # Verificar si hay Git manager
        if organizer.git_manager:
            print("✅ GitManager detectado")
            
            # Probar stage_and_commit_changes
            files_to_stage = ["test1.md", "test2.py"]
            commit_message = "test(organizer): prueba de integración Git"
            
            print(f"\n🔄 Haciendo stage y commit de {len(files_to_stage)} archivos...")
            git_result = organizer.stage_and_commit_changes(
                files=files_to_stage,
                message=commit_message,
                interactive=False,
                auto_push=False
            )
            
            if git_result.get("success"):
                print("✅ Cambios commiteados exitosamente")
                if 'results' in git_result:
                    if 'stage' in git_result['results']:
                        print(f"   Stage: {git_result['results']['stage'].get('message')}")
                    if 'commit' in git_result['results']:
                        print(f"   Commit: {git_result['results']['commit'].get('message')}")
            else:
                print(f"❌ Error en Git: {git_result.get('error', git_result.get('message', 'Unknown'))}")
        else:
            print("⚠️  No se detectó un repositorio Git")


def ejemplo_6_estadisticas():
    """Ejemplo 6: Obtener Estadísticas"""
    print("\n" + "="*60)
    print("EJEMPLO 6: Obtener Estadísticas")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        
        # Crear archivos
        (workspace / "doc1.md").write_text("# Doc 1")
        (workspace / "doc2.md").write_text("# Doc 2")
        (workspace / "script1.py").write_text("print('1')")
        
        organizer = FileOrganizerAgent(workspace_path=str(workspace))
        
        # Realizar algunas operaciones
        print("\n🔄 Realizando operaciones...")
        organizer.organize_existing_files(interactive=False)
        
        # Obtener estadísticas
        stats = organizer.get_statistics()
        
        print("\n📊 Estadísticas del Agente:")
        print(f"  Total de operaciones: {stats['total_operations']}")
        print(f"  Operaciones completadas: {stats['completed_operations']}")
        print(f"  Archivos organizados: {stats['total_files_organized']}")
        print(f"  Aprobaciones solicitadas: {stats['total_approvals_requested']}")
        print(f"  Aprobaciones concedidas: {stats['total_approvals_granted']}")
        print(f"  Aprobaciones rechazadas: {stats['total_approvals_rejected']}")
        print(f"  Tasa de aprobación: {stats['approval_rate']:.2%}")
        print(f"  Duración total: {stats['total_duration_seconds']:.2f} segundos")
        if stats['completed_operations'] > 0:
            print(f"  Duración promedio: {stats['average_duration_seconds']:.2f} segundos")


def main():
    """Ejecutar todos los ejemplos"""
    print("\n" + "🚀"*30)
    print("EJECUTANDO EJEMPLOS DE LA GUÍA DE USO")
    print("🚀"*30)
    
    try:
        ejemplo_1_basico()
        ejemplo_2_sugerir_ubicacion()
        ejemplo_3_detectar_obsoletos()
        ejemplo_4_git_integracion()
        ejemplo_6_estadisticas()
        
        print("\n" + "="*60)
        print("✅ TODOS LOS EJEMPLOS COMPLETADOS")
        print("="*60)
        print("\n💡 Próximos pasos:")
        print("   1. Revisa GUIA_USO.md para más detalles")
        print("   2. Prueba con tu propio proyecto:")
        print("      organizer = FileOrganizerAgent(workspace_path='/ruta/a/tu/proyecto')")
        print("      result = organizer.organize_existing_files()")
        print("   3. Usa el CLI: files-organizer scan /ruta/a/tu/proyecto")
        
    except Exception as e:
        print(f"\n❌ Error ejecutando ejemplos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
