# GPT Correction Agent

Agente especializado para aplicar correcciones a la base de conocimientos del GPT después de identificar errores o recibir feedback del equipo.

## 📋 Características

- ✅ **Aplicación automática de correcciones** a archivos KB
- ✅ **Sistema de backups** antes de modificar archivos
- ✅ **Validación de cambios** para mantener integridad
- ✅ **Reportes detallados** de todas las correcciones aplicadas
- ✅ **Soporte para múltiples tipos de correcciones**
- ✅ **Aplicación en lote** de múltiples correcciones

## 🚀 Uso Rápido

### Instalación

```python
from gpt_kb_config_agent.correction_agent import GPTCorrectionAgent

agent = GPTCorrectionAgent(
    project_root="/ruta/al/proyecto",
    backup_enabled=True
)
```

### Ejemplo Básico: Corrección Institucional

```python
result = agent.apply_correction(
    correction_id="KB-001",
    correction_type="institucional",
    description="Actualizar descripción institucional",
    priority="P0",
    changes={
        "descripcion": "BMC Uruguay no fabrica. Suministra/comercializa...",
        "diferencial": "Soluciones técnicas optimizadas..."
    }
)

print(f"Éxito: {result['success']}")
print(f"Archivos modificados: {result['affected_files']}")
```

### Ejemplo: Actualizar Precio

```python
result = agent.apply_correction(
    correction_id="KB-PRICE-001",
    correction_type="precio",
    description="Actualizar precio de ISODEC EPS 100mm",
    priority="P0",
    changes={
        "product_id": "ISODEC_EPS",
        "espesor": "100",
        "nuevo_precio": 47.50
    }
)
```

### Ejemplo: Agregar Producto

```python
result = agent.apply_correction(
    correction_id="KB-003",
    correction_type="producto",
    description="Agregar producto Isofrig PIR",
    priority="P1",
    changes={
        "product_id": "ISOFRIG_PIR",
        "nombre_comercial": "Isofrig (PIR)",
        "tipo": "pared_frigorifica",
        "espesores": {
            "100": {
                "autoportancia": 5.5,
                "precio": 65.0,
                "coeficiente_termico": 0.022,
                "resistencia_termica": 4.55
            }
        }
    }
)
```

## 📝 Tipos de Correcciones Soportadas

### 1. `institucional`
Corrige información institucional de BMC Uruguay.

**Archivos afectados:**
- `BMC_Base_Conocimiento_GPT-2.json`

**Campos soportados:**
- `descripcion`: Descripción de la empresa
- `diferencial`: Diferencial competitivo
- `empresa`: Nombre de la empresa

### 2. `producto`
Agrega o modifica productos en el catálogo.

**Archivos afectados:**
- `BMC_Base_Conocimiento_GPT-2.json`

**Campos requeridos:**
- `product_id`: ID del producto (ej: "ISOFRIG_PIR")
- `nombre_comercial`: Nombre comercial
- `tipo`: Tipo de producto
- `espesores`: Diccionario con espesores disponibles

### 3. `precio`
Actualiza precios de productos existentes.

**Archivos afectados:**
- `BMC_Base_Conocimiento_GPT-2.json`

**Campos requeridos:**
- `product_id`: ID del producto
- `espesor`: Espesor en mm (string)
- `nuevo_precio`: Nuevo precio en USD

### 4. `formula`
Actualiza fórmulas de cálculo.

**Archivos afectados:**
- `BMC_Base_Conocimiento_GPT-2.json`

**Campos requeridos:**
- `tipo_formula`: "cotizacion" o "ahorro_energetico"
- `nombre_formula`: Nombre de la fórmula
- `nueva_formula`: Nueva expresión de la fórmula

### 5. `catalogo`
Actualiza información del catálogo.

**Archivos afectados:**
- `BMC_Base_Conocimiento_GPT-2.json`
- `catalog/out/shopify_catalog_v1.json`

### 6. `capabilities`
Actualiza políticas de capabilities.

**Archivos afectados:**
- `BMC_Base_Conocimiento_GPT-2.json`

### 7. `reglas_negocio`
Actualiza reglas de negocio.

**Archivos afectados:**
- `BMC_Base_Conocimiento_GPT-2.json`

### 8. `instrucciones`
Actualiza archivos de instrucciones del sistema.

