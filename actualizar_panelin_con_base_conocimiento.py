#!/usr/bin/env python3
"""
Actualizar Panelin con Base de Conocimiento
===========================================

Actualiza el asistente Panelin para usar los archivos de Files/ como base de conocimiento.
"""

import os
from openai import OpenAI
from pathlib import Path

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set. Please set it in your .env file.")
ASSISTANT_ID = "asst_7LdhJMasW5HHGZh0cgchTGkX"

# Archivos de conocimiento a subir
ARCHIVOS_CONOCIMIENTO = [
    "Files /BMC_Base_Unificada_v4.json",
    "Files /panelin_truth_bmcuruguay_web_only_v2.json",
    "Files /panelin_truth_bmcuruguay_catalog_v2_index.csv",
    "BMC_Base_Conocimiento_GPT-2.json",  # También incluir el original
]

def actualizar_asistente():
    """Actualiza el asistente con los archivos de conocimiento"""
    
    client = OpenAI(api_key=API_KEY)
    
    print("=" * 70)
    print("🔄 ACTUALIZANDO PANELIN CON BASE DE CONOCIMIENTO")
    print("=" * 70)
    
    # Subir archivos
    file_ids = []
    print("\n📤 Subiendo archivos de conocimiento...")
    
    for archivo_path in ARCHIVOS_CONOCIMIENTO:
        path = Path(archivo_path)
        if not path.exists():
            print(f"   ⚠️  No encontrado: {archivo_path}")
            continue
        
        try:
            print(f"   📄 Subiendo {path.name}...")
            with open(path, "rb") as f:
                file = client.files.create(
                    file=f,
                    purpose="assistants"
                )
            file_ids.append(file.id)
            print(f"      ✅ Subido: {file.id}")
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    if not file_ids:
        print("\n❌ No se pudieron subir archivos")
        return
    
    print(f"\n✅ {len(file_ids)} archivos subidos exitosamente")
    
    # Actualizar asistente
    print("\n🔧 Actualizando asistente...")
    try:
        # Obtener asistente actual
        assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
        
        # Actualizar con nuevos archivos
        updated_assistant = client.beta.assistants.update(
            ASSISTANT_ID,
            tool_resources={
                "code_interpreter": {
                    "file_ids": file_ids
                }
            }
        )
        
        print(f"\n✅ Asistente actualizado exitosamente")
        print(f"   ID: {updated_assistant.id}")
        print(f"   Archivos asociados: {len(file_ids)}")
        print(f"\n💡 Panelin ahora tiene acceso a:")
        for archivo in ARCHIVOS_CONOCIMIENTO:
            if Path(archivo).exists():
                print(f"   ✅ {Path(archivo).name}")
        
    except Exception as e:
        print(f"\n❌ Error actualizando asistente: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    actualizar_asistente()
