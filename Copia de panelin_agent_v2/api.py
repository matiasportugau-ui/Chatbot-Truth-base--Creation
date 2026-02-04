import os

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from tools.quotation_calculator import (
    calculate_panel_quote,
    QuotationResult,
    AccessoriesResult,
)
from tools.product_lookup import (
    find_product_by_query,
    get_product_price,
    check_product_availability,
    list_all_products,
    get_pricing_rules,
)

OPENAPI_SERVER_URL = os.getenv(
    "OPENAPI_SERVER_URL", "https://panelin-api-xxxxx-uc.a.run.app"
)
OPENAPI_SERVER_DESCRIPTION = os.getenv(
    "OPENAPI_SERVER_DESCRIPTION", "Cloud Run Production"
)

app = FastAPI(
    title="Panelin Agent V2 API",
    description="Deterministic API for BMC Uruguay panel quotations. LLM extracts parameters, Python calculates.",
    version="2.0.0",
    servers=[
        {
            "url": OPENAPI_SERVER_URL,
            "description": OPENAPI_SERVER_DESCRIPTION,
        }
    ],
)

# --- Response Models ---


class ProductInfo(BaseModel):
    product_id: str
    name: str
    family: str
    thickness_mm: Optional[int] = None
    price_per_m2: float
    currency: str
    stock_status: str
    ancho_util_m: Optional[float] = None
    largo_min_m: Optional[float] = None
    largo_max_m: Optional[float] = None
    match_score: Optional[int] = None


class PriceInfo(BaseModel):
    product_id: str
    name: str
    price_per_m2: float
    currency: str
    last_updated: Optional[str] = None
    _source: str


class AvailabilityInfo(BaseModel):
    product_id: str
    found: bool
    name: Optional[str] = None
    available: bool
    stock_status: str
    inventory_quantity: Optional[int] = None
    last_updated: Optional[str] = None
    _source: str


class PricingRules(BaseModel):
    tax_rate_uy_iva: float
    currency: str
    delivery_cost_per_m2: float
    minimum_delivery_charge_usd: float
    payment_terms: Dict[str, Any]


# --- Request Models ---


class QuoteRequest(BaseModel):
    product_id: str = Field(..., description="ID del producto (ej: ISOPANEL_EPS_50mm)")
    length_m: float = Field(..., description="Largo del panel en metros", gt=0)
    width_m: float = Field(..., description="Ancho total a cubrir en metros", gt=0)
    quantity: int = Field(1, description="Cantidad de instalaciones/paneles", ge=1)
    discount_percent: float = Field(
        0.0, description="Porcentaje de descuento aplicable", ge=0, le=30
    )
    include_accessories: bool = Field(
        False, description="Incluir cálculo de accesorios"
    )
    include_tax: bool = Field(True, description="Incluir IVA (22%)")
    installation_type: Literal["techo", "pared"] = Field(
        "techo", description="Tipo de instalación"
    )


# --- Endpoints ---


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "Panelin Agent V2 API"}


@app.get("/health", tags=["Health"])
def liveness_check():
    return {"status": "ok"}


@app.get("/ready", tags=["Health"])
def readiness_check():
    try:
        pricing_rules = get_pricing_rules()
        products = list_all_products()
    except Exception as exc:
        raise HTTPException(
            status_code=503, detail=f"Readiness check failed: {exc}"
        )

    return {
        "status": "ready",
        "products_loaded": len(products),
        "pricing_rules_loaded": bool(pricing_rules),
    }


@app.get("/products/search", response_model=List[ProductInfo], tags=["Products"])
def search_products(
    q: str = Query(..., description="Query de búsqueda"), max_results: int = 5
):
    """Busca productos basándose en descripción en lenguaje natural."""
    return find_product_by_query(q, max_results=max_results)


@app.get("/products/{product_id}/price", response_model=PriceInfo, tags=["Products"])
def get_price(product_id: str):
    """Obtiene el precio exacto de un producto por su ID."""
    price = get_product_price(product_id)
    if not price:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return price


@app.get(
    "/products/{product_id}/availability",
    response_model=AvailabilityInfo,
    tags=["Products"],
)
def get_availability(product_id: str):
    """Verifica disponibilidad y stock de un producto."""
    return check_product_availability(product_id)


@app.get("/products", response_model=List[ProductInfo], tags=["Products"])
def list_products(family: Optional[str] = None):
    """Lista todos los productos disponibles, opcionalmente filtrados por familia."""
    return list_all_products(family=family)


@app.post("/quotes", response_model=QuotationResult, tags=["Quotations"])
def create_quote(request: QuoteRequest):
    """Calcula una cotización determinista para paneles."""
    try:
        return calculate_panel_quote(
            product_id=request.product_id,
            length_m=request.length_m,
            width_m=request.width_m,
            quantity=request.quantity,
            discount_percent=request.discount_percent,
            include_accessories=request.include_accessories,
            include_tax=request.include_tax,
            installation_type=request.installation_type,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/pricing/rules", response_model=PricingRules, tags=["Pricing"])
def get_rules():
    """Obtiene las reglas de precios vigentes (IVA, envíos, etc.)."""
    return get_pricing_rules()
