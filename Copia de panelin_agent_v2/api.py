import os
import time
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import JSONResponse
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

# =============================================================================
# Application Configuration
# =============================================================================
SERVICE_VERSION = "2.1.0"
SERVICE_NAME = "panelin-api"
STARTUP_TIME = time.time()

# Cloud Run URL (set via environment variable)
CLOUD_RUN_URL = os.getenv("CLOUD_RUN_URL", "https://YOUR-CLOUD-RUN-URL.run.app")

app = FastAPI(
    title="Panelin Agent V2 API",
    description="Deterministic API for BMC Uruguay panel quotations. LLM extracts parameters, Python calculates.",
    version=SERVICE_VERSION,
    servers=[
        {
            "url": CLOUD_RUN_URL,
            "description": "Production Server (Cloud Run)",
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


# =============================================================================
# Health & Readiness Endpoints
# =============================================================================
# These endpoints are critical for Cloud Run and container orchestration:
# - /health (liveness): Is the container alive? Basic process check.
# - /ready (readiness): Is the service ready to accept traffic?
# =============================================================================


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    service: str
    version: str
    timestamp: str
    uptime_seconds: float


class ReadinessResponse(BaseModel):
    """Readiness check response model."""
    ready: bool
    service: str
    version: str
    timestamp: str
    checks: Dict[str, Any]


def _check_knowledge_base() -> Dict[str, Any]:
    """Verify knowledge base is accessible."""
    try:
        # Try to list products - this validates the knowledge base is loaded
        products = list_all_products()
        return {
            "status": "ok",
            "product_count": len(products) if products else 0
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def _check_pricing_rules() -> Dict[str, Any]:
    """Verify pricing rules are accessible."""
    try:
        rules = get_pricing_rules()
        return {
            "status": "ok" if rules else "warning",
            "has_rules": rules is not None
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/", tags=["Health"], response_model=HealthResponse)
def root():
    """Root endpoint - returns basic service info."""
    return HealthResponse(
        status="healthy",
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        uptime_seconds=round(time.time() - STARTUP_TIME, 2)
    )


@app.get("/health", tags=["Health"], response_model=HealthResponse)
def health_check():
    """
    Liveness probe endpoint.
    
    Returns 200 if the service is alive and responding.
    This should be a fast, lightweight check that doesn't validate dependencies.
    Used by Cloud Run to determine if the container should be restarted.
    """
    return HealthResponse(
        status="healthy",
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        uptime_seconds=round(time.time() - STARTUP_TIME, 2)
    )


@app.get("/ready", tags=["Health"], response_model=ReadinessResponse)
def readiness_check(response: Response):
    """
    Readiness probe endpoint.
    
    Returns 200 if the service is ready to accept traffic.
    Validates that all dependencies (knowledge base, pricing rules) are accessible.
    Used by Cloud Run to determine if traffic should be routed to this instance.
    """
    kb_check = _check_knowledge_base()
    pricing_check = _check_pricing_rules()
    
    checks = {
        "knowledge_base": kb_check,
        "pricing_rules": pricing_check
    }
    
    # Determine overall readiness
    all_ok = all(
        check.get("status") in ("ok", "warning") 
        for check in checks.values()
    )
    
    if not all_ok:
        response.status_code = 503  # Service Unavailable
    
    return ReadinessResponse(
        ready=all_ok,
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        checks=checks
    )


# =============================================================================
# Business Endpoints
# =============================================================================


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
