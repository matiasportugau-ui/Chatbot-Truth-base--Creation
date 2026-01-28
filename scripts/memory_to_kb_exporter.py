#!/usr/bin/env python3
"""
MCP Memory to Knowledge Base Exporter
=====================================
Este script extrae entidades y observaciones del servidor MCP Memory 
y las integra en el archivo JSON de Knowledge Base (Nivel 1 Master).
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

def load_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path: str, data: Dict[str, Any]):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def export_memory_to_kb(kb_path: str, memory_data: Dict[str, Any]):
    kb = load_json(kb_path)
    if not kb:
        print(f"❌ Error: No se pudo cargar el archivo KB en {kb_path}")
        return

    entities = memory_data.get("entities", [])
    if not entities:
        print("ℹ️ No hay entidades nuevas en la memoria MCP para exportar.")
        return

    print(f"🔍 Procesando {len(entities)} entidades de la memoria MCP...")
    
    # Asegurar sección de correcciones o notas de usuario
    if "user_corrections" not in kb:
        kb["user_corrections"] = []

    new_entries = 0
    for entity in entities:
        name = entity.get("name")
        entity_type = entity.get("entityType")
        observations = entity.get("observations", [])
        
        # Crear una entrada estructurada para la KB
        entry = {
            "fuente": "MCP_Memory",
            "fecha_captura": datetime.now().isoformat(),
            "entidad": name,
            "tipo": entity_type,
            "observaciones": observations
        }
        
        kb["user_corrections"].append(entry)
        new_entries += 1
        print(f"  ✅ Entidad '{name}' ({entity_type}) añadida a user_corrections.")

    # Actualizar meta
    kb["meta"]["fecha"] = datetime.now().strftime("%Y-%m-%d")
    kb["meta"]["version"] = kb["meta"].get("version", "1.0") + "-mem-update"

    save_json(kb_path, kb)
    print(f"\n✨ Exportación completada. {new_entries} entradas añadidas a {kb_path}")

if __name__ == "__main__":
    # Este script espera recibir el JSON de la memoria por STDIN o un archivo temporal
    # Para uso manual, se puede pasar el path del KB
    KB_MASTER = "BMC_Base_Conocimiento_GPT-2.json"
    
    if len(sys.argv) > 1:
        # Si se pasa un argumento, asumimos que es el JSON de la memoria (para pruebas)
        try:
            mem_data = json.loads(sys.argv[1])
            export_memory_to_kb(KB_MASTER, mem_data)
        except Exception as e:
            print(f"❌ Error al procesar datos: {e}")
    else:
        print("💡 Uso: Este script es invocado por el Asistente para sincronizar la memoria MCP.")
