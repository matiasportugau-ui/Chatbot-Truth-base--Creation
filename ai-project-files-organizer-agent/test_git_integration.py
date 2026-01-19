#!/usr/bin/env python3
"""
Script para probar la integración Git con stage_and_commit_changes()
"""

import tempfile
import subprocess
from pathlib import Path
from ai_files_organizer import FileOrganizerAgent

# Crear un workspace temporal
with tempfile.TemporaryDirectory() as tmpdir:
    workspace = Path(tmpdir)
    
    # Inicializar un repositorio Git
    print("=== Inicializando repositorio Git ===")
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
    
    # Crear algunos archivos de prueba
    print("\n=== Creando archivos de prueba ===")
    test_file1 = workspace / "test1.md"
    test_file2 = workspace / "test2.py"
    test_file1.write_text("# Test File 1")
    test_file2.write_text("print('test')")
    
    print(f"Creados: {test_file1.name}, {test_file2.name}")
    
    # Inicializar el agente
    print("\n=== Inicializando FileOrganizerAgent ===")
    agent = FileOrganizerAgent(
        workspace_path=str(workspace),
        require_approval=False  # Desactivar aprobación para pruebas
    )
    
    if not agent.git_manager:
        print("❌ GitManager no inicializado")
    else:
        print("✅ GitManager inicializado correctamente")
        
        # Analizar estado del repositorio
        print("\n=== Estado del repositorio ===")
        state = agent.git_manager.analyze_repository_state()
        print(f"Branch: {state['branch']}")
        print(f"Archivos modificados: {len(state['modified_files'])}")
        print(f"Archivos sin seguimiento: {len(state['untracked_files'])}")
        
        # Probar stage_and_commit_changes
        print("\n=== Probando stage_and_commit_changes() ===")
        files_to_stage = ["test1.md", "test2.py"]
        commit_message = "test(organizer): prueba de integración Git"
        
        result = agent.stage_and_commit_changes(
            files=files_to_stage,
            message=commit_message,
            interactive=False,  # No interactivo para pruebas
            auto_push=False
        )
        
        print(f"\nResultado:")
        print(f"  Success: {result.get('success')}")
        
        if result.get('success'):
            print("✅ Stage y commit exitosos")
            if 'results' in result:
                if 'stage' in result['results']:
                    print(f"  Stage: {result['results']['stage'].get('message')}")
                if 'commit' in result['results']:
                    print(f"  Commit: {result['results']['commit'].get('message')}")
        else:
            print(f"❌ Error: {result.get('error', result.get('message', 'Unknown error'))}")
        
        # Verificar el estado después del commit
        print("\n=== Estado después del commit ===")
        state_after = agent.git_manager.analyze_repository_state()
        print(f"Branch: {state_after['branch']}")
        print(f"Archivos modificados: {len(state_after['modified_files'])}")
        print(f"Archivos staged: {len(state_after['staged_files'])}")
        print(f"Repositorio limpio: {state_after['is_clean']}")
    
    print("\n✅ Prueba de integración Git completada")
