# PROMPT: Instrucciones para Resolver Fixes de Reviewer de Forma Perfecta

## Contexto y Objetivo

Este documento define las **instrucciones completas** para que el asistente de IA pueda resolver de forma perfecta todos los fixes que un reviewer encuentre en el código, documentación, o configuración del proyecto Panelin (BMC Assistant Pro).

El objetivo es crear un **entorno de chat perfecto** donde:
- ✅ Se entienden completamente los fixes solicitados
- ✅ Se analizan las implicaciones antes de implementar
- ✅ Se implementan los fixes correctamente siguiendo las mejores prácticas
- ✅ Se validan los cambios antes de considerarlos completos
- ✅ Se documentan los cambios apropiadamente
- ✅ Se mantiene la integridad del proyecto (especialmente la identidad de Panelin)

---

## 1. PROCESO DE ANÁLISIS DE FIXES

### 1.1 Entender el Fix

**ANTES de implementar cualquier cambio, el asistente DEBE:**

1. **LEER COMPLETAMENTE** el feedback del reviewer:
   - ¿Qué problema específico identifica?
   - ¿En qué archivo(s) está el problema?
   - ¿Qué línea(s) o sección(es) están afectadas?
   - ¿Cuál es el comportamiento esperado vs. el actual?

2. **CLASIFICAR el tipo de fix:**
   - 🐛 **Bug Fix**: Error funcional que causa comportamiento incorrecto
   - 🔒 **Security Fix**: Vulnerabilidad o problema de seguridad
   - 📝 **Code Quality**: Mejora de legibilidad, mantenibilidad, o estilo
   - 🏗️ **Architecture**: Cambio en estructura o diseño
   - 📚 **Documentation**: Corrección o mejora de documentación
   - ⚡ **Performance**: Optimización de rendimiento
   - 🧪 **Testing**: Agregar o corregir tests
   - 🔄 **Refactoring**: Reestructuración sin cambiar funcionalidad

3. **IDENTIFICAR el alcance:**
   - ¿Es un cambio localizado (un archivo) o global (múltiples archivos)?
   - ¿Afecta a la funcionalidad core o es periférico?
   - ¿Requiere cambios en dependencias?
   - ¿Requiere actualizar documentación relacionada?

### 1.2 Analizar Impacto

**El asistente DEBE evaluar:**

1. **Impacto en Funcionalidad:**
   - ¿Este fix rompe alguna funcionalidad existente?
   - ¿Hay tests que validen el comportamiento actual?
   - ¿Necesito ejecutar tests antes y después del cambio?

2. **Impacto en Arquitectura:**
   - ¿Este fix respeta la arquitectura del proyecto?
   - ¿Afecta la "Capa de Identidad" de Panelin (INAMOVIBLE)?
   - ¿Afecta la jerarquía de Knowledge Base?
   - ¿Requiere cambios en múltiples capas?

3. **Impacto en Dependencias:**
   - ¿Este fix requiere actualizar `requirements.txt`?
   - ¿Hay conflictos con otras dependencias?
   - ¿Necesito verificar compatibilidad de versiones?

4. **Impacto en Documentación:**
   - ¿Este fix requiere actualizar README, guías, o comentarios?
   - ¿Hay ejemplos de código que necesitan actualizarse?
   - ¿Hay diagramas o arquitectura que cambió?

### 1.3 Verificar Contexto del Proyecto

**ANTES de implementar, verificar:**

1. **Identidad de Panelin (CRÍTICO - INAMOVIBLE):**
   - ❌ NUNCA modificar la personalidad, nombre, o rol de Panelin
   - ❌ NUNCA cambiar la lógica de personalización por usuario (Mauro, Martin, Rami)
   - ❌ NUNCA modificar el estilo de comunicación rioplatense
   - ✅ Si el fix afecta estas áreas, CONSULTAR con el usuario primero

2. **Jerarquía de Knowledge Base:**
   - ✅ Respetar la jerarquía: Nivel 1 (Master) > Nivel 2 (Validación) > Nivel 3 (Dinámico)
   - ✅ NUNCA cambiar la fuente de verdad sin validación
   - ✅ Si el fix afecta la KB, verificar impacto en todas las referencias

3. **Estructura del Proyecto:**
   - ✅ Respetar la estructura de carpetas establecida
   - ✅ Seguir convenciones de nombres de archivos
   - ✅ Mantener separación de concerns (agents, validators, utils, etc.)

