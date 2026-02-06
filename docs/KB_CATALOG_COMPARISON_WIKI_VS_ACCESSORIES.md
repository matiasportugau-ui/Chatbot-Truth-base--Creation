# Knowledge Base: Wiki Catalog vs Current Accessories Catalog

**Objetivo:** Revisar diferencias entre `wiki/normalized_full` (CSV/JSON) y el catálogo actual usado por el GPT (`accessories_catalog.json`), y analizar beneficios y riesgos de incorporar el catálogo actualizado a la KB.

**Fecha:** 2026-02-06

---

## 1. Resumen comparativo

| Aspecto | wiki/normalized_full | accessories_catalog.json (actual) |
|--------|----------------------|------------------------------------|
| **Items** | 512 (JSON) / 513 filas (CSV) | 97 |
| **Alcance** | Catálogo completo: paneles + accesorios + perfilería + fijaciones + 379 filas sin categoría | Solo accesorios/perfilería/fijaciones para BOM |
| **Paneles** | 26 filas (ISOROOF, ISODEC, ISOPANEL, ISOWALL, ISOFRIG, etc.) | 0 (paneles en BMC_Base_Conocimiento_GPT-2) |
| **Precio** | 508 filas con `sale_incl_vat` | 97 con `precio_unit_iva_inc` (94 con precio, 3 pendientes) |
| **Schema** | CSV-style: supplier, family, category, sub_family, sku, name, thickness_mm, length_m, unit_base, sale_incl_vat, cost_*, web_* | BOM-oriented: sku, name, tipo, unidad, largo_std_m, precio_unit_iva_inc, espesor_mm, compatibilidad[], uso, indices |
| **Normalización** | category/family a veces vacíos; unit_base inconsistente; SKUs duplicados | tipo estandarizado (gotero_frontal, babeta_adosar, etc.); compatibilidad ISODEC/ISOROOF/UNIVERSAL; uso techo/pared/general |
| **Uso en GPT** | No referenciado en instrucciones actuales | Nivel 1A KB; usado en F4 BOM (filtrar por tipo, compatibilidad, espesor_mm) |

---

## 2. Diferencias estructurales

### 2.1 Wiki (normalized_full)

- **Archivos:** `wiki/normalized_full.csv`, `wiki/normalized_full.json` (array de objetos, mismo contenido).
- **Columnas relevantes:** supplier, family, category, sub_family, sku, name, thickness_mm, length_m, unit_base, length_range, compatibility, composition, cost_excl_vat, cost_incl_vat, sale_excl_vat, **sale_incl_vat**, web_price_incl_vat, price_public.
- **Categorías con datos:** Panel (26), Perfileria / Terminaciones (70), Accesorio (12), Anclajes / Fijaciones (8), Perfileria / Gotero Frontal (7), PANEL EPS (4), PANEL PIR (3), Montante (2), etc. **379 filas con category vacío** (otros proveedores: SECO CENTER, HOMEKIT, etc.).
- **Problemas conocidos (según GPT_EVALUATION_REPORT_BOM_COMPLETA):**
  - SKUs duplicados (ej. "6805" para muchos ítems, "IROOF80-PLS" para distintos productos).
  - thickness_mm y length_m a veces texto ("30", "Estandar", "on demand ", "3,03").
  - family con espacios ("ISOROOF ").
  - unit_base: "Unit", "unit", "m2", "".

### 2.2 Accessories catalog (actual)

- **Archivo:** `accessories_catalog.json`.
- **Estructura:** meta + accesorios[] + indices (por tipo, compatibilidad, uso).
- **Campos clave para BOM:** tipo (gotero_frontal, babeta_adosar, cumbrera, varilla, etc.), compatibilidad (["ISODEC"], ["ISOROOF"], ["UNIVERSAL"]), espesor_mm (numérico o null), largo_std_m, unidad (unid, m2, ml, tubo, rollo).
- **Precio:** precio_unit_iva_inc (IVA incluido); precio_por_ml_iva_inc para perfiles.
- **Cobertura:** 97 ítems; 94 con precio; pensado para cotización BOM (bom_rules.json usa tipo/compatibilidad/espesor).

