# Análisis GPT Panelin - Sistema de Cotización v3.0
**Fecha:** 2026-02-06  
**Autor:** Análisis automático por Cloud Agent  
**Branch:** `cursor/optimizaci-n-sistema-cotizaci-n-30d8`

---

## 1. DIAGNÓSTICO DEL SISTEMA ACTUAL

### 1.1 Lo que funciona bien ✅

| Componente | Estado | Detalles |
|-----------|--------|---------|
| KB Master (BMC_Base_Conocimiento_GPT-2.json) | ✅ Sólido | 8 familias de paneles con precios, autoportancia, fórmulas |
| Jerarquía de fuentes (5 niveles) | ✅ Bien definida | Prioridad clara: Master > Catálogo > Validación > Dinámico > Soporte |
| Política de IVA | ✅ Triple enfatizada | IVA 22% ya incluido en precios unitarios - regla reforzada 3 veces |
| Quotation Calculator (Python) | ✅ Robusto | Precisión Decimal, checksum, calculation_verified flag |
| Fórmulas de cotización | ✅ Codificadas | paneles, apoyos, puntos fijación, goteros, remaches, silicona |
| Tests unitarios | ✅ 29/33 pasan | 4 fallos pre-existentes por largo mínimo en test data |

### 1.2 Problemas detectados ❌

| # | Problema | Impacto | Severidad |
|---|---------|---------|-----------|
| 1 | **Accesorios sin precio en KB** | GPT dice "pendiente de precio" para babetas, encuentros, tornillería | 🔴 Alto |
| 2 | **Action no devuelve BOM valorizado** | Solo calcula paneles, no accesorios con precio×cantidad | 🔴 Alto |
| 3 | **Reglas BOM parcialmente codificadas** | Longitudes estándar de perfiles, solape y desperdicio no formalizados | 🟡 Medio |
| 4 | **Autoportancia fuera del flujo** | Validación es "conceptual", no integrada al cálculo automático | 🟡 Medio |
| 5 | **Campos no normalizados** | Unidades mixtas (m², m2, Unit, unit), falta flag IVA, falta largo_std | 🟡 Medio |
| 6 | **Token diet inexistente** | Instrucciones de 230 líneas, sin slash commands para cotización rápida | 🟠 Medio-bajo |
| 7 | **SKU duplicados en normalized_full.json** | Ej: SKU "6805" usado para 10+ ítems distintos | 🟡 Medio |
| 8 | **Familias con trailing spaces** | "ISOROOF " vs "ISOROOF", "ISODEC " vs "ISODEC" | 🟢 Bajo |

### 1.3 Datos cuantitativos del normalized_full.json

```
512 productos totales
├── 26 Paneles (con precios)
├── 70 Perfilería/Terminaciones (con precios ✅)
├── 12 Accesorios (con precios ✅)
├── 8 Fijaciones (con precios ✅)
├── 7 Goteros Frontales (con precios ✅)
├── 3 Montantes (con precios ✅)
└── 379 Sin categoría (paneles en formato diferente)

Familias únicas: 19 (con duplicados por trailing spaces)
Unidades: m2, m2 (con espacio), unit, Unit, None
```

---

## 2. SOLUCIONES IMPLEMENTADAS

### 2.1 accessories_catalog.json (NUEVO)
**Path:** `panelin/data/accessories_catalog.json`

Catálogo normalizado con 97 accesorios valorizados, extraídos de normalized_full.json:

| Sección | Items | Ejemplo |
|---------|-------|---------|
| perfileria_goterones | 34 | Gotero Frontal 100mm ISODEC $19.12 |
| babetas | 6 | Babeta ISODEC de Adosar $14.87 |
| canalones | 12 | Canalón Doble ISOROOF 50mm $89.29 |
| cumbreras | 3 | Cumbrera Roof 3G 3m $42.97 |
| perfiles_u | 10 | Perfil U 100mm 3m $15.15 |
| perfiles_especiales | 9 | Perfil Alu 5852 6.8m $77.15 |
| fijaciones | 8 | Varilla 3/8 1m $3.81, Tuerca $0.15 |
| selladores | 5 | Silicona Neutra $11.58 |

