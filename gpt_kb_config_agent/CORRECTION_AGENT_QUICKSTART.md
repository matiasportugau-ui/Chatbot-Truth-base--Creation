# 🚀 GPT Correction Agent - Guía Rápida

## Uso Rápido

### Desde Python

```python
from gpt_kb_config_agent.correction_agent import GPTCorrectionAgent

# Inicializar agente
agent = GPTCorrectionAgent(backup_enabled=True)

# Aplicar corrección
result = agent.apply_correction(
    correction_id="KB-001",
    correction_type="precio",
    description="Actualizar precio ISODEC EPS 100mm",
    priority="P0",
    changes={
        "product_id": "ISODEC_EPS",
        "espesor": "100",
        "nuevo_precio": 47.50
    }
)

print(f"Éxito: {result['success']}")
```

### Desde CLI

```bash
# Modo interactivo
python gpt_kb_config_agent/apply_corrections.py --interactive

# Desde archivo JSON
python gpt_kb_config_agent/apply_corrections.py --file docs/corrections/ejemplo_correcciones.json

# Validar archivos
python gpt_kb_config_agent/apply_corrections.py --validate
```

## Tipos de Correcciones

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `institucional` | Info de BMC Uruguay | Descripción, diferencial |
| `producto` | Agregar/modificar productos | Nuevo producto con espesores |
| `precio` | Actualizar precios | Cambiar precio de un espesor |
| `formula` | Actualizar fórmulas | Fórmulas de cálculo |
| `catalogo` | Actualizar catálogo | Líneas mencionadas |
| `capabilities` | Políticas de capabilities | Transcripción de audio |
| `reglas_negocio` | Reglas de negocio | IVA, moneda, etc. |

## Ejemplo Completo

Ver `docs/corrections/ejemplo_correcciones.json` para ejemplos completos.

## Después de Aplicar Correcciones

1. ✅ Validar cambios: `python apply_corrections.py --validate`
2. ✅ Revisar reportes en `docs/corrections/`
3. ✅ Re-subir archivos al GPT según `docs/gpt/PANELIN_GPT_BUILDER_QUICK_FILL.md`
4. ✅ Ejecutar tests de validación
5. ✅ Commit a Git

## Documentación Completa

Ver `README_CORRECTION_AGENT.md` para documentación completa.