---

## 2. PROCESO DE IMPLEMENTACIÓN

### 2.1 Planificación del Fix

**El asistente DEBE crear un plan antes de implementar:**

```
📋 PLAN DE FIX

Tipo: [Bug Fix / Security / Code Quality / etc.]
Archivo(s) afectado(s):
  - [archivo1.py] (líneas X-Y)
  - [archivo2.md] (sección Z)

Problema identificado:
  [Descripción clara del problema]

Solución propuesta:
  1. [Paso 1 de la solución]
  2. [Paso 2 de la solución]
  3. [Paso 3 de la solución]

Archivos que se modificarán:
  - [archivo1.py] → [qué se cambiará]
  - [archivo2.md] → [qué se actualizará]

Archivos que se crearán (si aplica):
  - [nuevo_archivo.py] → [propósito]

Dependencias afectadas:
  - [dependencia1] → [cambio necesario]

Tests a ejecutar:
  - [test_file.py::test_function]
  - [Validación manual: descripción]

Riesgos identificados:
  - ⚠️ [Riesgo 1 y mitigación]
  - ⚠️ [Riesgo 2 y mitigación]

¿Proceder con este plan? (sí/no/modificar)
```

### 2.2 Implementación Paso a Paso

**El asistente DEBE:**

1. **LEER el archivo completo** antes de modificarlo:
   - Entender el contexto completo
   - Identificar todas las referencias al código que se modificará
   - Verificar imports y dependencias

2. **HACER cambios incrementales:**
   - Un cambio a la vez cuando sea posible
   - Verificar que cada cambio compila/valida antes del siguiente
   - No hacer múltiples fixes no relacionados en el mismo commit

3. **SEGUIR mejores prácticas del proyecto:**
   - **Python**: PEP 8, type hints cuando sea apropiado, docstrings
   - **Git**: Conventional Commits (ver `PROMPT_GIT_MANAGER_INSTRUCTIONS.md`)
   - **Documentación**: Markdown claro, ejemplos cuando sea útil
   - **Tests**: Agregar tests para nuevos fixes cuando sea apropiado

4. **MANTENER consistencia:**
   - Usar el mismo estilo de código que el resto del proyecto
   - Seguir los mismos patrones de diseño
   - Mantener la misma estructura de archivos

### 2.3 Validación Durante Implementación

**Después de cada cambio significativo:**

1. **Verificar sintaxis:**
   ```bash
   # Python
   python -m py_compile archivo.py
   # O
   python -m flake8 archivo.py  # si está configurado
   ```

2. **Verificar imports:**
   - ¿Todos los imports son válidos?
   - ¿Las dependencias están en `requirements.txt`?

3. **Verificar lógica:**
   - ¿El código hace lo que se espera?
   - ¿Maneja casos edge correctamente?
   - ¿Hay validaciones apropiadas?

4. **Verificar impacto:**
   - ¿Otros archivos referencian este código?
   - ¿Necesito actualizar referencias?

---

## 3. VALIDACIÓN POST-IMPLEMENTACIÓN

### 3.1 Checklist de Validación

**El asistente DEBE verificar:**

- [ ] **Sintaxis correcta**: El código compila/valida sin errores
- [ ] **Lógica correcta**: El fix resuelve el problema identificado
- [ ] **No rompe funcionalidad existente**: No introduce regresiones
- [ ] **Tests pasan**: Si hay tests relacionados, todos pasan
- [ ] **Documentación actualizada**: README, docstrings, comentarios
- [ ] **Consistencia mantenida**: Sigue patrones del proyecto
- [ ] **Identidad de Panelin preservada**: No afecta la capa inamovible
- [ ] **Knowledge Base intacta**: No rompe la jerarquía de fuentes
- [ ] **Git listo**: Cambios están staged apropiadamente

### 3.2 Pruebas Específicas por Tipo de Fix

#### Bug Fix:
- [ ] Reproducir el bug original (debe fallar)
- [ ] Aplicar el fix
- [ ] Verificar que el bug está resuelto
- [ ] Verificar que casos relacionados funcionan
- [ ] Verificar casos edge

#### Security Fix:
- [ ] Identificar la vulnerabilidad específica
- [ ] Verificar que el fix cierra la vulnerabilidad
- [ ] Verificar que no introduce nuevas vulnerabilidades
- [ ] Considerar agregar tests de seguridad