**Campos por ítem:**
```json
{
  "sku": "6838",
  "name": "Perf. Ch. Gotero Frontal 100mm - (3,03m)",
  "unidad": "unit",
  "largo_std_m": 3.03,
  "espesor_panel_mm": 100,
  "precio_unit_iva_inc": 19.12,
  "precio_unit_sin_iva": 15.67,
  "compatibilidad": ["ISODEC"],
  "proveedor": "BROMYROS"
}
```

### 2.2 bom_rules.json (NUEVO)
**Path:** `panelin/data/bom_rules.json`

Reglas paramétricas para 5 sistemas constructivos:

| Sistema | Producto Base | Espesores | Fijación |
|---------|--------------|-----------|----------|
| techo_isodec_eps | ISODEC_EPS | 100, 150, 200, 250 | varilla_tuerca |
| techo_isodec_pir | ISODEC_PIR | 50, 80, 120 | varilla_tuerca |
| techo_isoroof_3g | ISOROOF_3G | 30, 50, 80 | caballete_tornillo |
| pared_isopanel_eps | ISOPANEL_EPS | 50, 100, 150, 200 | varilla_tuerca |
| pared_isowall_pir | ISOWALL_PIR | 50, 80 | varilla_tuerca |

Cada sistema define:
- BOM completo con fórmulas paramátricas
- Tabla de autoportancia con validación integrada
- Largos estándar de piezas (3.0m, 3.03m)
- Reglas de redondeo (ceil siempre)
- Precios de referencia para fijaciones

### 2.3 bom_calculator.py (NUEVO)
**Path:** `panelin/tools/bom_calculator.py`

Funciones principales:
- `calculate_full_quote()` — 1 sola llamada devuelve BOM completo valorizado
- `validate_autoportancia()` — Validación integrada con recomendación
- `lookup_accessory_price()` — Búsqueda inteligente de precios (6 estrategias)

**Ejemplo de output (ISODEC EPS 100mm, 5m × 11m, metal):**
```
Quotation: BMC-20260206-AF2A2662
Area: 56.0 m² | 10 paneles
Autoportancia: CUMPLE (margen 9.1%)

Subtotal Paneles:    $2,579.92
Subtotal Perfilería: $  336.95
Subtotal Fijaciones: $  234.91
Subtotal Selladores: $   57.90
TOTAL (IVA inc):     $3,209.68
```

### 2.4 Schemas extendidos (ACTUALIZADO)
**Path:** `panelin/models/schemas.py`

Nuevos tipos:
- `BOMLineItem` — Item de BOM con categoría, unidad, precio
- `AutoportanciaResult` — Validación con cumple, margen, recomendación
- `FullQuotationResult` — Cotización completa con BOM + autoportancia
- `FullQuotationRequest` — Request con bom_preset y tipo_fijacion

### 2.5 Instrucciones GPT v3 optimizadas (NUEVO)
**Path:** `gpt_configs/INSTRUCCIONES_PANELIN_V3_OPTIMIZADAS.txt`

Cambios clave:
- Fuentes de verdad: 3 nuevos niveles (1B Accesorios, 1C Reglas BOM)
- Proceso de cotización reducido de narrativo a tabla compacta
- 7 slash commands nuevos (/cotizar, /accesorios, /autoportancia, /comparar...)
- Token diet: 5 reglas para reducir consumo
- BOM completo integrado en el flujo estándar

---

## 3. COMPARATIVA ANTES/DESPUÉS

| Dimensión | Antes (v2) | Después (v3) |
|-----------|-----------|-------------|
| **Accesorios con precio** | 5 (varilla, tuerca, taco, silicona, gotero) | **97** (todo el catálogo) |
| **BOM valorizado** | ❌ Solo paneles | ✅ Paneles + perfilería + fijaciones + selladores |
| **Autoportancia** | Manual/conceptual | ✅ Integrada con margen % y recomendación |
| **Llamadas API** | 2-3 (find_products + calculate_quote + lookup) | **1** (calculate_full_quote) |
| **Sistemas soportados** | Genérico | **5** específicos con reglas propias |
| **Slash commands** | 5 generales | **12** (7 nuevos para cotización rápida) |
| **Token cost estimado** | ~3000 tokens por cotización | ~1500 tokens (tabla compacta) |
| **Items sin precio** | ~70% de accesorios | **< 5%** (solo items sin dato en proveedor) |