### 2.3 Coincidencia entre ambos

- **SKUs en ambos:** ~56 (muchos ítems del wiki son paneles u otros productos que no están en accessories_catalog).
- **Mismo “universo” accesorio/perfileria/fijación:** el reporte BOM indica que accessories_catalog se generó a partir de un CSV normalizado (normalized_full o similar); los 97 ítems son un subconjunto curado y normalizado del catálogo amplio.

---

## 3. Beneficios de usar el catálogo actualizado (wiki) en la KB

1. **Una sola fuente de datos:** Si el wiki es el export “oficial” actualizado, tenerlo en KB reduce desfases entre sistemas y la web.
2. **Más ítems con precio:** 508 filas con sale_incl_vat vs 97 en accessories_catalog → más productos valorizables (paneles, variantes, otros proveedores) si el GPT los usa.
3. **Paneles en el mismo archivo:** Los 26 paneles del wiki podrían servir como respaldo o cruce con BMC_Base_Conocimiento_GPT-2 (con regla clara de prioridad).
4. **Costes y márgenes:** Campos cost_excl_vat, margin_percent, etc. pueden servir para análisis interno (no para cotización cliente, según políticas actuales).
5. **Precio web:** web_price_incl_vat permite comparar “precio interno” vs “precio web” si se documenta cuál usar en cotización.

---

## 4. Riesgos de reemplazar o mezclar sin criterio

1. **Romper BOM actual:** Las instrucciones y bom_rules.json asumen `accessories_catalog.json` con campos **tipo**, **compatibilidad**, **uso**, **espesor_mm**. El wiki no tiene `tipo` ni índices; si el GPT usa solo el wiki, no puede filtrar “gotero_frontal ISODEC 100mm” y la F4 BOM deja de ser determinista.
2. **379 filas sin categoría:** Incluir el wiki tal cual puede hacer que el modelo devuelva ítems no clasificados (otros proveedores, chapas, estructuras) en respuestas de cotización.
3. **SKUs duplicados:** Mismo SKU para distintos productos (ej. IROOF80-PLS) → ambigüedad en “precio de X”; el GPT podría elegir el ítem equivocado.
4. **Dos fuentes de verdad para paneles:** Si tanto BMC_Base_Conocimiento_GPT-2 como el wiki tienen precios de paneles, hay que fijar explícitamente que Nivel 1 es BMC y el wiki es solo referencia o respaldo.
5. **Tamaño y ruido:** 512 ítems sin índices por tipo/uso/compatibilidad aumentan tokens y búsquedas menos precisas frente a 97 ítems indexados.
6. **Precios distintos:** Donde el wiki y accessories_catalog comparten ítem, sale_incl_vat y precio_unit_iva_inc pueden diferir (por fecha de export o redondeo); sin regla clara, el GPT puede dar dos precios para el mismo SKU.

---

## 5. Recomendaciones

### 5.1 No reemplazar accessories_catalog por el wiki en bruto

- Mantener **accessories_catalog.json** como Nivel 1A para BOM (perfilería, fijaciones, selladores) porque:
  - Tiene tipo, compatibilidad, uso y espesor_mm alineados con bom_rules.
  - Tiene índices que el GPT puede usar en instrucciones (“filtrar por tipo y compatibilidad”).
  - Evita duplicados y ítems no categorizados.

### 5.2 Usar el wiki como fuente para actualizar el catálogo

