"""
Panelin BOM Calculator - Cotización completa con BOM valorizado.

Este módulo extiende el sistema de cotización para generar un Bill of Materials
completo con todos los accesorios, fijaciones y perfilería valorizados.

PRINCIPIO FUNDAMENTAL: El LLM NUNCA calcula - solo extrae parámetros.
Toda la aritmética financiera ocurre aquí con tipo Decimal para precisión garantizada.

Funciones principales:
1. calculate_full_quote() - Cotización completa con BOM
2. validate_autoportancia() - Validación de luz vs autoportancia
3. lookup_accessory_price() - Búsqueda de precios de accesorios
"""

import json
import math
import hashlib
import uuid
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

from panelin.models.schemas import (
    BOMLineItem,
    AutoportanciaResult,
    FullQuotationResult,
)


# Constants
DECIMAL_PLACES = Decimal('0.01')
DATA_DIR = Path(__file__).parent.parent / "data"
DEFAULT_KB_PATH = DATA_DIR / "panelin_truth_bmcuruguay.json"
ACCESSORIES_PATH = DATA_DIR / "accessories_catalog.json"
BOM_RULES_PATH = DATA_DIR / "bom_rules.json"


def _to_decimal(value) -> Decimal:
    """Convierte un valor a Decimal de forma segura."""
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Cannot convert {value} to Decimal: {e}")


def _round_currency(value: Decimal) -> Decimal:
    """Redondea un valor monetario a 2 decimales."""
    return value.quantize(DECIMAL_PLACES, rounding=ROUND_HALF_UP)


