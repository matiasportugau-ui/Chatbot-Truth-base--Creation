#!/bin/bash
# Script para instalar dependencias de OCR (opcional)

echo "Instalando dependencias para OCR..."
echo ""

# Verificar si estamos en macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detectado macOS"
    echo ""
    echo "1. Instalando tesseract (requiere Homebrew):"
    echo "   brew install tesseract tesseract-lang"
    echo ""
    echo "2. Instalando librerías Python:"
    pip3 install pdf2image pytesseract Pillow
    echo ""
    echo "✅ Instalación completada"
else
    echo "Para Linux/Windows, instala tesseract según tu distribución"
    echo "Luego ejecuta: pip3 install pdf2image pytesseract Pillow"
fi
