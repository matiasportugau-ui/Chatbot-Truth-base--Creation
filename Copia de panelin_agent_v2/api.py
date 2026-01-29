from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from tools.quotation_calculator import calculate_panel_quote, QuotationResult, AccessoriesResult
from tools.product_lookup import (
    find_product_by_query, 
    get_product_price, 
    check_product_availability, 
    list_all_products,
    get_pricing_rules
)

app = FastAPI(
    title="Panelin Agent V2 API",
    description="Deterministic API for BMC Uruguay panel quotations. LLM extracts parameters, Python calculates.",
    version="2.0.0"
)

# --- Models ---

class QuoteRequest(BaseModel):
    product_id: str = Field(..., description="ID del producto (ej: ISOPANEL_EPS_50mm)")
    length_m: float = Field(..., description="Largo del panel en metros", gt=0)
    width_m: float = Field(..., description="Ancho total a cubrir en metros", gt=0)
    quantity: int = Field(1, description="Cantidad de instalaciones/paneles", ge=1)
    discount_percent: float = Field(0.0, description="Porcentaje de descuento aplicable", ge=0, le=30)
    include_accessories: bool = Field(False, description="Incluir cálculo de accesorios")
    include_tax: bool = Field(True, description="Incluir IVA (22%)")
    installation_type: Literal["techo", "pared"] = Field("techo", description="Tipo de instalación")

# --- Endpoints ---

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "Panelin Agent V2 API"}

@app.get("/products/search", tags=["Products"])
def search_products(q: str = Query(..., description="Query de búsqueda"), max_results: int = 5):
    """Busca productos basándose en descripción en lenguaje natural."""
    return find_product_by_query(q, max_results=max_results)

@app.get("/products/{product_id}/price", tags=["Products"])
def get_price(product_id: str):
    """Obtiene el precio exacto de un producto por su ID."""
    price = get_product_price(product_id)
    if not price:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return price

@app.get("/products/{product_id}/availability", tags=["Products"])
def get_availability(product_id: str):
    """Verifica disponibilidad y stock de un producto."""
    return check_product_availability(product_id)

@app.get("/products", tags=["Products"])
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
            installation_type=request.installation_type
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/pricing/rules", tags=["Pricing"])
def get_rules():
    """Obtiene las reglas de precios vigentes (IVA, envíos, etc.)."""
    return get_pricing_rules()
