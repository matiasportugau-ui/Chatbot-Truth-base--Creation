#!/usr/bin/env python3
"""
Ejemplo rápido de uso del AI Project Files Organizer Agent
Ejecuta este script para ver cómo funciona el agente
"""

import tempfile
from pathlib import Path
from ai_files_organizer import FileOrganizerAgent

def ejemplo_rapido():
    """Ejemplo rápido con un proyecto temporal"""
    
    # Crear un proyecto temporal de ejemplo
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        
        print("📁 Creando proyecto de ejemplo...")
        
        # Crear algunos archivos de ejemplo
        (workspace / "documento.md").write_text("# Documentación")
        (workspace / "script.py").write_text("print('Hola')")
        (workspace / "config.json").write_text('{"key": "value"}')
        (workspace / "README.txt").write_text("Este es un README")
        
        print(f"✅ Proyecto creado en: {workspace}")
        print(f"   Archivos creados: documento.md, script.py, config.json, README.txt\n")
        
        # Inicializar el agente
        print("🚀 Inicializando FileOrganizerAgent...")
        organizer = FileOrganizerAgent(
            workspace_path=str(workspace),
            require_approval=False  # Sin aprobación para el ejemplo
        )
        print("✅ Agente inicializado\n")
        
        # Escanear archivos
        print("📊 Escaneando archivos...")
        files = organizer.scanner.scan()
        print(f"   Encontrados {len(files)} archivos\n")
        
        # Obtener propuestas de organización
        print("💡 Generando propuestas de organización...")
        proposals = organizer.folder_engine.generate_batch_proposals(
            files, organizer.workspace_path
        )
        print(f"   {len(proposals)} propuestas generadas\n")
        
        # Mostrar propuestas
        print("📋 Propuestas de organización:")
        for i, proposal in enumerate(proposals, 1):
            file_name = Path(proposal['file']).name
            target = proposal['proposed_location']
            print(f"   {i}. {file_name} → {target}")
        
        # Obtener estadísticas
        print("\n📊 Estadísticas:")
        stats = organizer.get_statistics()
        print(f"   Total operaciones: {stats['total_operations']}")
        print(f"   Archivos organizados: {stats['total_files_organized']}")
        
        # Sugerir ubicación para un archivo nuevo
        print("\n💭 Sugiriendo ubicación para archivo nuevo...")
        proposal = organizer.suggest_new_file_location(str(workspace / "nuevo_doc.md"))
        if "error" not in proposal:
            print(f"   Archivo: nuevo_doc.md")
            print(f"   Ubicación sugerida: {proposal['proposed_location']}")
            print(f"   Nombre sugerido: {proposal['proposed_name']}")
        
        print("\n✅ Ejemplo completado!")
        print("\n💡 Para usar con tu proyecto real:")
        print("   organizer = FileOrganizerAgent(workspace_path='/ruta/a/tu/proyecto')")
        print("   result = organizer.organize_existing_files()")

if __name__ == "__main__":
    ejemplo_rapido()