**Archivos afectados:**
- `docs/gpt/PANELIN_SYSTEM_INSTRUCTIONS_CANONICAL.md`
- `PANELIN_INSTRUCTIONS_FINAL.txt`
- `gpt_configs/INSTRUCCIONES_PANELIN_ACTUALIZADAS.txt`

## 🔄 Aplicación en Lote

Para aplicar múltiples correcciones a la vez:

```python
corrections = [
    {
        "correction_id": "KB-BATCH-001",
        "correction_type": "institucional",
        "description": "Actualizar diferencial",
        "priority": "P0",
        "changes": {
            "diferencial": "Nuevo diferencial..."
        }
    },
    {
        "correction_id": "KB-BATCH-002",
        "correction_type": "precio",
        "description": "Actualizar precio",
        "priority": "P1",
        "changes": {
            "product_id": "ISODEC_EPS",
            "espesor": "100",
            "nuevo_precio": 47.50
        }
    }
]

summary = agent.batch_apply_corrections(corrections)
print(f"Exitosas: {summary['successful']}/{summary['total_corrections']}")
```

## ✅ Validación

Validar cambios aplicados:

```python
kb_file = Path("BMC_Base_Conocimiento_GPT-2.json")
validation = agent.validate_changes(kb_file)

if validation['valid']:
    print("✓ Archivo válido")
else:
    print("✗ Errores encontrados:")
    for error in validation['errors']:
        print(f"  - {error}")
```

## 📊 Reportes

Cada corrección genera un reporte JSON en:
```
docs/corrections/{correction_id}_{timestamp}.json
```

El reporte incluye:
- ID y tipo de corrección
- Archivos afectados
- Cambios aplicados
- Errores (si los hay)
- Información de backup
- Timestamp

## 🔒 Sistema de Backups

Por defecto, el agente crea backups automáticos antes de modificar archivos.

**Ubicación de backups:**
```
.corrections_backup/{correction_id}_{timestamp}/
```

Para deshabilitar backups:
```python
agent = GPTCorrectionAgent(backup_enabled=False)
```

## 📋 Prioridades

- **P0**: Crítico - Requiere acción inmediata
- **P1**: Alta - Importante, aplicar pronto
- **P2**: Media - Puede esperar

## 🔍 Estructura de Corrección

Formato estándar de una corrección:

```python
{
    "correction_id": "KB-XXX",           # ID único
    "correction_type": "tipo",           # Tipo de corrección
    "description": "Descripción...",     # Qué se corrige
    "priority": "P0|P1|P2",             # Prioridad
    "changes": {                         # Cambios a aplicar
        # ... estructura específica según tipo
    },
    "affected_files": [...]              # Opcional: archivos específicos
}
```

## 📚 Ejemplos Completos

Ver `example_corrections.py` para ejemplos completos de todos los tipos de correcciones.

## 🛠️ Integración con Workflow

### Flujo Recomendado:

1. **Identificar corrección** (manual o automática)
2. **Crear objeto de corrección** con formato estándar
3. **Aplicar corrección** con `apply_correction()`
4. **Validar cambios** con `validate_changes()`
5. **Revisar reporte** en `docs/corrections/`
6. **Re-subir archivos al GPT** según `PANELIN_GPT_BUILDER_QUICK_FILL.md`

### Después de Aplicar Correcciones:

1. Verificar que los cambios sean correctos
2. Validar integridad de archivos JSON
3. Re-subir archivos modificados al GPT Builder
4. Ejecutar tests de validación (ver `PANELIN_GPT_TEST_PLAN.md`)
5. Commit cambios a Git

## ⚠️ Notas Importantes

- **Siempre revisa los backups** antes de aplicar correcciones masivas
- **Valida los cambios** después de aplicarlos
- **Los archivos JSON se actualizan automáticamente** con versión y registro de correcciones
- **Las correcciones se registran en metadata** del archivo JSON
- **Los backups se guardan permanentemente** - considera limpiarlos periódicamente

## 🔗 Archivos Relacionados

- `PANELIN_GPT_BUILDER_QUICK_FILL.md`: Guía para re-subir archivos al GPT
- `CORRECCIONES_KB_2026-01-24.md`: Ejemplo de correcciones aplicadas
- `PANELIN_GPT_MAINTENANCE.md`: Guía de mantenimiento del GPT
