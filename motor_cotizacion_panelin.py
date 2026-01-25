#!/usr/bin/env python3
"""
Motor de Cotización Panelin
============================

Motor de cotización que usa la base de conocimiento de Files/ para generar
cotizaciones precisas basadas en la lógica validada.
"""

import json
import math
from pathlib import Path
from typing import Dict, Optional, List, Tuple

# Rutas a archivos de conocimiento
BASE_UNIFICADA = Path("Files /BMC_Base_Unificada_v4.json")
WEB_ONLY = Path("Files /panelin_truth_bmcuruguay_web_only_v2.json")
ALEROS = Path("Files /Aleros -2.rtf")


class MotorCotizacionPanelin:
    """Motor de cotización usando base de conocimiento validada"""
    
    def __init__(self):
        self.base_unificada = self._cargar_base_unificada()
        self.web_only = self._cargar_web_only()
        self.reglas_aleros = self._cargar_reglas_aleros()
        
    def _cargar_base_unificada(self) -> Dict:
        """Carga BMC_Base_Unificada_v4.json"""
        try:
            with open(BASE_UNIFICADA, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error cargando base unificada: {e}")
            return {}
    
    def _cargar_web_only(self) -> Dict:
        """Carga panelin_truth_bmcuruguay_web_only_v2.json"""
        try:
            with open(WEB_ONLY, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error cargando web only: {e}")
            return {}
    
    def _cargar_reglas_aleros(self) -> Dict:
        """Carga reglas de aleros desde RTF"""
        try:
            import re
            with open(ALEROS, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read()
                # Extraer JSON del RTF
                json_match = re.search(r'\{.*\}', contenido, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
        except Exception as e:
            print(f"⚠️  Error cargando reglas aleros: {e}")
        return {}
    
    def identificar_producto(self, consulta: str, producto_especificado: str = None) -> Optional[Dict]:
        """Identifica el producto desde la consulta"""
        consulta_upper = consulta.upper()
        
        # Buscar en base unificada
        productos = self.base_unificada.get('productos', {})
        
        # Buscar por palabras clave
        # Verificar ISOWALL PIR primero (antes de ISODEC/ISOWALL genérico)
        if 'ISOWALL' in consulta_upper and 'PIR' in consulta_upper:
            return productos.get('ISOWALL_PIR')
        elif 'ISODEC' in consulta_upper or 'ISOWALL' in consulta_upper:
            if 'PIR' in consulta_upper:
                return productos.get('ISODEC_PIR')
            else:
                return productos.get('ISODEC_EPS')
        elif 'ISOPANEL' in consulta_upper:
            return productos.get('ISOPANEL_EPS')
        elif 'ISOFRIG' in consulta_upper:
            # Línea mencionada para cámaras frigoríficas / cerramientos.
            # Puede no tener precios/espesores cargados todavía: el motor debe responder con error controlado en esos casos.
            return productos.get('ISOFRIG_PIR')
        elif 'ISOROOF' in consulta_upper:
            if 'PLUS' in consulta_upper:
                return productos.get('ISOROOF_PLUS')
            elif 'FOIL' in consulta_upper:
                return productos.get('ISOROOF_FOIL')
            else:
                return productos.get('ISOROOF_3G')
        
        return None
    
    def obtener_precio(self, producto_key: str, espesor: str) -> Optional[float]:
        """Obtiene precio del producto y espesor"""
        # Primero intentar base unificada
        producto = self.base_unificada.get('productos', {}).get(producto_key)
        if producto:
            espesor_key = f"{espesor}mm" if not espesor.endswith('mm') else espesor
            espesor_info = producto.get('espesores', {}).get(espesor_key)
            if espesor_info:
                return espesor_info.get('precio_shopify')
        
        # Fallback a web_only
        catalog = self.web_only.get('catalog_snapshots', {}).get('bmcuruguay_shopify_public', {})
        # Buscar por handle aproximado
        for key, item in catalog.items():
            if producto_key.lower() in key:
                # Intentar extraer precio del display
                price_display = item.get('price_display', '')
                import re
                match = re.search(r'[\d.]+', price_display)
                if match:
                    return float(match.group(0))
        
        return None
    
    def calcular_cotizacion(
        self,
        producto: str,
        espesor: str,
        largo: float,
        ancho: float,
        tipo_fijacion: str = "hormigon",
        luz: float = None,
        alero_1: float = 0,
        alero_2: float = 0
    ) -> Dict:
        """Calcula cotización completa"""
        
        # Identificar producto
        producto_info = self.identificar_producto(producto)
        if not producto_info:
            return {'error': f'Producto no identificado: {producto}'}
        
        producto_key = None
        for key, info in self.base_unificada.get('productos', {}).items():
            if info == producto_info:
                producto_key = key
                break
        
        if not producto_key:
            return {'error': 'No se pudo identificar la clave del producto'}
        
        # Obtener precio
        precio_m2 = self.obtener_precio(producto_key, espesor)
        if not precio_m2:
            return {'error': f'No se encontró precio para {producto} {espesor}mm'}
        
        # Obtener especificaciones
        espesor_key = f"{espesor}mm" if not espesor.endswith('mm') else espesor
        espesor_info = producto_info.get('espesores', {}).get(espesor_key)
        if not espesor_info:
            return {'error': f'Espesor {espesor}mm no disponible para {producto}'}
        
        autoportancia = espesor_info.get('autoportancia', 0)
        ancho_util = producto_info.get('ancho_util', 1.12)
        
        # Calcular luz efectiva
        # Si se proporciona luz, usarla; si no, calcular del largo menos aleros
        if luz is not None:
            luz_efectiva = luz
        else:
            luz_efectiva = largo - alero_1 - alero_2
        
        # Validar autoportancia
        cumple_autoportancia = luz_efectiva <= autoportancia if autoportancia > 0 else None
        
        # Calcular materiales
        area_total = largo * ancho
        cantidad_paneles = math.ceil(ancho / ancho_util)
        
        # Calcular apoyos
        if autoportancia > 0:
            apoyos = math.ceil((largo / autoportancia) + 1)
        else:
            apoyos = 1  # Mínimo 1 apoyo
        
        # Calcular puntos de fijación
        sistema_fijacion = producto_info.get('sistema_fijacion', 'varilla_tuerca')
        
        if sistema_fijacion == 'varilla_tuerca':
            # Fórmula: ROUNDUP(((CANTIDAD * APOYOS) * 2) + (LARGO * 2 / 2.5))
            puntos_fijacion = math.ceil(((cantidad_paneles * apoyos) * 2) + (largo * 2 / 2.5))
            
            # Calcular accesorios de fijación
            varilla_ratio = producto_info.get('varilla_ratio', 4)
            varilla_cantidad = math.ceil(puntos_fijacion / varilla_ratio)
            
            if tipo_fijacion.lower() in ['hormigon', 'hormigón', 'concreto']:
                tuercas = puntos_fijacion * 1
                tacos = puntos_fijacion * 1
            else:  # metal
                tuercas = puntos_fijacion * 2
                tacos = 0
        else:
            # ISOROOF a madera (caballetes + tornillos)
            puntos_fijacion = 0
            varilla_cantidad = 0
            tuercas = 0
            tacos = 0
        
        # Calcular goteros
        gotero_frontal = math.ceil((cantidad_paneles * ancho_util) / 3)
        gotero_lateral = math.ceil((largo * 2) / 3)
        total_goteros = gotero_frontal + gotero_lateral
        
        # Calcular costos
        # Precios de referencia (deberían venir de la base de conocimiento)
        precios = {
            'varilla_3_8': 19.9,
            'tuerca_3_8': 2.0,
            'taco_3_8': 8.7,
            'gotero_frontal': 23.88,
            'silicona_pomo': 11.89
        }
        
        costo_paneles = precio_m2 * largo * cantidad_paneles * ancho_util
        costo_varillas = varilla_cantidad * precios['varilla_3_8']
        costo_tuercas = tuercas * precios['tuerca_3_8']
        costo_tacos = tacos * precios['taco_3_8']
        costo_goteros = total_goteros * precios['gotero_frontal']
        
        # Silicona (estimado)
        ml_total = (largo * 2) + (ancho * 2)  # Perímetro aproximado
        cantidad_silicona = math.ceil(ml_total / 8)
        costo_silicona = cantidad_silicona * precios['silicona_pomo']
        
        subtotal = (costo_paneles + costo_varillas + costo_tuercas + 
                   costo_tacos + costo_goteros + costo_silicona)
        
        iva = subtotal * 0.22
        total = subtotal + iva
        
        return {
            'producto': producto_info.get('nombre', producto),
            'espesor': espesor_key,
            'dimensiones': {
                'largo': largo,
                'ancho': ancho,
                'area': area_total,
                'luz_efectiva': luz_efectiva,
                'alero_1': alero_1,
                'alero_2': alero_2
            },
            'validacion': {
                'autoportancia': autoportancia,
                'luz_efectiva': luz_efectiva,
                'cumple_autoportancia': cumple_autoportancia,
                'advertencia': None if cumple_autoportancia else f'⚠️ Luz efectiva {luz_efectiva}m excede autoportancia {autoportancia}m'
            },
            'materiales': {
                'paneles': cantidad_paneles,
                'apoyos': apoyos,
                'puntos_fijacion': puntos_fijacion,
                'varillas': varilla_cantidad,
                'tuercas': tuercas,
                'tacos': tacos,
                'goteros_frontal': gotero_frontal,
                'goteros_lateral': gotero_lateral,
                'goteros_total': total_goteros,
                'silicona': cantidad_silicona
            },
            'costos': {
                'paneles': round(costo_paneles, 2),
                'varillas': round(costo_varillas, 2),
                'tuercas': round(costo_tuercas, 2),
                'tacos': round(costo_tacos, 2),
                'goteros': round(costo_goteros, 2),
                'silicona': round(costo_silicona, 2),
                'subtotal': round(subtotal, 2),
                'iva': round(iva, 2),
                'total': round(total, 2)
            },
            'precio_referencia': {
                'precio_m2': precio_m2,
                'fuente': 'BMC_Base_Unificada_v4.json (validado con 31 presupuestos)'
            }
        }
    
    def formatear_cotizacion(self, cotizacion: Dict) -> str:
        """Formatea la cotización como texto"""
        if 'error' in cotizacion:
            return f"❌ Error: {cotizacion['error']}"
        
        texto = f"""
╔══════════════════════════════════════════════════════════════╗
║           COTIZACIÓN - {cotizacion['producto']:<30} ║
╚══════════════════════════════════════════════════════════════╝

📋 ESPECIFICACIONES:
   Producto: {cotizacion['producto']}
   Espesor: {cotizacion['espesor']}
   Dimensiones: {cotizacion['dimensiones']['largo']}m x {cotizacion['dimensiones']['ancho']}m
   Área total: {cotizacion['dimensiones']['area']:.2f} m²

✅ VALIDACIÓN TÉCNICA:
   Autoportancia: {cotizacion['validacion']['autoportancia']}m
   Luz efectiva: {cotizacion['validacion']['luz_efectiva']}m
   {'✅ CUMPLE autoportancia' if cotizacion['validacion']['cumple_autoportancia'] else '⚠️ ' + cotizacion['validacion']['advertencia']}

📦 MATERIALES:
   • Paneles: {cotizacion['materiales']['paneles']} unidades
   • Apoyos: {cotizacion['materiales']['apoyos']}
   • Varillas 3/8": {cotizacion['materiales']['varillas']} unidades
   • Tuercas: {cotizacion['materiales']['tuercas']} unidades
   • Tacos: {cotizacion['materiales']['tacos']} unidades
   • Goteros frontal: {cotizacion['materiales']['goteros_frontal']} unidades
   • Goteros lateral: {cotizacion['materiales']['goteros_lateral']} unidades
   • Silicona: {cotizacion['materiales']['silicona']} pomos

💰 COSTOS:
   Paneles ({cotizacion['precio_referencia']['precio_m2']}/m²):     ${cotizacion['costos']['paneles']:>10.2f}
   Varillas:                                    ${cotizacion['costos']['varillas']:>10.2f}
   Tuercas:                                     ${cotizacion['costos']['tuercas']:>10.2f}
   Tacos:                                       ${cotizacion['costos']['tacos']:>10.2f}
   Goteros:                                     ${cotizacion['costos']['goteros']:>10.2f}
   Silicona:                                    ${cotizacion['costos']['silicona']:>10.2f}
   ─────────────────────────────────────────────────────────────
   Subtotal:                                   ${cotizacion['costos']['subtotal']:>10.2f}
   IVA (22%):                                  ${cotizacion['costos']['iva']:>10.2f}
   ─────────────────────────────────────────────────────────────
   TOTAL:                                      ${cotizacion['costos']['total']:>10.2f}

📌 Nota: Precios basados en {cotizacion['precio_referencia']['fuente']}
"""
        return texto


def main():
    """Ejemplo de uso del motor"""
    motor = MotorCotizacionPanelin()
    
    print("=" * 70)
    print("🏗️  MOTOR DE COTIZACIÓN PANELIN")
    print("=" * 70)
    print("\nUsando base de conocimiento validada:")
    print("  ✅ BMC_Base_Unificada_v4.json (31 presupuestos reales)")
    print("  ✅ panelin_truth_bmcuruguay_web_only_v2.json (Shopify)")
    print("  ✅ Reglas técnicas de aleros\n")
    
    # Ejemplo: Input de Agustín Arbiza
    print("📋 Ejemplo: Cotización para Agustín Arbiza")
    print("   Producto: ISODEC EPS 100mm")
    print("   Dimensiones: 10m x 5m")
    print("   Luz: 4.5m")
    print("   Fijación: Hormigón\n")
    
    cotizacion = motor.calcular_cotizacion(
        producto="ISODEC EPS",
        espesor="100",
        largo=10.0,
        ancho=5.0,
        tipo_fijacion="hormigon"
    )
    
    if 'error' not in cotizacion:
        print(motor.formatear_cotizacion(cotizacion))
    else:
        print(f"❌ {cotizacion['error']}")


if __name__ == "__main__":
    main()
