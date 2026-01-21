# 📊 BMC Matriz de Costos y Ventas 2026 - Knowledge Base

## 📋 Descripción

Esta knowledge base contiene información completa de costos y precios de venta extraída de la matriz de costos y ventas 2026 de BROMYROS. Incluye:

- **Costos de fábrica directo**: Precios de compra directa a fábrica
- **Precios web/stock**: Precios de venta para compras web o desde stock
- **Información de productos**: Códigos, nombres, categorías, espesores
- **Margenes y ganancias**: Información de márgenes aplicados

---

## 📁 Archivos Generados

- **`BMC_Matriz_Costos_Ventas_2026.json`**: Knowledge base principal en formato JSON
- **`parse_costos_ventas.py`**: Script Python para regenerar la KB desde el CSV

---

## 🏗️ Estructura del JSON

```json
{
  "meta": {
    "nombre": "BMC Uruguay - Matriz de Costos y Ventas 2026",
    "version": "1.0.0",
    "fecha_creacion": "2026-01-21",
    "fuente": "MATRIZ de COSTOS y VENTAS 2026.xlsx - BROMYROS.csv",
    "estadisticas": {
      "total_productos": 145,
      "productos_activos": 145,
      "familias": 13,
      "productos_con_costo_fabrica": 123,
      "productos_con_precio_web": 116
    }
  },
  "productos": [
    {
      "codigo": "IAGRO30",
      "nombre": "Isoroof FOIL 30 mm - Color Gris-Rojo",
      "estado": "ACT.",
      "categoria": {
        "tipo": "cubierta_liviana",
        "familia": "isoroof",
        "unidad": "m2",
        "variante": "foil"
      },
      "espesor_mm": "30",
      "costos": {
        "fabrica_directo": {
          "costo_m2_usd_iva": 28.18,
          "costo_con_aumento": 29.12,
          "costo_proximo_aumento": 32.04
        },
        "margen_porcentaje": "15%",
        "ganancia_usd": 4.2271
      },
      "precios": {
        "venta_iva": 32.41,
        "consumidor_iva_inc": 39.54,
        "web_venta_iva": 39.45,
        "web_venta_iva_inc": 48.13
      },
      "precio_metro_lineal": 30.9988096
    }
  ],
  "indice_familias": {
    "isoroof": ["IAGRO30", "IAGRO50", ...],
    "isodec_eps": ["ISD100EPS", ...],
    ...
  }
}
```

---

## 🔍 Campos Principales

### Meta
- **nombre**: Nombre de la knowledge base
- **version**: Versión del formato
- **fecha_creacion**: Fecha de generación
- **estadisticas**: Resumen de productos procesados

### Productos

Cada producto contiene:

#### Identificación
- **codigo**: Código del producto (ej: "IAGRO30")
- **nombre**: Nombre completo del producto
- **estado**: Estado del producto ("ACT." = activo)
- **notas**: Notas adicionales
- **espesor_mm**: Espesor en milímetros (extraído del nombre)

#### Categorización
- **categoria.tipo**: Tipo de producto (cubierta_liviana, cubierta_pesada, fachada, accesorio, etc.)
- **categoria.familia**: Familia del producto (isoroof, isodec_eps, isodec_pir, isowall, etc.)
- **categoria.unidad**: Unidad de medida (m2, metro_lineal, unidad)
- **categoria.variante**: Variante del producto (foil, plus, colonial, standard)

#### Costos (Compras a Fábrica Directo)
- **costos.fabrica_directo.costo_m2_usd_iva**: Costo por m² en USD con IVA incluido
- **costos.fabrica_directo.costo_con_aumento**: Costo con aumento aplicado
- **costos.fabrica_directo.costo_proximo_aumento**: Costo con próximo aumento previsto
- **costos.margen_porcentaje**: Margen de ganancia porcentual
- **costos.ganancia_usd**: Ganancia en USD

#### Precios (Compras Web/Stock)
- **precios.venta_iva**: Precio de venta + IVA
- **precios.consumidor_iva_inc**: Precio consumidor con IVA incluido
- **precios.web_venta_iva**: Precio web + IVA
- **precios.web_venta_iva_inc**: Precio web con IVA incluido
- **precio_metro_lineal**: Precio por metro lineal (si aplica)

---

## 📊 Familias de Productos

La KB organiza productos en las siguientes familias:

