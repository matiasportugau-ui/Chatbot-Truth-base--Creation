# PROMPT: Instrucciones para Agente de Gestión Git/GitHub Segura

## Contexto

El agente "AI Project Files Organizer Agent" necesita poder:
1. Stage, commit, pull y push cambios de forma segura
2. Pedir aprobación explícita antes de cualquier operación Git
3. Explicar claramente el plan de acción antes de ejecutar
4. Seguir mejores prácticas de GitHub
5. Manejar conflictos y errores de forma segura
6. Validar el estado del repositorio antes de operaciones

## Requisitos Críticos

### 1. SEGURIDAD PRIMERO
- NUNCA ejecutar operaciones Git sin aprobación explícita del usuario
- SIEMPRE mostrar qué archivos serán afectados antes de stage
- SIEMPRE mostrar el mensaje de commit antes de commit
- SIEMPRE verificar estado del repositorio antes de pull/push
- NUNCA hacer force push sin aprobación explícita
- NUNCA eliminar branches sin confirmación

### 2. MEJORES PRÁCTICAS DE GIT

#### Commits
- Usar Conventional Commits: `type(scope): description`
  - Types: feat, fix, docs, style, refactor, test, chore
  - Ejemplo: `feat(organizer): add version manager with ddmm format`
- Mensajes descriptivos y concisos (máx 72 caracteres para subject)
- Body opcional para explicación detallada (separado por línea vacía)
- Footer para breaking changes o referencias a issues

#### Branching Strategy
- `main` o `master`: producción estable
- `develop`: desarrollo activo
- `feature/`: nuevas features
- `fix/`: bug fixes
- `hotfix/`: fixes urgentes de producción
- `release/`: preparación de releases

#### Workflow
1. Verificar estado: `git status`
2. Pull antes de push: `git pull --rebase` o `git pull`
3. Resolver conflictos si existen
4. Stage cambios: `git add`
5. Commit con mensaje apropiado
6. Push a branch remoto

### 3. FLUJO DE APROBACIÓN

Para CADA operación Git, el agente debe:

1. **ANALIZAR** la situación:
   - Estado actual del repositorio
   - Archivos modificados/agregados/eliminados
   - Branch actual
   - Estado remoto (si hay cambios)
   - Conflictos potenciales

2. **PLANIFICAR** la acción:
   - Qué operaciones se ejecutarán
   - En qué orden
   - Qué archivos serán afectados
   - Qué mensajes de commit se usarán
   - Qué branches serán afectados

3. **PRESENTAR** el plan al usuario:
   ```
   📋 PLAN DE ACCIÓN GIT
   
   Operación: [stage/commit/pull/push]
   Branch actual: [nombre]
   Archivos afectados:
     - [archivo1] (modificado/agregado/eliminado)
     - [archivo2] (modificado)
   
   Mensaje de commit propuesto:
   "[tipo](scope): descripción"
   
   Pasos a ejecutar:
   1. git status (verificar estado)
   2. git add [archivos]
   3. git commit -m "[mensaje]"
   4. git pull origin [branch] (si es necesario)
   5. git push origin [branch]
   
   ⚠️ ADVERTENCIAS:
   - [Cualquier advertencia relevante]
   
   ¿Aprobar esta operación? (sí/no/modificar)
   ```

4. **ESPERAR** aprobación explícita:
   - Usuario puede: aprobar, rechazar, o modificar el plan
   - Si modifica: re-presentar plan actualizado
   - Si rechaza: cancelar y explicar por qué

5. **EJECUTAR** solo si aprobado:
   - Ejecutar comandos en orden
   - Verificar éxito de cada paso
   - Manejar errores apropiadamente
   - Reportar resultados

6. **VERIFICAR** resultado:
   - Confirmar que operaciones fueron exitosas
   - Mostrar estado final
   - Reportar cualquier problema

### 4. VALIDACIONES ANTES DE OPERACIONES

#### Antes de STAGE:
- ✅ Verificar que hay cambios para stagear
- ✅ Verificar que archivos existen
- ✅ Verificar permisos de archivos
- ✅ Verificar que no hay conflictos de merge pendientes
- ✅ Verificar que .gitignore está respetado

#### Antes de COMMIT:
- ✅ Verificar que hay cambios staged
- ✅ Validar formato del mensaje de commit (Conventional Commits)
- ✅ Verificar que no hay conflictos
- ✅ Verificar que branch es correcto
- ✅ Verificar que pre-commit hooks pasan (si existen)

#### Antes de PULL:
- ✅ Verificar estado del repositorio (no hay cambios sin commit)
- ✅ Verificar branch actual
- ✅ Verificar conexión con remoto
- ✅ Detectar conflictos potenciales
- ✅ Hacer backup si es necesario

#### Antes de PUSH:
- ✅ Verificar que hay commits para push
- ✅ Verificar que branch remoto existe o crear si es necesario
- ✅ Verificar que no hay conflictos
- ✅ NUNCA hacer force push sin aprobación explícita
- ✅ Verificar que no se está pusheando a main/master directamente (sugerir PR)