- **Regenerar** `accessories_catalog.json` a partir de `wiki/normalized_full.csv` (o .json) con un script que:
  - Filtre por category (y opcionalmente supplier) para quedarse con Accesorio, Perfileria, Anclajes, Gotero Frontal, etc.
  - Asigne **tipo** (gotero_frontal, babeta_adosar, cumbrera, varilla, etc.) a partir de name/category/sub_family.
  - Normalice **compatibilidad** (ISODEC, ISOROOF, UNIVERSAL) desde family/compatibility.
  - Normalice **unidad** (unid, m2, ml, tubo, rollo) desde unit_base.
  - Use **sale_incl_vat** como precio_unit_iva_inc; calcule precio_por_ml_iva_inc donde aplique.
  - Resuelva duplicados de SKU (regla: por ejemplo “más específico por espesor/family” o primera aparición).
  - Genere de nuevo **indices** por tipo, compatibilidad y uso.
- Así la KB se “mejora” con precios y ítems actualizados del wiki sin perder el esquema que el GPT y bom_rules necesitan.

### 5.3 Incorporar el wiki (o un derivado) como capa adicional, con prioridad clara

- **Opción A – Solo actualizar:** No subir el wiki a la KB; solo usarlo para regenerar accessories_catalog (y opcionalmente cruzar/actualizar BMC para paneles). El GPT sigue usando solo BMC + accessories_catalog + bom_rules.
- **Opción B – Wiki como referencia secundaria:** Subir un archivo “full_catalog” (wiki o un JSON derivado con mismo schema que accessories: tipo, compatibilidad, uso) como Nivel 2 o 3, con instrucción explícita: “Para BOM y cotización usar accessories_catalog (y BMC para paneles); para listar productos o buscar un SKU no encontrado, consultar full_catalog”.
- **Opción C – Paneles desde wiki:** Si se quiere unificar paneles en un solo catálogo, generar un “panels_catalog” desde el wiki (solo category=Panel, etc.) y documentar si reemplaza o complementa a BMC_Base_Conocimiento_GPT-2; en cualquier caso, definir cuál es la fuente de verdad de precios (ej. “BMC Nivel 1, panels_catalog solo validación”).

### 5.4 Checklist antes de subir el wiki a la KB

- [ ] Definir si el wiki es solo fuente de actualización o también un archivo en la KB.
- [ ] Si se sube: normalizar schema (tipo, compatibilidad, uso) o dejar claro que no se usa para BOM.
- [ ] Resolver duplicados de SKU en el wiki (regla de desempate documentada).
- [ ] Decidir qué precio usar en cotización (sale_incl_vat vs web_price_incl_vat) y documentarlo en instrucciones.
- [ ] Mantener prioridad: BMC para paneles, accessories_catalog para BOM; wiki/full_catalog como respaldo o lista ampliada.

---

## 6. Conclusión

- **Diferencias:** El wiki es un catálogo amplio (512 ítems, paneles + accesorios + muchos sin categoría) con schema plano; el actual es un catálogo reducido (97 ítems) con schema BOM y índices.
- **Beneficios de “mejorar la KB con el catálogo actualizado”:** Precios y lista de productos al día, una sola fuente de export, posibilidad de más ítems valorizables y de cruce con paneles.
- **Riesgos:** Romper la lógica BOM si se reemplaza accessories_catalog por el wiki sin mapear tipo/compatibilidad/uso; duplicados de SKU; dos fuentes de verdad para paneles; más ruido por ítems no categorizados.
- **Recomendación práctica:** Usar **wiki/normalized_full** como fuente para **regenerar y actualizar** `accessories_catalog.json` (y opcionalmente documentar o actualizar paneles en BMC). No sustituir accessories_catalog por el wiki en bruto en la KB. Opcionalmente añadir el wiki o un “full_catalog” derivado como capa secundaria con prioridad explícita en las instrucciones del GPT.

Si quieres, el siguiente paso puede ser esbozar el script de regeneración (entrada: normalized_full.csv, salida: accessories_catalog.json + índices) o una plantilla de “full_catalog” para subir a la KB como Nivel 2.
