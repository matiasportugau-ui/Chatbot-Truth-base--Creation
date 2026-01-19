# Guía de Uso - AI Project Files Organizer Agent

## 📋 Índice
1. [Instalación](#instalación)
2. [Uso desde Línea de Comandos (CLI)](#uso-desde-línea-de-comandos-cli)
3. [Uso desde Python (API)](#uso-desde-python-api)
4. [Ejemplos Prácticos](#ejemplos-prácticos)
5. [Configuración](#configuración)

---

## 🚀 Instalación

### Opción 1: Instalación en modo desarrollo (recomendado)
```bash
cd ai-project-files-organizer-agent
pip install -e .
```

### Opción 2: Instalar dependencias manualmente
```bash
pip install -r requirements.txt
```

---

## 💻 Uso desde Línea de Comandos (CLI)

### 1. Escanear proyecto (sin hacer cambios)
Ver qué archivos se organizarían sin modificar nada:

```bash
# Escanear un proyecto
files-organizer scan /ruta/a/tu/proyecto

# Escanear y detectar archivos obsoletos
files-organizer scan /ruta/a/tu/proyecto --outdated
```

### 2. Organizar archivos existentes
Organiza todos los archivos del proyecto:

```bash
# Con aprobación interactiva (recomendado)
files-organizer organize /ruta/a/tu/proyecto

# Sin aprobación (usa con precaución)
files-organizer organize /ruta/a/tu/proyecto --no-approval

# Con archivo de configuración personalizado
files-organizer organize /ruta/a/tu/proyecto --config /ruta/config.json
```

### 3. Monitoreo en tiempo real
Vigila nuevos archivos y sugiere organización automáticamente:

```bash
files-organizer watch /ruta/a/tu/proyecto
# Presiona Ctrl+C para detener
```

---

## 🐍 Uso desde Python (API)

### Ejemplo 1: Uso Básico - Organizar Archivos

```python
from ai_files_organizer import FileOrganizerAgent

# Inicializar el agente
organizer = FileOrganizerAgent(
    workspace_path="/ruta/a/tu/proyecto",
    require_approval=True  # Pedir aprobación antes de cambios
)

# Organizar archivos existentes
result = organizer.organize_existing_files(interactive=True)

if result.get("success"):
    print(f"✅ Organizados {len(result['results']['successful'])} archivos")
    print(f"❌ Fallaron {len(result['results']['failed'])} archivos")
else:
    print("❌ La organización no fue aprobada")
```

### Ejemplo 2: Sugerir Ubicación para un Archivo Nuevo

```python
from ai_files_organizer import FileOrganizerAgent

organizer = FileOrganizerAgent(workspace_path="/ruta/a/tu/proyecto")

# Sugerir dónde debería ir un archivo nuevo
proposal = organizer.suggest_new_file_location("mi_documento.md")

if "error" not in proposal:
    print(f"📁 Ubicación sugerida: {proposal['proposed_location']}")
    print(f"📝 Nombre sugerido: {proposal['proposed_name']}")
else:
    print(f"Error: {proposal['error']}")
```

### Ejemplo 3: Detectar Archivos Obsoletos

```python
from ai_files_organizer import FileOrganizerAgent

organizer = FileOrganizerAgent(workspace_path="/ruta/a/tu/proyecto")

# Detectar archivos obsoletos
outdated = organizer.detect_outdated_files()

print(f"⚠️  Encontrados {len(outdated)} archivos obsoletos:")
for file_info in outdated:
    print(f"  - {file_info['file']}: {file_info.get('reason', 'Sin razón especificada')}")
```

### Ejemplo 4: Integración con Git

```python
from ai_files_organizer import FileOrganizerAgent

organizer = FileOrganizerAgent(
    workspace_path="/ruta/a/tu/proyecto",
    require_approval=False  # Para pruebas
)

# Verificar si hay Git manager
if organizer.git_manager:
    # Organizar archivos primero
    result = organizer.organize_existing_files(interactive=False)
    
    if result.get("success"):
        # Obtener archivos organizados
        successful = result['results']['successful']
        files_to_commit = [f["new_location"] for f in successful]
        
        # Hacer stage y commit
        git_result = organizer.stage_and_commit_changes(
            files=files_to_commit,
            message="chore(organizer): organizar archivos del proyecto",
            interactive=False,
            auto_push=False  # No hacer push automáticamente
        )
        
        if git_result.get("success"):
            print("✅ Cambios commiteados exitosamente")
        else:
            print(f"❌ Error en Git: {git_result.get('error', 'Unknown')}")
else:
    print("⚠️  No se detectó un repositorio Git")
```

### Ejemplo 5: Monitoreo en Tiempo Real

```python
from ai_files_organizer import FileOrganizerAgent
import time

organizer = FileOrganizerAgent(workspace_path="/ruta/a/tu/proyecto")

try:
    print("👀 Iniciando monitoreo... (Ctrl+C para detener)")
    organizer.start_monitoring(interactive=True)
    
    # Mantener el programa corriendo
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\n🛑 Deteniendo monitoreo...")
    organizer.stop_monitoring()
    print("✅ Monitoreo detenido")
```

### Ejemplo 6: Obtener Estadísticas

```python
from ai_files_organizer import FileOrganizerAgent

organizer = FileOrganizerAgent(workspace_path="/ruta/a/tu/proyecto")

# Realizar algunas operaciones
organizer.organize_existing_files(interactive=False)

# Obtener estadísticas
stats = organizer.get_statistics()

print("📊 Estadísticas del Agente:")
print(f"  Total de operaciones: {stats['total_operations']}")
print(f"  Archivos organizados: {stats['total_files_organized']}")
print(f"  Aprobaciones solicitadas: {stats['total_approvals_requested']}")
print(f"  Aprobaciones concedidas: {stats['total_approvals_granted']}")
print(f"  Tasa de aprobación: {stats['approval_rate']:.2%}")
print(f"  Duración total: {stats['total_duration_seconds']:.2f} segundos")
```

---

## ⚙️ Configuración

### Ubicación del Archivo de Configuración
El archivo de configuración por defecto está en:
```
ai_files_organizer/config/default_config.json
```

### Configuración Actual
```json
{
  "backup": {
    "enabled": true,
    "location": ".files_organizer/backups",
    "keep_days": 60  // ← Configurado a 60 días
  },
  "monitoring": {
    "realtime": true,
    "periodic_interval_hours": 24
  },
  "versioning": {
    "format": "ddmm_vN",
    "auto_increment": true
  }
}
```

### Usar Configuración Personalizada

```python
from pathlib import Path
from ai_files_organizer import FileOrganizerAgent

# Especificar ruta a tu archivo de configuración
config_path = Path("/ruta/a/mi_config.json")

organizer = FileOrganizerAgent(
    workspace_path="/ruta/a/tu/proyecto",
    config_path=config_path
)
```

---

## 📝 Ejemplos Prácticos Completos

### Script Completo: Organizar y Hacer Commit

```python
#!/usr/bin/env python3
"""
Script completo para organizar un proyecto y hacer commit en Git
"""

from pathlib import Path
from ai_files_organizer import FileOrganizerAgent

def main():
    # Configurar ruta del proyecto
    project_path = Path("/ruta/a/tu/proyecto")
    
    # Inicializar agente
    print("🚀 Inicializando agente...")
    organizer = FileOrganizerAgent(
        workspace_path=str(project_path),
        require_approval=True  # Pedir aprobación
    )
    
    # Escanear primero
    print("\n📊 Escaneando archivos...")
    files = organizer.scanner.scan()
    print(f"   Encontrados {len(files)} archivos")
    
    # Organizar
    print("\n🗂️  Organizando archivos...")
    result = organizer.organize_existing_files(interactive=True)
    
    if result.get("success"):
        successful = result['results']['successful']
        print(f"\n✅ {len(successful)} archivos organizados exitosamente")
        
        # Si hay Git, hacer commit
        if organizer.git_manager:
            print("\n🔄 Haciendo commit en Git...")
            files_to_commit = [f["new_location"] for f in successful]
            
            git_result = organizer.stage_and_commit_changes(
                files=files_to_commit,
                message="chore(organizer): organizar estructura de archivos",
                interactive=True,
                auto_push=False
            )
            
            if git_result.get("success"):
                print("✅ Commit realizado exitosamente")
            else:
                print(f"⚠️  No se pudo hacer commit: {git_result.get('error')}")
        
        # Mostrar estadísticas
        print("\n📊 Estadísticas:")
        stats = organizer.get_statistics()
        print(f"   Archivos organizados: {stats['total_files_organized']}")
        print(f"   Duración: {stats['total_duration_seconds']:.2f}s")
    else:
        print("❌ La organización no fue aprobada")

if __name__ == "__main__":
    main()
```

---

## 🔍 Comandos Útiles

### Verificar instalación
```bash
python3 -c "from ai_files_organizer import FileOrganizerAgent; print('✅ Instalado correctamente')"
```

### Ejecutar tests
```bash
pytest tests/ -v
```

### Ver cobertura de tests
```bash
pytest tests/ --cov=ai_files_organizer
```

---

## 💡 Consejos

1. **Siempre escanea primero**: Usa `scan` antes de `organize` para ver qué cambiará
2. **Revisa las propuestas**: El agente pide aprobación antes de hacer cambios
3. **Usa Git**: El agente detecta repositorios Git automáticamente
4. **Configura backups**: Los backups se guardan en `.files_organizer/backups`
5. **Personaliza reglas**: Crea `folder_rules.json` para reglas personalizadas

---

## 🆘 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'watchdog'"
```bash
pip install -r requirements.txt
```

### Error: "Not a Git repository"
El agente funciona sin Git, pero algunas funciones requieren un repositorio Git inicializado.

### Los archivos no se organizan
- Verifica que tengas permisos de escritura
- Revisa que el workspace_path sea correcto
- Comprueba los logs en `.files_organizer/logs/agent.log`

---

¿Necesitas más ayuda? Revisa la documentación completa en `docs/` o los ejemplos en `docs/examples/`.