1. **isoroof**: Isoroof (cubiertas livianas)
2. **isodec_eps**: ISODEC/ISOPANEL EPS (cubiertas pesadas EPS)
3. **isodec_pir**: ISODEC PIR (cubiertas pesadas PIR)
4. **isowall**: Isowall (fachadas)
5. **isofrig**: IsoFrig (salas limpias)
6. **gotero**: Goteros (accesorios)
7. **canalon**: Canalones (accesorios)
8. **cumbrera**: Cumbreras (accesorios)
9. **babeta**: Babetas (accesorios)
10. **perfil**: Perfiles (accesorios)
11. **anclaje**: Anclajes (varillas, tuercas, arandelas, tacos, caballetes)
12. **otro**: Otros accesorios (cintas, siliconas, fletes, etc.)

---

## 🔧 Uso

### Regenerar la Knowledge Base

Si el CSV original se actualiza, regenera la KB ejecutando:

```bash
python3 parse_costos_ventas.py
```

### Buscar Productos por Código

```python
import json

with open('BMC_Matriz_Costos_Ventas_2026.json', 'r', encoding='utf-8') as f:
    kb = json.load(f)

# Buscar producto por código
codigo = "IAGRO30"
producto = next((p for p in kb["productos"] if p["codigo"] == codigo), None)

if producto:
    print(f"Producto: {producto['nombre']}")
    print(f"Costo fábrica: ${producto['costos']['fabrica_directo']['costo_m2_usd_iva']:.2f} USD/m²")
    print(f"Precio web: ${producto['precios']['web_venta_iva']:.2f} USD/m²")
```

### Buscar Productos por Familia

```python
# Buscar todos los productos ISOROOF
isoroof_products = [p for p in kb["productos"] if p["categoria"]["familia"] == "isoroof"]

for producto in isoroof_products:
    print(f"{producto['codigo']}: {producto['nombre']}")
```

### Obtener Costo de Fábrica Directo

```python
def obtener_costo_fabrica(codigo: str) -> float:
    producto = next((p for p in kb["productos"] if p["codigo"] == codigo), None)
    if producto and producto["costos"]["fabrica_directo"]["costo_m2_usd_iva"]:
        return producto["costos"]["fabrica_directo"]["costo_m2_usd_iva"]
    return None

costo = obtener_costo_fabrica("IAGRO30")
print(f"Costo fábrica: ${costo:.2f} USD/m²")
```

### Obtener Precio Web/Stock

```python
def obtener_precio_web(codigo: str) -> float:
    producto = next((p for p in kb["productos"] if p["codigo"] == codigo), None)
    if producto and producto["precios"]["web_venta_iva"]:
        return producto["precios"]["web_venta_iva"]
    return None

precio = obtener_precio_web("IAGRO30")
print(f"Precio web: ${precio:.2f} USD/m²")
```

---

## 📈 Estadísticas Actuales

- **Total productos**: 145
- **Productos activos**: 145
- **Familias**: 13
- **Productos con costo fábrica**: 123
- **Productos con precio web**: 116

---

## ⚠️ Notas Importantes

1. **Productos excluidos**: Los productos marcados como "NO SUBIR" o "DESCONTINUADO" fueron excluidos automáticamente
2. **Valores nulos**: Algunos productos pueden no tener todos los campos completos (costos o precios)
3. **Unidades**: 
   - La mayoría de productos usan m² como unidad
   - Accesorios como goteros, canalones, perfiles usan metro_lineal
   - Anclajes y algunos accesorios usan unidad
4. **IVA**: Todos los precios incluyen IVA (22% en Uruguay)
5. **Moneda**: Todos los valores están en USD

---

## 🔄 Actualización

Para actualizar la knowledge base:

1. Actualizar el archivo CSV original
2. Ejecutar: `python3 parse_costos_ventas.py`
3. El nuevo JSON se generará con la fecha actual

---

## 📚 Integración con Panelin

Esta knowledge base puede ser usada junto con `BMC_Base_Conocimiento_GPT-2.json` para:

- Obtener costos de fábrica directo para cotizaciones especiales
- Consultar precios web/stock para ventas online
- Validar márgenes y ganancias
- Comparar precios entre diferentes canales de venta

**Recomendación**: Usar esta KB como referencia complementaria, manteniendo `BMC_Base_Conocimiento_GPT-2.json` como fuente primaria de precios de venta al público.

---

**Última actualización**: 2026-01-21  
**Versión**: 1.0.0
