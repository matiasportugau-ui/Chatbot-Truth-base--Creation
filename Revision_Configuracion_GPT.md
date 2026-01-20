# Revisión de Configuración GPT - Panelin Reloaded

## ✅ Lo que está BIEN

1. **Archivos cargados**: Veo que tienes archivos en Knowledge Base
2. **Interfaz**: Estás en la pestaña "Configurar" correctamente

## ⚠️ Problemas Detectados

### 1. **INSTRUCCIONES DEL SISTEMA** ❌ CRÍTICO

**Problema**: Las "Instrucciones" muestran una lista de checkboxes (tareas), NO las instrucciones reales del sistema.

**Lo que debería tener**:
- Las instrucciones completas de `Instrucciones_Sistema_Panelin_CopiarPegar.txt`
- Source of Truth
- Personalización (Mauro, Martin, Rami)
- Guardrails
- Fórmulas
- Comandos SOP
- Etc.

**Solución**: 
1. Abre el archivo `Instrucciones_Sistema_Panelin_CopiarPegar.txt`
2. Copia TODO el contenido
3. Pégalo en el campo "Instrucciones"
4. Verifica que no exceda 8000 caracteres (debería estar bien)

### 2. **DESCRIPCIÓN** ⚠️ MEJORABLE

**Actual**: "ENE2026"

**Recomendado**: 
```
Experto técnico en cotizaciones y sistemas constructivos BMC. Especializado en Isopaneles (EPS y PIR), Construcción Seca e Impermeabilizantes. Genera cotizaciones técnicas precisas.
```

### 3. **ARCHIVOS** ✅ Verificar

Necesitas verificar que estén cargados estos 7 archivos:

1. ✅ `BMC_Base_Conocimiento_GPT-2.json` (o `BMC_Base_Conocimiento_GPT.json`) - **MASTER**
2. ✅ `BMC_Base_Unificada_v4.json`
3. ✅ `BMC_Catalogo_Completo_Shopify (1).json`
4. ✅ `panelin_truth_bmcuruguay_web_only_v2.json`
5. ✅ `panelin_context_consolidacion_sin_backend.md`
6. ✅ `Aleros -2.rtf` (o convertido a .txt/.md)
7. ✅ `panelin_truth_bmcuruguay_catalog_v2_index.csv`

**Importante**: El archivo MASTER debe estar cargado PRIMERO o al menos presente.

### 4. **MODELO RECOMENDADO** ⚠️ FALTANTE

**Recomendado**: 
- `gpt-4-turbo` o `gpt-4o` (si GPT-5.2 Thinking no está disponible)
- O dejar en blanco si quieres que el usuario elija

### 5. **FRASES PARA INICIAR** ✅ OPCIONAL

Puedes agregar ejemplos como:
- "Hola, mi nombre es [nombre]"
- "Necesito cotizar ISODEC 100mm para un techo de 6m de luz"
- "¿Qué diferencia hay entre EPS y PIR?"

---

## 🔧 Pasos para Corregir

### Paso 1: Corregir Instrucciones (CRÍTICO)

1. Abre `Instrucciones_Sistema_Panelin_CopiarPegar.txt`
2. Selecciona TODO (Cmd+A / Ctrl+A)
3. Copia (Cmd+C / Ctrl+C)
4. Ve al campo "Instrucciones" en el GPT
5. Borra la lista de checkboxes
6. Pega las instrucciones completas
7. Verifica que se guardó correctamente

### Paso 2: Mejorar Descripción

Reemplaza "ENE2026" con:
```
Experto técnico en cotizaciones y sistemas constructivos BMC. Especializado en Isopaneles (EPS y PIR), Construcción Seca e Impermeabilizantes.
```

### Paso 3: Verificar Archivos

Asegúrate de que estos archivos estén cargados:
- `BMC_Base_Conocimiento_GPT-2.json` ⭐ (MASTER - debe estar)
- Los otros 6 archivos

### Paso 4: Configurar Modelo (Opcional)

En "Modelo recomendado", selecciona:
- `gpt-4-turbo` o `gpt-4o`

---

## ✅ Checklist Final

Antes de guardar, verifica:

- [ ] Instrucciones del sistema están completas (no solo checkboxes)
- [ ] Descripción es clara y descriptiva
- [ ] Archivo MASTER está cargado (`BMC_Base_Conocimiento_GPT-2.json`)
- [ ] Todos los archivos necesarios están cargados (7 archivos)
- [ ] Modelo recomendado está configurado (opcional)
- [ ] Frases para iniciar están configuradas (opcional)

---

## 🚨 CRÍTICO: Instrucciones

**El problema más importante** es que las Instrucciones tienen una lista de tareas en lugar de las instrucciones reales del sistema. Esto hará que el GPT no funcione correctamente.

**Solución inmediata**: Copiar y pegar el contenido completo de `Instrucciones_Sistema_Panelin_CopiarPegar.txt` en el campo "Instrucciones".