---

## 4. DATOS NORMALIZADOS

### 4.1 Problemas de normalización detectados y resueltos

| Campo | Problema | Solución aplicada |
|-------|---------|-------------------|
| `unit_base` | Mixto: "m2", "m2 ", "Unit", "unit", null | Normalizado a "m2", "unit" lowercase, trim |
| `family` | Trailing spaces: "ISOROOF " | Trim en accessories_catalog |
| `sale_incl_vat` | Algunos null | Solo incluidos ítems con precio |
| `sku` | Duplicados (6805 para 10+ ítems) | Desambiguado por nombre+familia |
| `thickness_mm` | String "30" en vez de int 30 | Parseado a int donde aplica |
| `length_m` | "on demand" en paneles, "N/A" en accesorios | Extraído de nombre cuando posible |

### 4.2 Convenciones establecidas
```json
{
  "iva_incluido": true,
  "moneda": "USD",
  "unidades_validas": ["m2", "ml", "unit", "kit"],
  "redondeo_paneles": "ceil",
  "redondeo_perfiles": "ceil (por largo estándar de pieza)",
  "fijacion_perfileria_paso_cm": 30,
  "rendimiento_silicona_ml": 8,
  "pendiente_minima_techo_pct": 7
}
```

---

## 5. RECOMENDACIONES PENDIENTES

### 5.1 Prioridad Alta (próximo sprint)
1. **Extender Action API** para exponer `calculate_full_quote()` vía endpoint REST
2. **Resolver SKUs duplicados** en normalized_full.json (6805 aparece 15 veces)
3. **Agregar precios ISOFRIG** (actualmente "Consultar")

### 5.2 Prioridad Media
4. **Recargos por color/terminación** — Parametrizar como % sobre precio base
5. **Reglas de corte/solape** — Agregar solape_cm y desperdicio_% por perfil
6. **Tabla de cargas por zona** — Viento (categorías C1-C5), nieve (kg/m²)
7. **Exchange rate UYU** — Integrar tipo de cambio BCU para cotizar en pesos

### 5.3 Prioridad Baja
8. **Longitudes personalizadas** — Perfiles cortados a medida (no solo estándar)
9. **Multi-proveedor** — Soporte Barraca Parna junto a BROMYROS
10. **Historial de cotizaciones** — Persistencia en DB para analytics

---

## 6. ARCHIVOS MODIFICADOS/CREADOS

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| `panelin/data/accessories_catalog.json` | 🆕 Nuevo | 97 accesorios valorizados |
| `panelin/data/bom_rules.json` | 🆕 Nuevo | Reglas BOM para 5 sistemas |
| `panelin/tools/bom_calculator.py` | 🆕 Nuevo | Calculadora BOM completa |
| `panelin/models/schemas.py` | 📝 Actualizado | +4 nuevos TypedDict |
| `gpt_configs/INSTRUCCIONES_PANELIN_V3_OPTIMIZADAS.txt` | 🆕 Nuevo | Instrucciones optimizadas |
| `ANALISIS_GPT_COTIZACION_V3.md` | 🆕 Nuevo | Este documento |

---

## 7. CÓMO USAR

### 7.1 Para el GPT (Instructions)
Copiar el contenido de `gpt_configs/INSTRUCCIONES_PANELIN_V3_OPTIMIZADAS.txt` en las instrucciones del GPT.

### 7.2 Para la Action API
```python
from panelin.tools.bom_calculator import calculate_full_quote

result = calculate_full_quote(
    product_id="ISODEC_EPS",
    length_m=5.0,
    width_m=11.0,
    thickness_mm=100,
    bom_preset="techo_isodec_eps",
    tipo_fijacion="metal",
    luz_m=5.0,
)
# result contiene BOM completo con todos los precios
```

### 7.3 Para el Knowledge Base del GPT
Subir estos archivos como KB:
1. `BMC_Base_Conocimiento_GPT-2.json` (ya existe)
2. `panelin/data/accessories_catalog.json` (NUEVO)
3. `panelin/data/bom_rules.json` (NUEVO)
