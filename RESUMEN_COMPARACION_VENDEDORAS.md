# Resumen: Comparación Vendedoras vs Sistema

## Estado del Sistema

### ✅ Implementado

1. **Búsqueda de PDFs**
   - Encuentra 6,406 PDFs relacionados con paneles en Dropbox
   - Filtra por productos: ISODEC, ISOROOF, ISOPANEL, ISOWALL
   - Ordena por tamaño (pequeños primero para validar)

2. **Procesamiento**
   - Procesa hasta 500 PDFs (aumentado desde 20)
   - Extrae información del nombre del archivo:
     - Producto (ISODEC EPS, ISOROOF 3G, etc.)
     - Espesor (100mm, 150mm, etc.)
     - Fecha y cliente
   - Genera presupuestos usando el motor con base de conocimiento

3. **Generación de Presupuestos**
   - ✅ Funciona correctamente
   - Usa dimensiones por defecto (10m x 5m) cuando no están en el nombre
   - Calcula materiales, costos, IVA y totales
   - Incluye validación de autoportancia

### ⚠️ Limitaciones Actuales

1. **Extracción de Totales de PDFs**
   - Los PDFs están dando timeout al leerlos
   - Incluso PDFs pequeños (50-70 KB) fallan
   - Posibles causas:
     - PDFs corruptos o con formato complejo
     - Imágenes escaneadas (requieren OCR)
     - Protección o encriptación

2. **OCR (Opcional)**
   - Código preparado para OCR con `pytesseract` y `pdf2image`
   - Requiere instalación:
     ```bash
     brew install tesseract tesseract-lang  # macOS
     pip3 install pdf2image pytesseract Pillow
     ```
   - Se activa automáticamente si el texto extraído está vacío

## Resultados Actuales

- **PDFs encontrados**: 6,406
- **PDFs procesados**: 500 (configurable)
- **Presupuestos generados**: ~90% de los PDFs con producto/espesor identificado
- **Comparaciones realizadas**: 0 (no se pueden extraer totales de PDFs)

## Archivos Generados

1. `comparacion_vendedoras_sistema.json` - Resultados completos
2. `pdfs_pequenos_lista.txt` - Lista de PDFs pequeños para validación
3. `prueba_pdfs_pequenos_resultados.json` - Resultados de prueba con PDFs pequeños

## Próximos Pasos Recomendados

1. **Instalar OCR** (si los PDFs son imágenes):
   ```bash
   ./instalar_ocr.sh
   ```

2. **Probar con PDFs específicos** que se sepa que tienen texto extraíble

3. **Mejorar extracción**:
   - Probar con diferentes librerías (pdfplumber, camelot)
   - Extraer solo última página (donde suele estar el total)
   - Usar patrones más flexibles para buscar totales

4. **Validar presupuestos generados**:
   - Comparar manualmente algunos casos
   - Ajustar lógica de cotización según diferencias encontradas

## Uso

```bash
# Procesar comparación completa (500 PDFs)
python3 comparar_cotizaciones_vendedoras.py

# Probar con PDFs pequeños (10 PDFs)
python3 probar_pdfs_pequenos.py

# Buscar PDFs pequeños
python3 buscar_pdfs_pequenos.py
```

## Notas Técnicas

- Timeout reducido a 10 segundos para lectura de PDFs
- Solo lee primera y última página (más rápido)
- OCR se activa automáticamente si texto está vacío
- Usa dimensiones por defecto (10m x 5m) cuando no están disponibles
