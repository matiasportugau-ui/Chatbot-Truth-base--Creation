# 🔄 Script de Consolidación de Knowledge Base

Script para consolidar múltiples archivos JSON de Knowledge Base en uno solo.

## 🚀 Uso Rápido

```bash
# Consolidar KB (desde raíz del proyecto)
python scripts/consolidar_kb_v5.py
```

## 📋 Opciones

```bash
# Consolidar con nombre de archivo específico
python scripts/consolidar_kb_v5.py --output mi_kb_consolidada.json

# Solo validar (sin consolidar)
python scripts/consolidar_kb_v5.py --validate-only

# Especificar ruta base diferente
python scripts/consolidar_kb_v5.py --base-path /ruta/a/archivos

# Ayuda
python scripts/consolidar_kb_v5.py --help
```

## 📂 Archivos que Consolida

El script consolida estos 3 archivos en uno solo:

1. **BMC_Base_Conocimiento_GPT-2.json** (Nivel 1 - Master)
2. **BMC_Base_Unificada_v4.json** (Nivel 2 - Validación)
3. **panelin_truth_bmcuruguay_web_only_v2.json** (Nivel 3 - Dinámico)

## ✅ Resultado

Genera:
- **BMC_Base_Conocimiento_CONSOLIDADA_v5.0_YYYYMMDD.json** - KB consolidada
- **REPORTE_CONSOLIDACION_KB_v5.0.txt** - Reporte de consolidación

## 🔍 Validaciones

El script valida automáticamente:
- ✅ Precios completos para todos los productos
- ✅ Fórmulas de cotización requeridas
- ✅ Estructura correcta del JSON
- ✅ Consistencia entre fuentes

## 📊 Ejemplo de Salida

```
============================================================
🔄 CONSOLIDANDO KNOWLEDGE BASE v5.0
============================================================

📂 Cargando archivos...

✅ Cargado: BMC_Base_Conocimiento_GPT-2.json (125.3 KB)
✅ Cargado: BMC_Base_Unificada_v4.json (89.7 KB)
✅ Cargado: panelin_truth_bmcuruguay_web_only_v2.json (45.2 KB)

🔀 Consolidando productos...

📦 Base Nivel 1: 48 productos
📦 Después Nivel 2: 48 productos (validaciones agregadas)
📦 Después Nivel 3: 35 productos con precios actualizados

✅ Consolidación completada!
📊 Productos consolidados: 48
📐 Fórmulas incluidas: 9
📋 Reglas de negocio: 7

============================================================
🔍 VALIDANDO CONSISTENCIA
============================================================

💰 Validando precios...
  ✅ Todos los productos tienen precios

📐 Validando fórmulas...
  ✅ Todas las fórmulas presentes (4)

🏗️  Validando estructura...
  ✅ Estructura completa

------------------------------------------------------------
✅ VALIDACIÓN EXITOSA: Sin errores ni advertencias

✅ Archivo guardado: BMC_Base_Conocimiento_CONSOLIDADA_v5.0_20260123.json
📦 Tamaño: 156.8 KB
📍 Ruta: /home/user/Chatbot-Truth-base--Creation/BMC_Base_Conocimiento_CONSOLIDADA_v5.0_20260123.json

🎉 ¡CONSOLIDACIÓN EXITOSA!

📋 PRÓXIMOS PASOS:
  1. Revisar archivo consolidado
  2. Backup de archivos antiguos
  3. Subir a GPT Builder
  4. Testing
```

## ⚠️ Importante

**Antes de ejecutar:**
1. Asegúrate de tener los 3 archivos JSON en el directorio
2. Haz backup de los archivos originales
3. Verifica que tienes Python 3.7+

**Después de ejecutar:**
1. Revisa el archivo consolidado
2. Verifica el reporte de consolidación
3. Haz testing antes de usar en producción

## 🐛 Troubleshooting

**Error: "Archivo no encontrado"**
```bash
# Verifica que estás en el directorio correcto
ls -la *.json

# O especifica la ruta base
python scripts/consolidar_kb_v5.py --base-path /ruta/completa
```

**Error: "JSON inválido"**
```bash
# Valida el JSON manualmente
python -m json.tool BMC_Base_Conocimiento_GPT-2.json
```

**Quiero revertir cambios**
```bash
# Restaura desde backup
cp kb_backup_20260123/*.json .
```

## 📚 Más Información

Ver documentación completa en:
- `ANALISIS_UN_ARCHIVO_VS_MULTIPLES.md` - Análisis detallado
- `CONFIGURACION_OPTIMIZADA_GPT.md` - Configuración completa

## 📞 Soporte

Si encuentras problemas, revisa:
1. Logs de ejecución del script
2. REPORTE_CONSOLIDACION_KB_v5.0.txt
3. Documentación en ANALISIS_UN_ARCHIVO_VS_MULTIPLES.md
