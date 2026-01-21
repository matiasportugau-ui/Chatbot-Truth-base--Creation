# 📊 Guía: Base de Conocimiento de Costos y Precios por Proveedor

## 📋 Descripción

Este sistema analiza matrices de costos y ventas (CSV exportados desde Excel) donde cada pestaña representa un proveedor diferente. Extrae y organiza:

- **Costos para compras a fábrica directo**
- **Precios para compras web o stock**

## 🗂️ Estructura de Archivos

### Archivos Generados

1. **`BMC_Base_Costos_Precios_BROMYROS.json`**
   - Base de conocimiento para el proveedor BROMYROS
   - Contiene todos los productos organizados por sección
   - Incluye costos y precios estructurados

2. **`resumen_analisis_costos_BROMYROS.json`**
   - Resumen estadístico del análisis
   - Total de productos por sección
   - Productos con costos/precios disponibles

3. **`BMC_Base_Costos_Precios_UNIFICADA.json`** (si procesas múltiples proveedores)
   - Base de conocimiento unificada de todos los proveedores
   - Estructura: `proveedores -> secciones -> productos`

## 🔧 Scripts Disponibles

### 1. `analizar_matriz_costos.py`

Analiza un archivo CSV individual (un proveedor).

**Uso:**
```bash
python3 analizar_matriz_costos.py
```

**Requisitos:**
- Archivo CSV con nombre: `MATRIZ de COSTOS y VENTAS 2026.xlsx - BROMYROS.csv`
- O modificar el script para usar otro nombre de archivo

**Salida:**
- `BMC_Base_Costos_Precios_BROMYROS.json`
- `resumen_analisis_costos_BROMYROS.json`

### 2. `procesar_multiples_proveedores.py`

Procesa automáticamente todos los archivos CSV de proveedores encontrados.

**Uso:**
```bash
python3 procesar_multiples_proveedores.py
```

**Formato esperado de archivos:**
```
MATRIZ de COSTOS y VENTAS 2026.xlsx - PROVEEDOR1.csv
MATRIZ de COSTOS y VENTAS 2026.xlsx - PROVEEDOR2.csv
MATRIZ de COSTOS y VENTAS 2026.xlsx - PROVEEDOR3.csv
```

**Salida:**
- `BMC_Base_Costos_Precios_UNIFICADA.json`
- `resumen_analisis_costos_UNIFICADO.json`

## 📊 Estructura de Datos

### Estructura del JSON Generado

```json
{
  "meta": {
    "nombre": "Base de Conocimiento - Costos y Precios por Proveedor",
    "version": "1.0",
    "fecha_creacion": "2026-01-21T...",
    "fuente": "MATRIZ de COSTOS y VENTAS 2026.xlsx"
  },
  "estructura_precios": {
    "compras_fabrica_directo": {
      "campos": [
        "costo_base_usd_iva",
        "costo_con_aumento_usd_iva",
        "costo_proximo_aumento_usd_iva"
      ]
    },
    "compras_web_stock": {
      "campos": [
        "venta_iva_usd",
        "consumidor_iva_inc_usd",
        "web_venta_iva_usd",
        "web_venta_iva_inc_usd"
      ]
    }
  },
  "proveedores": {
    "BROMYROS": {
      "nombre": "BROMYROS",
      "secciones": {
        "ISOROOF_FOIL": {
          "nombre": "ISOROOF_FOIL",
          "total_productos": 2,
          "productos": [
            {
              "codigo": "IAGRO30",
              "nombre": "Isoroof FOIL 30 mm - Color Gris-Rojo",
              "estado": "ACT.",
              "subir_web": true,
              "costos_fabrica_directo": {
                "costo_base_usd_iva": 28.18,
                "costo_con_aumento_usd_iva": 29.12,
                "costo_proximo_aumento_usd_iva": 32.04
              },
              "precios_web_stock": {
                "venta_iva_usd": 32.41,
                "consumidor_iva_inc_usd": 39.54,
                "web_venta_iva_usd": null,
                "web_venta_iva_inc_usd": null
              },
              "margen_porcentaje": 15.0,
              "ganancia_usd": 4.2271,
              "precios_metro_lineal_por_largo": {
                "1.5m": 39.54,
                "2.0m": 138.38,
                ...
              }
            }
          ]
        }
      }
    }
  }
}
```

## 📝 Campos Extraídos

### Costos (Compras a Fábrica Directo)

| Campo | Descripción | Columna CSV |
|-------|-------------|-------------|
| `costo_base_usd_iva` | Costo base por m² en USD + IVA | Col 5 |
| `costo_con_aumento_usd_iva` | Costo con aumento aplicado | Col 6 |
| `costo_proximo_aumento_usd_iva` | Costo del próximo aumento | Col 7 |