#### Code Quality:
- [ ] Verificar que el código es más legible
- [ ] Verificar que mantiene la misma funcionalidad
- [ ] Ejecutar linter/formatter si está configurado
- [ ] Verificar que no afecta performance negativamente

#### Documentation:
- [ ] Verificar que la documentación es clara y precisa
- [ ] Verificar que los ejemplos funcionan
- [ ] Verificar que está actualizada con el código
- [ ] Verificar formato Markdown

#### Architecture:
- [ ] Verificar que respeta la arquitectura del proyecto
- [ ] Verificar que no rompe separación de concerns
- [ ] Verificar que es escalable y mantenible
- [ ] Actualizar diagramas si es necesario

### 3.3 Ejecución de Tests

**El asistente DEBE:**

1. **Identificar tests relevantes:**
   - Tests unitarios del módulo afectado
   - Tests de integración si aplica
   - Tests end-to-end si es crítico

2. **Ejecutar tests:**
   ```bash
   # Si hay pytest
   pytest tests/ -v
   
   # Si hay tests específicos
   pytest tests/test_archivo.py::test_funcion -v
   
   # Si hay scripts de validación
   python bundle_validator.py  # ejemplo del proyecto
   ```

3. **Interpretar resultados:**
   - ✅ Todos los tests pasan → Fix correcto
   - ⚠️ Tests fallan → Analizar si es esperado (cambió comportamiento) o error
   - ❌ Nuevos tests fallan → El fix introdujo un problema

---

## 4. DOCUMENTACIÓN DE FIXES

### 4.1 Actualizar Documentación Relacionada

**El asistente DEBE actualizar:**

1. **Comentarios en código:**
   - Docstrings si cambió la firma de funciones
   - Comentarios inline si la lógica cambió significativamente
   - TODOs o FIXMEs si se resolvieron

2. **Documentación de usuario:**
   - README.md si cambió funcionalidad visible
   - Guías de uso si cambió el workflow
   - Ejemplos si cambiaron APIs o comandos

3. **Documentación técnica:**
   - Arquitectura si cambió estructura
   - API reference si cambió interfaz
   - CHANGELOG.md (si existe) con el fix

### 4.2 Crear Resumen del Fix

**El asistente DEBE generar un resumen:**

```markdown
## Fix: [Título Descriptivo]

**Tipo**: [Bug Fix / Security / Code Quality / etc.]
**Prioridad**: [Critical / High / Medium / Low]
**Reviewer**: [Nombre o referencia]

### Problema
[Descripción clara del problema identificado]

### Solución
[Descripción de la solución implementada]

### Archivos Modificados
- `archivo1.py`: [qué se cambió]
- `archivo2.md`: [qué se actualizó]

### Tests
- [ ] Tests existentes pasan
- [ ] Nuevos tests agregados: [descripción]
- [ ] Validación manual: [descripción]

### Verificación
- [ ] Fix resuelve el problema original
- [ ] No introduce regresiones
- [ ] Documentación actualizada
- [ ] Código sigue estándares del proyecto

### Notas Adicionales
[Si hay algo importante que el reviewer deba saber]
```

---

## 5. CASOS ESPECIALES Y GUARDRAILS

### 5.1 Fixes que Afectan la Identidad de Panelin

**SI el fix afecta:**
- Sistema de instrucciones de Panelin
- Personalización por usuario (Mauro, Martin, Rami)
- Estilo de comunicación
- Fuente de verdad (Knowledge Base hierarchy)

**ENTONCES el asistente DEBE:**
1. ⚠️ **DETENER** y alertar al usuario
2. 📋 **EXPLICAR** qué se vería afectado
3. ❓ **CONSULTAR** si el cambio es intencional
4. ✅ **SOLO proceder** con aprobación explícita

### 5.2 Fixes que Afectan Knowledge Base

**SI el fix afecta:**
- Estructura de archivos JSON de KB
- Jerarquía de fuentes (Nivel 1, 2, 3)
- Fórmulas de cotización
- Precios o productos

**ENTONCES el asistente DEBE:**
1. ✅ **VERIFICAR** que respeta la jerarquía
2. ✅ **VALIDAR** formato JSON si aplica
3. ✅ **VERIFICAR** que no rompe referencias
4. ✅ **DOCUMENTAR** cambios en estructura si aplica

### 5.3 Fixes que Requieren Cambios en Múltiples Archivos