def _load_json(path: Path) -> Dict[str, Any]:
    """Carga un archivo JSON."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _generate_checksum(data: Dict[str, Any]) -> str:
    """Genera un checksum para verificar integridad de la cotización."""
    checksum_data = {
        "line_items": [
            {
                "sku": item.get("sku", ""),
                "cantidad": item.get("cantidad", 0),
                "total_iva_inc": item.get("total_iva_inc", 0),
            }
            for item in data.get("line_items", [])
        ],
        "total_iva_inc": data.get("total_iva_inc", 0),
    }
    json_str = json.dumps(checksum_data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()[:16]


def validate_autoportancia(
    espesor_mm: int,
    luz_m: float,
    producto_base: str,
    kb_path: Optional[Path] = None,
    bom_rules_path: Optional[Path] = None,
) -> AutoportanciaResult:
    """
    Valida si un panel cumple con autoportancia para la luz dada.

    Args:
        espesor_mm: Espesor del panel en mm
        luz_m: Distancia entre apoyos en metros
        producto_base: ID del producto (ej: ISODEC_EPS)
        kb_path: Path a la KB principal
        bom_rules_path: Path a las reglas BOM

    Returns:
        AutoportanciaResult con cumple/no cumple y recomendación
    """
    kb = _load_json(kb_path or DEFAULT_KB_PATH)
    bom_rules = _load_json(bom_rules_path or BOM_RULES_PATH)

    # Get autoportancia from KB first, then from BOM rules
    product = kb.get("products", {}).get(producto_base, {})
    espesores = product.get("espesores", {})
    espesor_data = espesores.get(str(espesor_mm), {})
    autoportancia_m = espesor_data.get("autoportancia")

    # Fallback to BOM rules
    if autoportancia_m is None:
        for sistema_key, sistema in bom_rules.get("sistemas", {}).items():
            if sistema.get("producto_base") == producto_base:
                tabla = sistema.get("autoportancia", {}).get("tabla", {})
                entry = tabla.get(str(espesor_mm), {})
                autoportancia_m = entry.get("autoportancia_m")
                break

    if autoportancia_m is None:
        return AutoportanciaResult(
            cumple=False,
            luz_m=luz_m,
            autoportancia_m=0,
            espesor_mm=espesor_mm,
            margen_seguridad_pct=0,
            recomendacion=f"No se encontró dato de autoportancia para {producto_base} {espesor_mm}mm. Consultar con ingeniería.",
        )

    cumple = luz_m <= autoportancia_m
    margen = ((autoportancia_m - luz_m) / autoportancia_m) * 100 if autoportancia_m > 0 else 0

    recomendacion = None
    if not cumple:
        # Find next espesor that works
        all_espesores = sorted(espesores.keys(), key=lambda x: int(x))
        for esp in all_espesores:
            esp_auto = espesores[esp].get("autoportancia")
            if esp_auto and luz_m <= esp_auto:
                recomendacion = (
                    f"El espesor {espesor_mm}mm (autoportancia {autoportancia_m}m) NO cubre la luz de {luz_m}m. "
                    f"Recomendación: usar {esp}mm (autoportancia {esp_auto}m) o agregar apoyo intermedio."
                )
                break
        if not recomendacion:
            recomendacion = (
                f"El espesor {espesor_mm}mm (autoportancia {autoportancia_m}m) NO cubre la luz de {luz_m}m. "
                f"Se requiere apoyo intermedio adicional."
            )
    elif margen < 15:
        recomendacion = (
            f"Cumple pero con margen ajustado ({margen:.0f}%). "
            f"Considerar espesor mayor para mayor seguridad."
        )

    return AutoportanciaResult(
        cumple=cumple,
        luz_m=luz_m,
        autoportancia_m=autoportancia_m,
        espesor_mm=espesor_mm,
        margen_seguridad_pct=round(margen, 1),
        recomendacion=recomendacion,
    )


def lookup_accessory_price(
    tipo: str,
    familia: str,
    espesor_mm: Optional[int] = None,
    sku: Optional[str] = None,
    accessories_path: Optional[Path] = None,
) -> Optional[Dict[str, Any]]:
    """
    Busca precio de un accesorio en el catálogo.

    Search priority:
    1. Exact SKU match
    2. Type + family + thickness match
    3. Type + family match (any thickness)

    Returns dict with sku, name, precio_unit_iva_inc, largo_std_m, unidad
    """
    acc_catalog = _load_json(accessories_path or ACCESSORIES_PATH)

    # Build a flat list of all accessories
    all_items = []
    for section_key in ['perfileria_goterones', 'babetas', 'canalones', 'cumbreras',
                        'perfiles_u', 'perfiles_especiales', 'fijaciones',
                        'selladores', 'accesorios_varios', 'montantes']:
        for item in acc_catalog.get(section_key, []):
            all_items.append(item)

    # Strategy 1: Exact SKU match
    if sku:
        for item in all_items:
            if item.get("sku") == sku:
                return item

    # Strategy 2: Type + family + thickness
    if espesor_mm:
        for item in all_items:
            item_tipo = item.get("tipo", "")
            item_compat = item.get("compatibilidad", [])
            item_espesor = item.get("espesor_panel_mm")

            if item_tipo == tipo and familia in item_compat and item_espesor == espesor_mm:
                return item

    # Strategy 3: Type + family (any thickness)
    for item in all_items:
        item_tipo = item.get("tipo", "")
        item_compat = item.get("compatibilidad", [])

        if item_tipo == tipo and familia in item_compat:
            # If espesor matters, prefer matching espesor
            if espesor_mm and item.get("espesor_panel_mm") == espesor_mm:
                return item

    # Strategy 4: Broader match
    for item in all_items:
        item_tipo = item.get("tipo", "")
        item_compat = item.get("compatibilidad", [])
        if item_tipo == tipo and familia in item_compat:
            return item

    return None


def _get_fijacion_price(nombre_key: str, accessories_path: Optional[Path] = None) -> Tuple[float, str]:
    """Get fixation price from BOM rules reference prices."""
    bom_rules = _load_json(BOM_RULES_PATH)
    ref_prices = bom_rules.get("precios_fijaciones_referencia", {})

    if nombre_key in ref_prices:
        entry = ref_prices[nombre_key]
        return entry["precio_iva_inc"], entry["nombre"]

    return 0, nombre_key


def calculate_full_quote(
    product_id: str,
    length_m: float,
    width_m: float,
    thickness_mm: int,
    bom_preset: str,
    tipo_fijacion: str = "metal",
    luz_m: Optional[float] = None,
    incluir_canalon: bool = False,
    incluir_cumbrera: bool = False,
    discount_percent: float = 0.0,
    kb_path: Optional[Path] = None,
    accessories_path: Optional[Path] = None,
    bom_rules_path: Optional[Path] = None,
) -> FullQuotationResult:
    """
    Calcula cotización COMPLETA con BOM valorizado.

    Una sola llamada devuelve paneles + accesorios + fijaciones + selladores,
    todos con precio, cantidad y total por línea.

    Args:
        product_id: ID del producto base (ej: "ISODEC_EPS")
        length_m: Largo total del techo/pared en metros
        width_m: Ancho total del techo/pared en metros
        thickness_mm: Espesor del panel en mm
        bom_preset: Sistema a usar (ej: "techo_isodec_eps")
        tipo_fijacion: "metal", "hormigon", o "madera"
        luz_m: Distancia entre apoyos (para autoportancia)
        incluir_canalon: Incluir canalón en la cotización
        incluir_cumbrera: Incluir cumbrera en la cotización
        discount_percent: Descuento global (0-30)
        kb_path: Path a KB principal
        accessories_path: Path a catálogo de accesorios
        bom_rules_path: Path a reglas BOM

    Returns:
        FullQuotationResult con BOM completo valorizado
    """
    kb = _load_json(kb_path or DEFAULT_KB_PATH)
    bom_rules = _load_json(bom_rules_path or BOM_RULES_PATH)

    # Validate inputs
    if discount_percent < 0 or discount_percent > 30:
        raise ValueError(f"Descuento {discount_percent}% fuera de rango (0-30%)")

    # Get system rules
    sistema = bom_rules.get("sistemas", {}).get(bom_preset)
    if not sistema:
        available = list(bom_rules.get("sistemas", {}).keys())
        raise ValueError(f"Sistema '{bom_preset}' no encontrado. Disponibles: {available}")

    # Get product from KB
    product = kb.get("products", {}).get(product_id)
    if not product:
        raise ValueError(f"Producto '{product_id}' no encontrado en KB")

    espesor_data = product.get("espesores", {}).get(str(thickness_mm))
    if not espesor_data:
        available_esp = list(product.get("espesores", {}).keys())
        raise ValueError(f"Espesor {thickness_mm}mm no disponible para {product_id}. Disponibles: {available_esp}")

    precio_panel_m2 = espesor_data.get("precio")
    if precio_panel_m2 is None or isinstance(precio_panel_m2, str):
        raise ValueError(f"Precio no disponible para {product_id} {thickness_mm}mm. Consultar con ventas.")

    # Calculate basic dimensions
    ancho_util = _to_decimal(str(sistema.get("ancho_util_m", product.get("ancho_util", 1.0))))
    largo = _to_decimal(str(length_m))
    ancho = _to_decimal(str(width_m))
    panels_needed = math.ceil(float(ancho / ancho_util))
    area_m2 = float(_round_currency(_to_decimal(str(panels_needed)) * largo * ancho_util))

    # Autoportancia validation
    effective_luz = luz_m if luz_m else length_m
    autoportancia = validate_autoportancia(
        espesor_mm=thickness_mm,
        luz_m=effective_luz,
        producto_base=product_id,
        kb_path=kb_path or DEFAULT_KB_PATH,
        bom_rules_path=bom_rules_path or BOM_RULES_PATH,
    )

    # Calculate supports (apoyos)
    autoportancia_m = autoportancia["autoportancia_m"]
    if autoportancia_m > 0:
        apoyos = math.ceil(effective_luz / autoportancia_m) + 1
    else:
        apoyos = 2  # minimum

    # Calculate fixation points
    puntos_fijacion = math.ceil(((panels_needed * apoyos) * 2) + (float(largo) * 2 / 2.5))

    # Build BOM line items
    line_items: List[BOMLineItem] = []
    items_sin_precio: List[str] = []
    notes: List[str] = []

    subtotal_paneles = Decimal('0')
    subtotal_perfileria = Decimal('0')
    subtotal_fijaciones = Decimal('0')
    subtotal_selladores = Decimal('0')

    # ─── 1. PANELES ───
    panel_price = _to_decimal(str(precio_panel_m2))
    panel_total = _round_currency(panel_price * _to_decimal(str(area_m2)))
    subtotal_paneles += panel_total

    line_items.append(BOMLineItem(
        sku=product_id,
        name=product.get("nombre_comercial", product_id),
        categoria="panel",
        unidad="m2",
        cantidad=area_m2,
        precio_unit_iva_inc=float(panel_price),
        total_iva_inc=float(panel_total),
        nota=f"{panels_needed} paneles de {float(largo)}m x {float(ancho_util)}m",
    ))

    # ─── 2. PERFILERÍA (goterones, babetas) ───
    bom_rules_items = sistema.get("bom", {})
    familia = product_id.split("_")[0] if "_" in product_id else product_id

    # Helper to add profile items
    def _add_profile_item(key: str, rule: Dict, categoria: str):
        nonlocal subtotal_perfileria
        largo_std = rule.get("largo_std_m", 3.0)

        # Calculate quantity based on formula type
        if "gotero_frontal" in key:
            qty = math.ceil((panels_needed * float(ancho_util)) / largo_std)
        elif "gotero_lateral" in key:
            qty = math.ceil((float(largo) * 2) / largo_std)
        elif "gotero_superior" in key:
            if not rule.get("condicion") or rule.get("condicion") != "si_hay_muro_superior":
                qty = math.ceil((panels_needed * float(ancho_util)) / largo_std)
            else:
                qty = math.ceil((panels_needed * float(ancho_util)) / largo_std)
        elif "babeta" in key and "lateral" in key:
            qty = math.ceil((float(largo) * 2) / largo_std)
        elif "babeta" in key:
            qty = math.ceil(float(ancho) / largo_std)
        elif "vaina" in key:
            qty = max(0, panels_needed - 1)
        elif "cumbrera" in key:
            if not incluir_cumbrera:
                return
            qty = math.ceil(float(ancho) / largo_std)
        elif "canalon" in key and "soporte" not in key:
            if not incluir_canalon:
                return
            qty = math.ceil(float(ancho) / largo_std)
        elif "soporte_canalon" in key:
            if not incluir_canalon:
                return
            qty = math.ceil(float(ancho) / 1.0)
        elif "perfil_u" in key:
            qty = math.ceil(float(ancho) / largo_std)
        elif "perfil_g2" in key or "perfil_k2" in key:
            # Esquinas - assume 4 esquinas for a rectangular area
            esquinas = 4
            qty = math.ceil(esquinas * float(largo) / largo_std)
        else:
            qty = math.ceil(float(ancho) / largo_std)

        if qty <= 0:
            return

        # Look up price
        tipo_accesorio = rule.get("tipo_accesorio", key)
        familia_accesorio = rule.get("familia_accesorio", familia)
        sku_default = rule.get("sku_default")

        acc = lookup_accessory_price(
            tipo=tipo_accesorio,
            familia=familia_accesorio,
            espesor_mm=thickness_mm,
            sku=sku_default,
            accessories_path=accessories_path or ACCESSORIES_PATH,
        )

        if acc and acc.get("precio_unit_iva_inc"):
            price = _to_decimal(str(acc["precio_unit_iva_inc"]))
            total = _round_currency(price * _to_decimal(str(qty)))
            subtotal_perfileria += total
            line_items.append(BOMLineItem(
                sku=acc.get("sku", sku_default or key),
                name=acc.get("name", rule.get("descripcion", key)),
                categoria=categoria,
                unidad="unit",
                cantidad=qty,
                precio_unit_iva_inc=float(price),
                total_iva_inc=float(total),
                nota=rule.get("descripcion"),
            ))
        else:
            items_sin_precio.append(f"{key} ({rule.get('descripcion', '')})")
            line_items.append(BOMLineItem(
                sku=sku_default or key,
                name=rule.get("descripcion", key),
                categoria=categoria,
                unidad="unit",
                cantidad=qty,
                precio_unit_iva_inc=0,
                total_iva_inc=0,
                nota="PRECIO PENDIENTE - consultar con ventas",
            ))

    for key, rule in bom_rules_items.items():
        if not isinstance(rule, dict):
            continue

        if "gotero" in key:
            _add_profile_item(key, rule, "gotero_frontal" if "frontal" in key
                              else "gotero_lateral" if "lateral" in key
                              else "gotero_superior")
        elif "babeta" in key:
            # Skip empotrar if adosar is already included (use one or the other)
            if "empotrar" in key:
                continue
            _add_profile_item(key, rule, "babeta")
        elif "vaina" in key:
            _add_profile_item(key, rule, "vaina")
        elif "canalon" in key:
            _add_profile_item(key, rule, "canalon" if "soporte" not in key else "soporte_canalon")
        elif "cumbrera" in key:
            _add_profile_item(key, rule, "cumbrera")
        elif "perfil_u" in key:
            _add_profile_item(key, rule, "perfil_u")
        elif "perfil_g2" in key:
            _add_profile_item(key, rule, "perfil_g2")
        elif "perfil_k2" in key:
            _add_profile_item(key, rule, "perfil_k2")
        elif key in ("varilla_roscada", "tuerca", "taco_expansivo",
                     "arandela_carrocero", "arandela_plana", "tortuga_pvc",
                     "caballete"):
            # Handle fixations below
            pass
        elif key in ("fijaciones_perfileria", "silicona"):
            # Handle below
            pass
        elif key in ("paneles", "apoyos"):
            # Already handled
            pass

    # ─── 3. FIJACIONES ───
    if sistema.get("sistema_fijacion") == "varilla_tuerca":
        # Varilla roscada
        varillas_qty = math.ceil(puntos_fijacion / 4)
        price, name = _get_fijacion_price("varilla_roscada_3_8_1m")
        price_dec = _to_decimal(str(price))
        total = _round_currency(price_dec * _to_decimal(str(varillas_qty)))
        subtotal_fijaciones += total
        line_items.append(BOMLineItem(
            sku="VAR-3/8-1M", name=name, categoria="varilla",
            unidad="unit", cantidad=varillas_qty,
            precio_unit_iva_inc=float(price_dec), total_iva_inc=float(total),
            nota=f"1 varilla cada 4 puntos de fijación ({puntos_fijacion} puntos)",
        ))

        # Tuercas
        if tipo_fijacion == "metal":
            tuercas_qty = puntos_fijacion * 2
        else:
            tuercas_qty = puntos_fijacion * 1
        price, name = _get_fijacion_price("tuerca_3_8")
        price_dec = _to_decimal(str(price))
        total = _round_currency(price_dec * _to_decimal(str(tuercas_qty)))
        subtotal_fijaciones += total
        line_items.append(BOMLineItem(
            sku="TUE-3/8", name=name, categoria="tuerca",
            unidad="unit", cantidad=tuercas_qty,
            precio_unit_iva_inc=float(price_dec), total_iva_inc=float(total),
            nota=f"{'2 por punto (metal)' if tipo_fijacion == 'metal' else '1 por punto (hormigón)'}",
        ))

        # Taco expansivo (solo hormigón)
        if tipo_fijacion == "hormigon":
            taco_qty = puntos_fijacion
            price, name = _get_fijacion_price("taco_expansivo_3_8")
            price_dec = _to_decimal(str(price))
            total = _round_currency(price_dec * _to_decimal(str(taco_qty)))
            subtotal_fijaciones += total
            line_items.append(BOMLineItem(
                sku="TACO-3/8", name=name, categoria="taco",
                unidad="unit", cantidad=taco_qty,
                precio_unit_iva_inc=float(price_dec), total_iva_inc=float(total),
                nota="1 por punto de fijación (solo hormigón)",
            ))

        # Arandela carrocero
        arandela_qty = puntos_fijacion
        price, name = _get_fijacion_price("arandela_carrocero_3_8")
        price_dec = _to_decimal(str(price))
        total = _round_currency(price_dec * _to_decimal(str(arandela_qty)))
        subtotal_fijaciones += total
        line_items.append(BOMLineItem(
            sku="ARAN-CARR-3/8", name=name, categoria="arandela",
            unidad="unit", cantidad=arandela_qty,
            precio_unit_iva_inc=float(price_dec), total_iva_inc=float(total),
            nota="1 por punto de fijación",
        ))

        # Arandela plana
        price, name = _get_fijacion_price("arandela_plana_3_8")
        price_dec = _to_decimal(str(price))
        total = _round_currency(price_dec * _to_decimal(str(arandela_qty)))
        subtotal_fijaciones += total
        line_items.append(BOMLineItem(
            sku="ARAN-PLANA-3/8", name=name, categoria="arandela",
            unidad="unit", cantidad=arandela_qty,
            precio_unit_iva_inc=float(price_dec), total_iva_inc=float(total),
            nota="1 por punto de fijación",
        ))

        # Tortuga PVC
        price, name = _get_fijacion_price("tortuga_pvc_blanca")
        price_dec = _to_decimal(str(price))
        total = _round_currency(price_dec * _to_decimal(str(arandela_qty)))
        subtotal_fijaciones += total
        line_items.append(BOMLineItem(
            sku="TORT-PVC-BL", name=name, categoria="tortuga",
            unidad="unit", cantidad=arandela_qty,
            precio_unit_iva_inc=float(price_dec), total_iva_inc=float(total),
            nota="1 por punto de fijación (sella e impermeabiliza)",
        ))

    elif sistema.get("sistema_fijacion") == "caballete_tornillo":
        # Caballete (ISOROOF)
        caballete_qty = panels_needed * apoyos
        price, name = _get_fijacion_price("caballete_isoroof")
        price_dec = _to_decimal(str(price))
        total = _round_currency(price_dec * _to_decimal(str(caballete_qty)))
        subtotal_fijaciones += total
        line_items.append(BOMLineItem(
            sku="CAB-ISOROOF", name=name, categoria="caballete",
            unidad="unit", cantidad=caballete_qty,
            precio_unit_iva_inc=float(price_dec), total_iva_inc=float(total),
            nota=f"{panels_needed} paneles x {apoyos} apoyos",
        ))

    # ─── 4. FIJACIONES PERFILERÍA (remaches/T1) ───
    # Calculate total perimeter of profiles installed
    perimetro_perfileria_ml = 0.0
    for item in line_items:
        if item["categoria"] in ("gotero_frontal", "gotero_lateral", "gotero_superior",
                                  "babeta", "perfil_u", "perfil_g2", "perfil_k2"):
            # Each piece has a standard length
            largo_pieza = 3.0  # default
            perimetro_perfileria_ml += item["cantidad"] * largo_pieza

    if perimetro_perfileria_ml > 0:
        fij_perf_qty = math.ceil(perimetro_perfileria_ml / 0.30)
        # Remaches are low cost, ~$0.02 each average
        price_dec = _to_decimal("0.05")  # estimated remache/T1
        total = _round_currency(price_dec * _to_decimal(str(fij_perf_qty)))
        subtotal_fijaciones += total
        line_items.append(BOMLineItem(
            sku="FIX-REMACHE", name="Remaches/T1 para perfilería",
            categoria="fijacion_perfileria",
            unidad="unit", cantidad=fij_perf_qty,
            precio_unit_iva_inc=float(price_dec), total_iva_inc=float(total),
            nota=f"1 cada 30cm - {perimetro_perfileria_ml:.1f}ml total perfilería",
        ))

    # ─── 5. SELLADORES ───
    if perimetro_perfileria_ml > 0:
        silicona_qty = math.ceil(perimetro_perfileria_ml / 8)
        price, name = _get_fijacion_price("silicona_neutra_600")
        price_dec = _to_decimal(str(price))
        total = _round_currency(price_dec * _to_decimal(str(silicona_qty)))
        subtotal_selladores += total
        line_items.append(BOMLineItem(
            sku="SELL-SILIC", name=name, categoria="silicona",
            unidad="unit", cantidad=silicona_qty,
            precio_unit_iva_inc=float(price_dec), total_iva_inc=float(total),
            nota=f"Rendimiento ~8ml por tubo ({perimetro_perfileria_ml:.1f}ml perfilería)",
        ))

    # ─── TOTALS ───
    subtotal = subtotal_paneles + subtotal_perfileria + subtotal_fijaciones + subtotal_selladores

    # Apply discount
    discount_dec = _to_decimal(str(discount_percent))
    discount_amount = _round_currency(subtotal * discount_dec / _to_decimal("100"))
    total_final = _round_currency(subtotal - discount_amount)

    # Notes
    if not autoportancia["cumple"]:
        notes.append(f"⚠️ AUTOPORTANCIA: {autoportancia['recomendacion']}")
    elif autoportancia.get("recomendacion"):
        notes.append(f"ℹ️ AUTOPORTANCIA: {autoportancia['recomendacion']}")

    if items_sin_precio:
        notes.append(f"⚠️ Items sin precio disponible: {', '.join(items_sin_precio)}")

    if discount_percent > 0:
        notes.append(f"Descuento aplicado: {discount_percent}%")

    notes.append("Precios con IVA 22% incluido. NO sumar IVA adicional.")

    # Build result
    quotation_id = f"BMC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    result = FullQuotationResult(
        quotation_id=quotation_id,
        timestamp=datetime.utcnow().isoformat() + "Z",
        calculation_verified=True,
        verification_checksum="",
        largo_m=float(largo),
        ancho_m=float(ancho),
        area_m2=area_m2,
        panels_needed=panels_needed,
        autoportancia=autoportancia,
        line_items=line_items,
        subtotal_paneles=float(_round_currency(subtotal_paneles)),
        subtotal_perfileria=float(_round_currency(subtotal_perfileria)),
        subtotal_fijaciones=float(_round_currency(subtotal_fijaciones)),
        subtotal_selladores=float(_round_currency(subtotal_selladores)),
        subtotal_usd=float(_round_currency(subtotal)),
        discount_percent=float(discount_dec),
        discount_amount_usd=float(discount_amount),
        total_iva_inc=float(total_final),
        sistema=bom_preset,
        espesor_mm=thickness_mm,
        tipo_fijacion=tipo_fijacion,
        notes=notes,
        items_sin_precio=items_sin_precio,
    )

    result["verification_checksum"] = _generate_checksum(result)
    return result