### 5. MANEJO DE CONFLICTOS

Si se detectan conflictos:

1. **DETECTAR** conflictos:
   - Durante pull
   - Durante merge
   - Durante rebase

2. **INFORMAR** al usuario:
   ```
   ⚠️ CONFLICTOS DETECTADOS
   
   Archivos en conflicto:
   - [archivo1]
   - [archivo2]
   
   Razón: [explicación]
   
   Opciones:
   1. Resolver manualmente (recomendado)
   2. Abortar operación
   3. Usar estrategia automática (solo si aprobado)
   ```

3. **NO RESOLVER** automáticamente sin aprobación explícita
4. **OFRECER** opciones de resolución
5. **ESPERAR** decisión del usuario

### 6. MENSAJES DE COMMIT

El agente debe generar mensajes de commit siguiendo Conventional Commits:

**Formato**:
```
<type>(<scope>): <subject>

<body (opcional)>

<footer (opcional)>
```

**Types**:
- `feat`: Nueva feature
- `fix`: Bug fix
- `docs`: Cambios en documentación
- `style`: Formato, punto y coma, etc. (no afecta código)
- `refactor`: Refactorización de código
- `test`: Agregar o modificar tests
- `chore`: Tareas de mantenimiento, build, etc.

**Ejemplos**:
```
feat(organizer): add version manager with ddmm format

Implement version manager that automatically adds date and version
codes to filenames in format ddmm_vN. Includes detection of existing
versions and automatic incrementing.

Closes #123

fix(scanner): handle edge case in file categorization

docs(readme): update installation instructions

refactor(agent): simplify file organization logic
```

### 7. OPERACIONES ESPECÍFICAS

#### STAGE
```python
def stage_files(files: List[str], approval_required: bool = True) -> Dict:
    """
    Stage archivos específicos
    
    Validaciones:
    - Archivos existen
    - No hay conflictos
    - Archivos no están en .gitignore
    
    Presenta plan y espera aprobación si approval_required=True
    
    Returns:
        Dict con resultado de la operación
    """
```

#### COMMIT
```python
def commit_changes(
    message: str,
    files: Optional[List[str]] = None,
    approval_required: bool = True
) -> Dict:
    """
    Commit cambios staged
    
    Validaciones:
    - Hay cambios staged
    - Mensaje sigue Conventional Commits
    - Pre-commit hooks pasan
    
    Presenta plan y espera aprobación si approval_required=True
    
    Returns:
        Dict con resultado de la operación
    """
```

#### PULL
```python
def pull_changes(
    branch: Optional[str] = None,
    rebase: bool = False,
    approval_required: bool = True
) -> Dict:
    """
    Pull cambios del remoto
    
    Validaciones:
    - Repositorio está limpio
    - Branch existe
    - Conexión con remoto
    
    Presenta plan y espera aprobación si approval_required=True
    
    Returns:
        Dict con resultado de la operación
    """
```

#### PUSH
```python
def push_changes(
    branch: Optional[str] = None,
    force: bool = False,
    approval_required: bool = True
) -> Dict:
    """
    Push cambios al remoto
    
    Validaciones:
    - Hay commits para push
    - Branch remoto existe o se puede crear
    - No hay conflictos
    - Force solo si explícitamente aprobado
    
    Presenta plan y espera aprobación si approval_required=True
    
    Returns:
        Dict con resultado de la operación
    """
```

### 8. CONFIGURACIÓN Y DETECCIÓN

El agente debe:
- Detectar si el directorio es un repositorio Git
- Detectar branch actual
- Detectar estado del repositorio
- Detectar remotos configurados
- Detectar si hay cambios sin commit
- Detectar si hay conflictos
- Detectar si pre-commit hooks están configurados

### 9. LOGGING Y AUDITORÍA

Todas las operaciones Git deben ser logueadas:
- Qué operación se ejecutó
- Cuándo se ejecutó
- Qué archivos fueron afectados
- Qué mensaje de commit se usó
- Si fue aprobado por el usuario
- Resultado (éxito/error)
- Cualquier advertencia o error

### 10. CASOS ESPECIALES

#### Trabajando en main/master
- Advertir fuertemente
- Sugerir crear branch
- Requerir doble confirmación

#### Force Push
- NUNCA sin aprobación explícita
- Advertir sobre peligros
- Sugerir alternativas

#### Eliminar Branches
- Advertir sobre pérdida de datos
- Verificar que no es branch protegido
- Requerir confirmación explícita

#### Cambios no commiteados
- Advertir antes de pull
- Ofrecer stash
- Ofrecer commit
- Ofrecer abortar

## OUTPUT ESPERADO

Genera un documento completo con:

1. **Instrucciones detalladas** para el agente sobre cómo manejar Git
2. **Código Python** para la clase `GitManager` con todos los métodos
3. **Ejemplos de uso** de cada operación
4. **Casos de prueba** para validar comportamiento
5. **Documentación** de cada método con docstrings
6. **Manejo de errores** para cada operación
7. **Validaciones** específicas para cada tipo de operación
8. **Templates** de mensajes de aprobación
9. **Guía de mejores prácticas** integrada en el código
10. **Configuración** para diferentes workflows (Git Flow, GitHub Flow, etc.)

## CRITERIOS DE ÉXITO

Las instrucciones deben resultar en un agente que:
- ✅ NUNCA ejecuta operaciones Git sin aprobación
- ✅ SIEMPRE explica qué va a hacer antes de hacerlo
- ✅ Sigue mejores prácticas de Git/GitHub
- ✅ Maneja errores de forma segura
- ✅ Proporciona información clara al usuario
- ✅ Es fácil de usar y entender
- ✅ Es robusto y confiable
- ✅ Está bien documentado
- ✅ Tiene tests completos

## IMPORTANTE

Este es un componente CRÍTICO para el proyecto. Las operaciones Git mal 
ejecutadas pueden causar pérdida de trabajo o problemas serios en el 
repositorio. Las instrucciones deben ser EXHAUSTIVAS, CLARAS, y 
ENFOCADAS EN SEGURIDAD.

## ESTRUCTURA DE CLASE ESPERADA

```python
# ai_files_organizer/core/git_manager.py

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import subprocess
import json

class GitManager:
    """
    Gestor seguro de operaciones Git con aprobación del usuario
    
    Características:
    - Validaciones exhaustivas antes de cada operación
    - Sistema de aprobación explícita
    - Seguimiento de mejores prácticas
    - Manejo seguro de conflictos
    - Logging completo de operaciones
    """
    
    def __init__(self, workspace_path: str, require_approval: bool = True):
        """
        Inicializar Git Manager
        
        Args:
            workspace_path: Ruta del repositorio
            require_approval: Si True, requiere aprobación para todas las operaciones
        """
        self.workspace_path = Path(workspace_path)
        self.require_approval = require_approval
        self.log_file = self.workspace_path / ".git_operations.log"
    
    def analyze_repository_state(self) -> Dict:
        """
        Analizar estado actual del repositorio
        
        Returns:
            Dict con información del estado del repositorio
        """
        pass
    
    def plan_stage_operation(self, files: List[str]) -> Dict:
        """
        Planificar operación de stage y presentar al usuario
        
        Args:
            files: Lista de archivos a stagear
            
        Returns:
            Dict con plan de acción
        """
        pass
    
    def plan_commit_operation(self, message: str) -> Dict:
        """
        Planificar commit y presentar al usuario
        
        Args:
            message: Mensaje de commit propuesto
            
        Returns:
            Dict con plan de acción
        """
        pass
    
    def plan_pull_operation(self, branch: Optional[str] = None) -> Dict:
        """
        Planificar pull y presentar al usuario
        
        Args:
            branch: Branch a hacer pull (None = actual)
            
        Returns:
            Dict con plan de acción
        """
        pass
    
    def plan_push_operation(self, branch: Optional[str] = None) -> Dict:
        """
        Planificar push y presentar al usuario
        
        Args:
            branch: Branch a hacer push (None = actual)
            
        Returns:
            Dict con plan de acción
        """
        pass
    
    def execute_approved_plan(self, plan: Dict) -> Dict:
        """
        Ejecutar plan aprobado por el usuario
        
        Args:
            plan: Plan de acción aprobado
            
        Returns:
            Dict con resultado de la operación
        """
        pass
    
    def handle_conflicts(self, conflicts: List[str]) -> Dict:
        """
        Manejar conflictos detectados
        
        Args:
            conflicts: Lista de archivos en conflicto
            
        Returns:
            Dict con resultado del manejo
        """
        pass
    
    def validate_commit_message(self, message: str) -> Tuple[bool, str]:
        """
        Validar formato de mensaje de commit (Conventional Commits)
        
        Args:
            message: Mensaje a validar
            
        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        pass
    
    def generate_commit_message(self, changes: Dict) -> str:
        """
        Generar mensaje de commit siguiendo Conventional Commits
        
        Args:
            changes: Dict con información de cambios
            
        Returns:
            Mensaje de commit generado
        """
        pass
    
    def _log_operation(self, operation: str, details: Dict) -> None:
        """
        Loggear operación Git
        
        Args:
            operation: Nombre de la operación
            details: Detalles de la operación
        """
        pass
```

---

**USO DE ESTE PROMPT:**

Copia este prompt completo y úsalo con un modelo de lenguaje (GPT-4, Claude, etc.) para generar las instrucciones detalladas y el código completo del `GitManager`. Asegúrate de revisar cuidadosamente el output antes de implementarlo, ya que este es un componente crítico para la seguridad del repositorio.