**SI el fix es global:**
1. ✅ **CREAR** plan detallado de todos los archivos
2. ✅ **IDENTIFICAR** orden de dependencias
3. ✅ **IMPLEMENTAR** en orden lógico
4. ✅ **VALIDAR** después de cada grupo de cambios
5. ✅ **TESTEAR** integración completa

### 5.4 Fixes de Seguridad

**SI es un fix de seguridad:**
1. ✅ **PRIORIZAR** sobre otros fixes
2. ✅ **VERIFICAR** que cierra completamente la vulnerabilidad
3. ✅ **CONSIDERAR** agregar tests de seguridad
4. ✅ **DOCUMENTAR** la vulnerabilidad y la solución
5. ✅ **VERIFICAR** que no introduce nuevas vulnerabilidades

### 5.5 Fixes que Requieren Dependencias Nuevas

**SI el fix requiere nueva dependencia:**
1. ✅ **VERIFICAR** que no hay conflicto con dependencias existentes
2. ✅ **AGREGAR** a `requirements.txt` con versión específica
3. ✅ **DOCUMENTAR** por qué se necesita
4. ✅ **VERIFICAR** compatibilidad con Python version del proyecto
5. ✅ **CONSIDERAR** impacto en tamaño/performance

---

## 6. FLUJO COMPLETO DE RESOLUCIÓN

### 6.1 Flujo Paso a Paso

```
1. RECIBIR feedback del reviewer
   ↓
2. LEER y ENTENDER completamente el fix solicitado
   ↓
3. CLASIFICAR tipo de fix y alcance
   ↓
4. ANALIZAR impacto (funcionalidad, arquitectura, dependencias, docs)
   ↓
5. VERIFICAR contexto del proyecto (Panelin identity, KB hierarchy)
   ↓
6. CREAR plan detallado del fix
   ↓
7. PRESENTAR plan al usuario (si es crítico) o proceder
   ↓
8. LEER archivos completos antes de modificar
   ↓
9. IMPLEMENTAR cambios paso a paso
   ↓
10. VALIDAR durante implementación (sintaxis, lógica)
    ↓
11. EJECUTAR tests relevantes
    ↓
12. VERIFICAR checklist de validación
    ↓
13. ACTUALIZAR documentación
    ↓
14. CREAR resumen del fix
    ↓
15. PREPARAR para commit (seguir Conventional Commits)
    ↓
16. PRESENTAR resultado final al usuario
```

### 6.2 Template de Respuesta al Reviewer

**Cuando el fix está completo, el asistente DEBE generar:**

```markdown
## ✅ Fix Implementado: [Título]

### Resumen
[Breve descripción del fix implementado]

### Cambios Realizados
- **Archivo**: `ruta/archivo.py`
  - Línea X: [cambio específico]
  - Línea Y: [cambio específico]

### Validación
- ✅ Sintaxis correcta
- ✅ Tests pasan: [lista de tests]
- ✅ No introduce regresiones
- ✅ Documentación actualizada

### Notas
[Si hay algo importante que el reviewer deba saber]

---

**¿Hay algo más que necesite ajustarse?**
```

---

## 7. MEJORES PRÁCTICAS ESPECÍFICAS DEL PROYECTO

### 7.1 Estructura de Archivos

**Respetar:**
```
project_root/
├── docs/              # Documentación
├── src/ or code/      # Código fuente
│   ├── agents/        # Agentes de IA
│   ├── validators/    # Validadores
│   └── utils/         # Utilidades
├── data/              # Datos y knowledge base
├── config/            # Configuraciones
├── output/            # Outputs generados
├── logs/              # Logs
└── archived/          # Archivos archivados
```

### 7.2 Convenciones de Código

**Python:**
- PEP 8 compliance
- Type hints cuando sea apropiado
- Docstrings en formato Google o NumPy
- Nombres descriptivos y en inglés
- Comentarios en español si el proyecto es en español

**Git:**
- Conventional Commits: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Siempre pull antes de push
- Nunca force push sin aprobación

### 7.3 Knowledge Base Management

**Reglas críticas:**
- Nivel 1 (Master) es la única fuente de verdad para precios/fórmulas
- NUNCA modificar Nivel 1 sin validación exhaustiva
- Nivel 2 es solo para cross-reference
- Nivel 3 es dinámico (web scraping)
- Documentar cualquier cambio en estructura de KB

### 7.4 Testing

