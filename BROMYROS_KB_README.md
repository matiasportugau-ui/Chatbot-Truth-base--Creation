# BROMYROS - Base de Conocimiento de Costos y Precios 2026

## 📋 Descripción

Base de conocimiento generada desde la matriz de costos y ventas BROMYROS 2026. Contiene información de costos de fábrica directa y precios para empresas, particulares y web/stock.

## 📊 Estructura

### Meta Información
- **Nombre**: BROMYROS - Matriz de Costos y Ventas 2026
- **Versión**: 1.0
- **Fecha**: 2026-01-21
- **Fuente**: MATRIZ de COSTOS y VENTAS 2026.xlsx - BROMYROS.csv

### Reglas de Precios

#### Empresas
- **Descripción**: Empresas descuentan IVA
- **Precio a usar**: `precios.empresa.venta_iva`
- **Campo**: Precio + IVA (las empresas descuentan el IVA)

#### Particulares
- **Descripción**: Particulares no descuentan IVA
- **Precio a usar**: `precios.particular.consumidor_iva_inc`
- **Campo**: Precio con IVA incluido

#### Cotizaciones
- **Regla CRÍTICA**: SIEMPRE usar `precios.empresa.venta_iva` para cotizar
- **IVA**: 22% (0.22)
- **Proceso**: Usar precio + IVA como base y agregar IVA al final del cálculo

#### Web/Stock
- **Descripción**: Precios para compras web o stock
- **Campos**: 
  - `precios.web_stock.web_venta_iva`
  - `precios.web_stock.web_venta_iva_inc`

### Costos

#### Fábrica Directa
- **Campo**: `costos.fabrica_directo.costo_m2_usd_iva`
- **Descripción**: Costo por m² en USD con IVA incluido
- **Uso**: Para calcular márgenes y ganancias internas

## 📦 Estructura de Productos

Cada producto contiene:

```json
{
  "codigo": "IAGRO30",
  "nombre": "Isoroof FOIL 30 mm - Color Gris-Rojo",
  "espesor": "30",
  "status": "ACT.",
  "costos": {
    "fabrica_directo": {
      "costo_m2_usd_iva": 28.18,
      "costo_con_aumento": 29.12,
      "costo_proximo_aumento": 32.04
    }
  },
  "precios": {
    "empresa": {
      "venta_iva": 32.41,
      "nota": "Empresas descuentan IVA, usar precio + IVA"
    },
    "particular": {
      "consumidor_iva_inc": 39.54,
      "nota": "Particulares no descuentan IVA, usar precio IVA incluido"
    },
    "web_stock": {
      "web_venta_iva": null,
      "web_venta_iva_inc": null
    }
  },
  "margen": "15%",
  "ganancia": 4.2271,
  "notas": {
    "shopify": "Fata foto",
    "generales": "Tenemos paneles en el fondo para fotografiar",
    "cotizacion": "SIEMPRE usar 'venta_iva' para cotizar y agregar IVA al final"
  }
}
```

## 🗂️ Categorías de Productos

- **ISOROOF_FOIL**: Isoroof FOIL (2 productos)
- **ISOROOF**: Isoroof estándar (6 productos)
- **ISOROOF_PLUS**: Isoroof Plus (2 productos)
- **ISOROOF_COLONIAL**: Isoroof Colonial (1 producto)
- **ISODEC_EPS**: Isodec EPS (3 productos)
- **ISODEC_PIR**: Isodec PIR (12 productos)
- **ISOPANEL_EPS**: Isopanel EPS (1 producto)
- **ISOWALL**: Isowall (5 productos)
- **ISOWALL_PIR**: Isowall PIR (2 productos)
- **ISOFRIG**: IsoFrig (12 productos)
- **GOTERO_FRONTAL**: Goteros frontales (9 productos)
- **GOTERO_LATERAL**: Goteros laterales (15 productos)
- **GOTERO**: Otros goteros (8 productos)
- **BABETAS**: Babetas (5 productos)
- **CANALON**: Canalones (9 productos)
- **CUMBRERAS**: Cumbreras (4 productos)
- **PERFILES**: Perfiles varios (15 productos)
- **ANCLAJES**: Anclajes (7 productos)
- **ACCESORIOS**: Accesorios varios (4 productos)
- **FLETE**: Flete (1 producto)
- **EPS_PAQUETES**: Paquetes EPS (1 producto)
- **OTROS**: Otros productos (14 productos)

**Total**: 138 productos en 22 categorías

## 🔍 Uso para Agentes Internos

### Obtener Costo de Fábrica
```json
producto.costos.fabrica_directo.costo_m2_usd_iva
```

### Obtener Precio para Empresa
```json
producto.precios.empresa.venta_iva
```

### Obtener Precio para Particular
```json
producto.precios.particular.consumidor_iva_inc
```

### Obtener Precio Web/Stock
```json
producto.precios.web_stock.web_venta_iva
// o
producto.precios.web_stock.web_venta_iva_inc
```

## ⚠️ Reglas Importantes

1. **Para Cotizaciones**: SIEMPRE usar `precios.empresa.venta_iva` y agregar IVA (22%) al final
2. **Para Empresas**: Usar `precios.empresa.venta_iva` (descuentan IVA)
3. **Para Particulares**: Usar `precios.particular.consumidor_iva_inc` (IVA incluido)
4. **Costos Internos**: Usar `costos.fabrica_directo.costo_m2_usd_iva` para cálculos de margen

## 📝 Notas

- Los precios web/stock pueden ser `null` si no están disponibles
- El campo `status` indica si el producto está activo ("ACT.")
- Las notas contienen información adicional sobre el producto (Shopify, generales, cotización)
- El espesor se extrae automáticamente del nombre del producto

## 🔄 Actualización

Para actualizar la base de conocimiento:

1. Actualizar el archivo CSV: `MATRIZ de COSTOS y VENTAS 2026.xlsx - BROMYROS.csv`
2. Ejecutar el script: `python3 create_bromyros_kb.py`
3. El nuevo archivo JSON se generará: `BROMYROS_Base_Costos_Precios_2026.json`

## 📚 Integración con Panelin

Este archivo puede ser usado como Knowledge Base adicional para agentes internos que necesiten:
- Consultar costos de fábrica
- Calcular márgenes y ganancias
- Obtener precios diferenciados por tipo de cliente
- Acceder a precios web/stock

**Nota**: Este archivo contiene información sensible de costos y márgenes. NO debe ser compartido con clientes externos.
