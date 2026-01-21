# 📚 Guía Rápida: Agente Integrador de Conocimiento

## 🚀 Uso Rápido

### Ejecución Básica

```bash
# Revisar todas las conversaciones disponibles
python3 agente_integrador_conocimiento.py

# Revisar conversaciones desde una fecha específica
python3 agente_integrador_conocimiento.py --since 2026-01-01

# Limitar número de conversaciones
python3 agente_integrador_conocimiento.py --limit 500

# Especificar rutas personalizadas
python3 agente_integrador_conocimiento.py \
  --kb-path ./gpt_configs \
  --output ./integration_output
```

---

## 📋 Proceso Completo

El agente ejecuta 5 fases automáticamente:

1. **Revisión**: Extrae conversaciones de todas las fuentes
2. **Validación**: Calcula métricas de calidad
3. **Extracción**: Identifica conocimiento validado
4. **Integración**: Integra en KB siguiendo jerarquía
5. **Reporte**: Genera reporte completo

---

## 📊 Fuentes de Datos

### MongoDB (Opcional)
Requiere configuración en `.env`:
```bash
MONGODB_CONNECTION_STRING=mongodb://...
MONGODB_DATABASE_NAME=panelin
```

### SQLite
Base de datos: `ingestion_database.db`
- Tabla: `ingestion_table`
- Extrae automáticamente si existe

### Archivos JSON
Busca en: `./training_data/**/*.json`
- Formatos soportados: bundles, conversaciones simples

### Archivos CSV
Busca en: `./training_data/**/*.csv`
- Columnas esperadas: `user_query`, `chatbot_response`, `timestamp`

---

## ✅ Criterios de Validación

### Umbrales Mínimos (Configurables)
- **Relevance Score**: >= 0.8
- **Groundedness Score**: >= 0.8
- **Coherence Score**: >= 0.8
- **Confidence**: >= 0.8

### Conocimiento Aprobado
- ✅ Pasa todos los umbrales
- ✅ No tiene conflictos con KB
- ✅ Fuente validada (Nivel 1 consultado)

### Conocimiento Rechazado
- ❌ No pasa umbrales
- ❌ Tiene conflictos
- ❌ Fuente no validada

---

## 🔧 Jerarquía de Knowledge Base

### Nivel 1 - MASTER ⭐
- `BMC_Base_Conocimiento_GPT-2.json`
- **Única fuente autorizada**
- Se actualiza solo con conocimiento crítico validado

### Nivel 2 - VALIDACIÓN
- `BMC_Base_Unificada_v4.json`
- Solo para cross-reference
- No se actualiza directamente

### Nivel 3 - DINÁMICO
- `panelin_truth_bmcuruguay_web_only_v2.json`
- Precios y stock actualizados
- Validar contra Nivel 1 antes de usar

### Nivel 4 - SOPORTE
- Archivos MD, RTF, CSV
- Solo contexto complementario

---

## 📈 Tipos de Conocimiento Extraído

1. **Productos**: Nuevos productos, especificaciones
2. **Precios**: Precios actualizados validados
3. **Fórmulas**: Correcciones a fórmulas de cotización
4. **FAQ**: Preguntas frecuentes y respuestas
5. **Correcciones**: Correcciones explícitas de usuarios
6. **Reglas**: Nuevas reglas de negocio

---

## 📝 Reporte de Integración

El reporte se guarda en: `./integration_output/integration_report_YYYYMMDD_HHMMSS.json`

### Estructura del Reporte

```json
{
  "timestamp": "2026-01-21T10:00:00",
  "conversations_reviewed": 150,
  "knowledge_extracted": {
    "products": 5,
    "prices": 3,
    "formulas": 2,
    "faq": 8,
    "corrections": 4
  },
  "integration_results": {
    "level_1_updates": 3,
    "level_3_updates": 2,
    "faq_additions": 8,
    "rejected": 5
  },
  "quality_scores": {
    "average_relevance": 0.85,
    "average_groundedness": 0.82,
    "average_coherence": 0.88
  },
  "conflicts_detected": 2,
  "recommendations": [
    "Actualizar precio ISODEC 100mm en Nivel 1",
    "Agregar FAQ sobre autoportancia 150mm"
  ],
  "changes": [...]
}
```

---

## ⚠️ Importante

### Validación Manual Requerida
- **Todos los cambios** requieren revisión manual antes de aplicar
- El agente **NO modifica** archivos de KB directamente
- Genera reportes con recomendaciones

### Conflictos
- Si detecta conflictos, marca para revisión
- Nivel 1 siempre tiene prioridad
- Reporta diferencias pero no sobrescribe

### Seguridad
- Mantiene historial de cambios
- No elimina información existente
- Solo agrega o actualiza con validación

---

## 🔍 Troubleshooting

### "MongoDB not connected"
- Verificar `MONGODB_CONNECTION_STRING` en `.env`
- O simplemente continuar (MongoDB es opcional)

### "KnowledgeBaseEvaluator no disponible"
- Instalar dependencias: `pip install -r requirements.txt`
- Verificar que `kb_training_system` esté disponible

### "No conversations found"
- Verificar que existan archivos en `./training_data/`
- Verificar que `ingestion_database.db` exista
- Verificar conexión a MongoDB

### "Low quality scores"
- Revisar calidad de conversaciones fuente
- Ajustar umbrales si es necesario (en código)
- Revisar si KB actual tiene información suficiente

---

## 📚 Documentación Completa

Para más detalles, consultar:
- `PROMPT_AGENTE_INTEGRADOR_CONOCIMIENTO.md` - Prompt completo del agente
- `KB_TRAINING_SYSTEM_ARCHITECTURE.md` - Arquitectura del sistema
- `PANELIN_KNOWLEDGE_BASE_GUIDE.md` - Guía de Knowledge Base

---

**Última actualización**: 2026-01-21