**Cuando agregar tests:**
- ✅ Para nuevos fixes de bugs (reproducir el bug)
- ✅ Para nuevas funcionalidades
- ✅ Para cambios en lógica crítica (cotizaciones, cálculos)
- ⚠️ Para cambios menores de estilo/documentación (opcional)

---

## 8. HERRAMIENTAS Y COMANDOS ÚTILES

### 8.1 Validación de Código

```bash
# Python syntax check
python -m py_compile archivo.py

# Type checking (si hay mypy)
mypy archivo.py

# Linting (si hay flake8)
flake8 archivo.py

# Formatting (si hay black)
black archivo.py --check
```

### 8.2 Validación de JSON (Knowledge Base)

```bash
# Validar JSON
python -m json.tool archivo.json > /dev/null

# Validar schema (si hay)
python bundle_validator.py archivo.json
```

### 8.3 Git Operations

```bash
# Ver estado
git status

# Ver cambios
git diff

# Ver cambios staged
git diff --staged

# Verificar antes de commit
git status
git diff --staged
```

### 8.4 Testing

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar test específico
pytest tests/test_archivo.py::test_funcion -v

# Con coverage
pytest tests/ --cov=src --cov-report=html
```

---

## 9. CHECKLIST FINAL ANTES DE CONSIDERAR FIX COMPLETO

**El asistente DEBE verificar:**

### Código
- [ ] El fix resuelve el problema identificado por el reviewer
- [ ] El código compila/valida sin errores
- [ ] No introduce nuevos bugs o regresiones
- [ ] Sigue las convenciones del proyecto
- [ ] Tiene comentarios/documentación apropiada
- [ ] Maneja casos edge y errores apropiadamente

### Tests
- [ ] Tests existentes pasan
- [ ] Nuevos tests agregados si es apropiado
- [ ] Tests cubren el caso del fix

### Documentación
- [ ] README actualizado si cambió funcionalidad visible
- [ ] Docstrings actualizados si cambió API
- [ ] Comentarios actualizados si cambió lógica
- [ ] CHANGELOG actualizado (si existe)

### Git
- [ ] Cambios están staged apropiadamente
- [ ] Mensaje de commit sigue Conventional Commits
- [ ] No hay archivos temporales o de debug incluidos
- [ ] .gitignore está respetado

### Proyecto Específico
- [ ] Identidad de Panelin preservada (si aplica)
- [ ] Knowledge Base hierarchy respetada (si aplica)
- [ ] Arquitectura del proyecto respetada
- [ ] Dependencias actualizadas si es necesario

---

## 10. EJEMPLOS DE FIXES COMUNES

### Ejemplo 1: Bug Fix - Error en Cálculo

**Reviewer dice:**
> "La función `calcular_paneles()` tiene un error en la línea 45. Debería usar `math.ceil()` en lugar de `round()` para redondear hacia arriba."

**Proceso:**
1. ✅ Leer función completa para entender contexto
2. ✅ Verificar todas las referencias a `calcular_paneles()`
3. ✅ Cambiar `round()` por `math.ceil()` en línea 45
4. ✅ Verificar que `math` está importado
5. ✅ Ejecutar tests relacionados
6. ✅ Verificar que el cambio no afecta otros cálculos
7. ✅ Actualizar docstring si menciona el comportamiento

### Ejemplo 2: Code Quality - Mejorar Legibilidad

**Reviewer dice:**
> "Esta función es muy larga y difícil de seguir. Considera refactorizar en funciones más pequeñas."

**Proceso:**
1. ✅ Analizar función completa
2. ✅ Identificar responsabilidades separables
3. ✅ Crear funciones helper con nombres descriptivos
4. ✅ Refactorizar función principal para usar helpers
5. ✅ Verificar que funcionalidad se mantiene igual
6. ✅ Ejecutar tests
7. ✅ Actualizar docstrings

### Ejemplo 3: Security Fix - Validación de Input

**Reviewer dice:**
> "Falta validación de input en `procesar_cotizacion()`. Un usuario podría inyectar código malicioso."

**Proceso:**
1. ✅ Identificar todos los inputs de la función
2. ✅ Agregar validaciones apropiadas (sanitización, type checking)
3. ✅ Agregar manejo de errores para inputs inválidos
4. ✅ Agregar tests para casos maliciosos
5. ✅ Verificar que no rompe funcionalidad legítima
6. ✅ Documentar validaciones en docstring

### Ejemplo 4: Documentation Fix

**Reviewer dice:**
> "El README tiene instrucciones desactualizadas. El comando de instalación ya no funciona."

**Proceso:**
1. ✅ Verificar comando actual correcto
2. ✅ Probar que el comando funciona
3. ✅ Actualizar README con comando correcto
4. ✅ Verificar que otros pasos del README siguen siendo válidos
5. ✅ Actualizar ejemplos si es necesario

---

## 11. COMUNICACIÓN CON EL REVIEWER

### 11.1 Cuando el Fix Está Completo

**El asistente DEBE:**
1. ✅ Generar resumen claro del fix
2. ✅ Indicar qué archivos se modificaron
3. ✅ Confirmar que el problema está resuelto
4. ✅ Preguntar si hay algo más que ajustar

### 11.2 Cuando Hay Ambigüedad

**Si el feedback del reviewer no es claro:**
1. ✅ Intentar inferir la intención basándose en contexto
2. ✅ Si no es claro, hacer preguntas específicas:
   - "¿Te refieres a la línea X o Y?"
   - "¿Prefieres solución A o B?"
   - "¿Este cambio debe aplicarse también a [archivo relacionado]?"

### 11.3 Cuando el Fix Requiere Más Contexto

**Si se necesita información adicional:**
1. ✅ Buscar en el código base por referencias
2. ✅ Leer documentación relacionada
3. ✅ Analizar tests existentes para entender comportamiento esperado
4. ✅ Si aún falta contexto, preguntar al reviewer

---

## 12. MANTENIMIENTO DE CALIDAD

### 12.1 Revisión de Propio Trabajo

**Antes de marcar un fix como completo, el asistente DEBE:**
1. ✅ Releer el feedback original del reviewer
2. ✅ Verificar que el fix realmente resuelve el problema
3. ✅ Verificar que no se introdujeron problemas nuevos
4. ✅ Verificar que el código es de calidad
5. ✅ Verificar que la documentación está actualizada

### 12.2 Aprendizaje Continuo

**El asistente DEBE:**
1. ✅ Notar patrones en fixes solicitados
2. ✅ Aplicar lecciones aprendidas a futuros fixes
3. ✅ Mejorar la calidad del código proactivamente
4. ✅ Sugerir mejoras adicionales cuando sea apropiado (sin ser intrusivo)

---

## 13. CRITERIOS DE ÉXITO

Un fix está **perfectamente resuelto** cuando:

✅ **Funcionalidad:**
- El problema identificado está completamente resuelto
- No se introdujeron nuevos problemas
- La funcionalidad existente sigue funcionando

✅ **Calidad:**
- El código sigue las mejores prácticas
- Es legible y mantenible
- Tiene documentación apropiada

✅ **Validación:**
- Tests pasan (o se agregaron tests nuevos)
- Validaciones manuales se completaron
- No hay errores de sintaxis o lógica

✅ **Documentación:**
- Documentación actualizada
- Comentarios claros en código
- Resumen del fix creado

✅ **Proyecto:**
- Respeta arquitectura del proyecto
- Preserva identidad de Panelin (si aplica)
- Respeta jerarquía de Knowledge Base (si aplica)

✅ **Git:**
- Cambios están listos para commit
- Mensaje de commit sigue convenciones
- No hay archivos temporales

---

## 14. USO DE ESTAS INSTRUCCIONES

**Para el Asistente de IA:**

Estas instrucciones deben ser tu guía completa para resolver cualquier fix que un reviewer solicite. Sigue el proceso paso a paso, no te saltes validaciones, y siempre prioriza la calidad y la integridad del proyecto.

**Para el Usuario:**

Puedes referirte a este documento cuando quieras que el asistente resuelva fixes de forma perfecta. También puedes decir: "Sigue las instrucciones de PROMPT_REVIEWER_FIXES_INSTRUCTIONS.md" para asegurar que el asistente use este proceso completo.

---

## 15. ACTUALIZACIÓN DE ESTAS INSTRUCCIONES

Estas instrucciones deben actualizarse cuando:
- Se identifican nuevos patrones de fixes
- Cambia la arquitectura del proyecto
- Se agregan nuevas herramientas o procesos
- Se identifican mejores prácticas adicionales

**Última actualización**: [Fecha]
**Versión**: 1.0

---

**NOTA FINAL**: Estas instrucciones están diseñadas para crear el entorno de chat perfecto donde todos los fixes de reviewer se resuelven de forma completa, correcta, y profesional. Sigue este proceso meticulosamente para garantizar la más alta calidad en cada fix implementado.
