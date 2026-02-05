from fastapi import FastAPI, HTTPException, Security, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Any
import sys
import os
from pathlib import Path

# Add project root to sys.path to allow importing from config
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from config.settings import settings
from panelin_agent_v2.tools.quotation_calculator import (
    calculate_panel_quote,
    QuotationResult,
    AccessoriesResult
)
from panelin_agent_v2.tools.product_lookup import (
    find_product_by_query,
    get_product_price,
    check_product_availability
)

app = FastAPI(
    title="Panelin Wolf API",
    description="Secure Deterministic API for BMC Uruguay Quotations",
    version="2.0.0"
)

# --- Security Configuration ---
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """
    Validate API Key against secure storage.
    CRITICAL: This ensures only authorized users (The Wolf GPT) can access.
    """
    if not settings.WOLF_API_KEY:
        # If key is not configured in backend, strictly deny all access
        # This prevents "fail open" if configuration is missing
        print("CRITICAL SECURITY ERROR: WOLF_API_KEY is not set in backend.")
        raise HTTPException(
            status_code=500,
            detail="Server security configuration incomplete. WOLF_API_KEY missing."
        )

    if api_key_header == settings.WOLF_API_KEY:
        return api_key_header

    raise HTTPException(
        status_code=403,
        detail="Could not validate credentials"
    )

# --- Request Models ---

class QuoteRequest(BaseModel):
    product_id: str = Field(..., description="ID del producto (ej: ISOPANEL_EPS_50mm)")
    length_m: float = Field(..., ge=0.5, le=14.0, description="Largo del panel en metros")
    width_m: float = Field(..., ge=0.5, le=50.0, description="Ancho total en metros")
    quantity: int = Field(1, ge=1, description="Cantidad")
    discount_percent: float = Field(0.0, ge=0.0, le=30.0, description="Descuento (0-30)")
    include_accessories: bool = Field(False, description="Incluir accesorios")
    include_tax: bool = Field(True, description="Incluir IVA")
    installation_type: Literal["techo", "pared"] = Field("techo", description="Tipo de instalación")

class ProductSearchRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Búsqueda en lenguaje natural")
    max_results: int = Field(5, ge=1, le=20)

class ProductPriceRequest(BaseModel):
    product_id: str

# --- Endpoints ---

@app.get("/", dependencies=[Security(get_api_key)])
async def root():
    return {
        "status": "active",
        "system": "Panelin Wolf API",
        "security": "Enforced",
        "version": "2.0.0"
    }

@app.get("/health")
async def health_check():
    """Liveness: public health check - only reveals if server is running."""
    return {"status": "ok"}


@app.get("/ready")
async def ready_check():
    """Readiness: service is ready to accept traffic (config present)."""
    if not settings.WOLF_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Service not ready: WOLF_API_KEY not configured",
        )
    return {"status": "ready"}

@app.post("/calculate_quote", response_model=QuotationResult, dependencies=[Security(get_api_key)])
async def api_calculate_quote(request: QuoteRequest):
    try:
        result = calculate_panel_quote(
            product_id=request.product_id,
            length_m=request.length_m,
            width_m=request.width_m,
            quantity=request.quantity,
            discount_percent=request.discount_percent,
            include_accessories=request.include_accessories,
            include_tax=request.include_tax,
            installation_type=request.installation_type
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error calculating quote: {e}")
        raise HTTPException(status_code=500, detail="Internal calculation error")

@app.post("/find_products", dependencies=[Security(get_api_key)])
async def api_find_products(request: ProductSearchRequest):
    results = find_product_by_query(request.query, request.max_results)
    return {"results": results}

@app.post("/product_price", dependencies=[Security(get_api_key)])
async def api_product_price(request: ProductPriceRequest):
    result = get_product_price(request.product_id)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return result

@app.post("/check_availability", dependencies=[Security(get_api_key)])
async def api_check_availability(request: ProductPriceRequest):
    result = check_product_availability(request.product_id)
    if not result.get("found"):
        raise HTTPException(status_code=404, detail="Product not found")
    return result
