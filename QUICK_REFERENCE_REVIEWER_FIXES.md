# Quick Reference: Resolver Fixes de Reviewer

## Flujo Rápido

```
1. Leer feedback completo → 2. Clasificar tipo → 3. Analizar impacto → 
4. Verificar contexto Panelin/KB → 5. Crear plan → 6. Implementar → 
7. Validar → 8. Documentar → 9. Resumen
```

## Checklist Rápido

### Antes de Implementar
- [ ] ¿Entiendo completamente el problema?
- [ ] ¿Clasifiqué el tipo de fix?
- [ ] ¿Analicé el impacto?
- [ ] ¿Verifiqué que no afecta identidad de Panelin?
- [ ] ¿Verifiqué que respeta KB hierarchy?

### Durante Implementación
- [ ] ¿Leí el archivo completo antes de modificar?
- [ ] ¿Hago cambios incrementales?
- [ ] ¿Valido sintaxis después de cada cambio?
- [ ] ¿Sigo convenciones del proyecto?

### Después de Implementar
- [ ] ¿El fix resuelve el problema?
- [ ] ¿Tests pasan?
- [ ] ¿No introduje regresiones?
- [ ] ¿Documentación actualizada?
- [ ] ¿Git listo para commit?

## Tipos de Fix

- 🐛 **Bug**: Error funcional
- 🔒 **Security**: Vulnerabilidad
- 📝 **Code Quality**: Legibilidad/mantenibilidad
- 🏗️ **Architecture**: Estructura/diseño
- 📚 **Documentation**: Docs desactualizadas
- ⚡ **Performance**: Optimización
- 🧪 **Testing**: Tests faltantes/incorrectos
- 🔄 **Refactoring**: Reestructuración

## Guardrails Críticos

### ❌ NUNCA Modificar
- Identidad de Panelin (nombre, personalidad, rol)
- Personalización por usuario (Mauro, Martin, Rami)
- Estilo de comunicación rioplatense
- Jerarquía KB sin validación (Nivel 1 es Master)

### ✅ SIEMPRE Verificar
- Sintaxis correcta
- Tests pasan
- No regresiones
- Documentación actualizada
- Respeta arquitectura

## Comandos Útiles

```bash
# Validar Python
python -m py_compile archivo.py

# Validar JSON
python -m json.tool archivo.json > /dev/null

# Tests
pytest tests/ -v

# Git status
git status
git diff --staged
```

## Template de Resumen

```markdown
## ✅ Fix: [Título]

**Tipo**: [Bug/Security/Code Quality/etc.]
**Archivos**: [lista]
**Problema**: [descripción]
**Solución**: [descripción]
**Validación**: ✅ Tests pasan, no regresiones
```

---

**Para instrucciones completas, ver**: `PROMPT_REVIEWER_FIXES_INSTRUCTIONS.md`
