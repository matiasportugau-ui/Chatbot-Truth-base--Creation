#!/usr/bin/env python3
"""Buscar PDFs pequeños para validar extracción"""

from pathlib import Path

dropbox = Path('/Users/matias/Library/CloudStorage/Dropbox/BMC - Uruguay/Cotizaciones')

print('Buscando PDFs más pequeños para validar extracción...')
print('=' * 70)

pdfs_info = []
for pdf_file in dropbox.rglob('*.pdf'):
    try:
        size = pdf_file.stat().st_size
        nombre = pdf_file.name.upper()
        
        # Filtrar solo paneles
        if any(p in nombre for p in ['ISODEC', 'ISOROOF', 'ISOPANEL', 'ISOWALL']):
            pdfs_info.append({
                'path': str(pdf_file),
                'nombre': pdf_file.name,
                'size_kb': size / 1024,
                'size_mb': size / (1024 * 1024)
            })
    except:
        continue

# Ordenar por tamaño (más pequeños primero)
pdfs_info.sort(key=lambda x: x['size_kb'])

print(f'Total PDFs encontrados: {len(pdfs_info)}')
print(f'\nTop 20 PDFs más pequeños:')
for idx, pdf in enumerate(pdfs_info[:20], 1):
    print(f'{idx}. {pdf["nombre"][:70]}')
    print(f'   Tamaño: {pdf["size_kb"]:.1f} KB ({pdf["size_mb"]:.2f} MB)')
    print()

# Guardar lista de PDFs pequeños
pequenos = pdfs_info[:50]
print(f'\nGuardando lista de 50 PDFs más pequeños...')
with open('pdfs_pequenos_lista.txt', 'w', encoding='utf-8') as f:
    for pdf in pequenos:
        f.write(f"{pdf['path']}\n")

print(f'✅ Lista guardada en: pdfs_pequenos_lista.txt')