### Precios (Compras Web o Stock)

| Campo | Descripción | Columna CSV |
|-------|-------------|-------------|
| `venta_iva_usd` | Precio de venta + IVA | Col 11 |
| `consumidor_iva_inc_usd` | Precio consumidor IVA incluido | Col 12 |
| `web_venta_iva_usd` | Precio web + IVA | Col 15 |
| `web_venta_iva_inc_usd` | Precio web IVA incluido | Col 16 |

### Información Adicional

- `codigo`: Código del producto (ej: IAGRO30, IROOF50)
- `nombre`: Nombre completo del producto
- `estado`: Estado del producto (ACT., etc.)
- `subir_web`: Si debe subirse a la web (false si tiene "NO SUBIR")
- `margen_porcentaje`: Margen de ganancia (%)
- `ganancia_usd`: Ganancia en USD
- `precio_metro_lineal_usd`: Precio por metro lineal (si aplica)
- `precios_metro_lineal_por_largo`: Precios según largo (1.0m, 1.5m, 2.0m, etc.)

## 🔍 Secciones Identificadas

El sistema identifica automáticamente las siguientes secciones:

- `ISOROOF_FOIL` - Isoroof FOIL
- `ISOROOF` - Isoroof estándar
- `ISOROOF_PLUS` - Isoroof Plus
- `ISOROOF_COLONIAL` - Isoroof Colonial
- `ISOPANEL_EPS` - Isopanel EPS (Fachada)
- `ISODEC_EPS` - Isodec EPS
- `ISODEC_PIR` - Isodec PIR
- `ISOWALL` - Isowall
- `ISOFRIG` - IsoFrig
- `GOTERO_FRONTAL` - Goteros frontales
- `GOTERO_LATERAL` - Goteros laterales
- `GOTERO_SUPERIOR` - Goteros superiores
- `BABETAS` - Babetas
- `CANALONES` - Canalones
- `CUMBRERAS` - Cumbreras
- `PERFILES` - Perfiles
- `ANCLAJES` - Anclajes
- `FLETES` - Fletes
- `ACCESORIOS` - Accesorios varios

## 📈 Estadísticas del Análisis

El resumen incluye:

- Total de proveedores procesados
- Total de productos por proveedor
- Total de secciones por proveedor
- Productos con costos disponibles
- Productos con precios web disponibles

## 🚀 Próximos Pasos

### Para Agregar Más Proveedores

1. Exportar cada pestaña del Excel como CSV con formato:
   ```
   MATRIZ de COSTOS y VENTAS 2026.xlsx - NOMBRE_PROVEEDOR.csv
   ```

2. Ejecutar:
   ```bash
   python3 procesar_multiples_proveedores.py
   ```

3. El script encontrará automáticamente todos los archivos y generará la KB unificada.

### Para Integrar con Panelin

1. Subir `BMC_Base_Costos_Precios_UNIFICADA.json` a la Knowledge Base de Panelin
2. Actualizar instrucciones para consultar costos/precios por proveedor
3. Usar estructura: `proveedores[PROVEEDOR].secciones[SECCION].productos`

### Ejemplo de Consulta

```python
import json

with open('BMC_Base_Costos_Precios_UNIFICADA.json') as f:
    kb = json.load(f)

# Buscar producto por código
proveedor = "BROMYROS"
codigo = "IAGRO30"

for seccion, datos in kb["proveedores"][proveedor]["secciones"].items():
    for producto in datos["productos"]:
        if producto["codigo"] == codigo:
            print(f"Producto: {producto['nombre']}")
            print(f"Costo fábrica: {producto['costos_fabrica_directo']}")
            print(f"Precio web: {producto['precios_web_stock']}")
            break
```

## ⚠️ Notas Importantes

1. **Formato CSV**: El CSV debe tener exactamente la estructura esperada (3 líneas de headers, luego datos)

2. **Columnas**: El script asume columnas específicas. Si el formato cambia, actualizar `analizar_matriz_costos.py`

3. **Valores nulos**: Los valores vacíos o inválidos se guardan como `null` en el JSON

4. **Productos "NO SUBIR"**: Se marcan con `subir_web: false` pero se incluyen en la KB

5. **Precios por metro lineal**: Solo se extraen si están presentes en las columnas 21-41

## 📞 Soporte

Si necesitas ajustar el análisis para:
- Diferentes formatos de CSV
- Nuevas columnas
- Nuevas secciones de productos
- Integración con otros sistemas

Modifica `analizar_matriz_costos.py` según tus necesidades.
