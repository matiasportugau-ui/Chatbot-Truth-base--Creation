"""
============================================================================
Panelin Agent V2 API - Production Server
============================================================================
FastAPI application with production-grade health checks, observability,
and Cloud Run optimizations.
============================================================================
"""

import os
import sys
import time
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Literal
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "logger": "%(name)s"}',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("panelin-api")

# -----------------------------------------------------------------------------
# Application State for Health Checks
# -----------------------------------------------------------------------------
class AppState:
    """Tracks application health state."""
    def __init__(self):
        self.startup_time: datetime = datetime.now(timezone.utc)
        self.is_ready: bool = False
        self.last_successful_request: Optional[datetime] = None
        self.total_requests: int = 0
        self.error_count: int = 0
        self.dependencies_healthy: Dict[str, bool] = {}

    def mark_ready(self):
        self.is_ready = True
        logger.info("Application marked as ready")

    def record_request(self, success: bool = True):
        self.total_requests += 1
        if success:
            self.last_successful_request = datetime.now(timezone.utc)
        else:
            self.error_count += 1

    def check_dependency(self, name: str, healthy: bool):
        self.dependencies_healthy[name] = healthy

app_state = AppState()

# -----------------------------------------------------------------------------
# Startup/Shutdown Lifecycle
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("Starting Panelin API...")
    
    # Validate critical dependencies
    try:
        # Check if knowledge base file exists
        kb_path = os.path.join(
            os.path.dirname(__file__),
            "panelin_agent_v2", "config", "panelin_truth_bmcuruguay.json"
        )
        if os.path.exists(kb_path):
            app_state.check_dependency("knowledge_base", True)
            logger.info(f"Knowledge base loaded from {kb_path}")
        else:
            app_state.check_dependency("knowledge_base", False)
            logger.warning(f"Knowledge base not found at {kb_path}")
        
        # Import tools to validate they load correctly
        from panelin_agent_v2.tools.quotation_calculator import calculate_panel_quote
        from panelin_agent_v2.tools.product_lookup import find_product_by_query
        app_state.check_dependency("quotation_tools", True)
        logger.info("Quotation tools loaded successfully")
        
    except Exception as e:
        logger.error(f"Startup validation failed: {e}")
        app_state.check_dependency("quotation_tools", False)
    
    # Mark as ready
    app_state.mark_ready()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Panelin API...")

# -----------------------------------------------------------------------------
# FastAPI Application
# -----------------------------------------------------------------------------
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
VERSION = os.getenv("VERSION", "2.0.0")

app = FastAPI(
    title="Panelin Agent V2 API",
    description="Production-grade API for BMC Uruguay panel quotations. Deterministic calculations with LLM parameter extraction.",
    version=VERSION,
    lifespan=lifespan,
    docs_url="/docs" if ENVIRONMENT != "production" else None,  # Disable Swagger in production
    redoc_url="/redoc" if ENVIRONMENT != "production" else None,
    servers=[
        {
            "url": os.getenv("API_BASE_URL", "https://panelin-api.run.app"),
            "description": f"{ENVIRONMENT.title()} Server",
        }
    ],
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Request Middleware for Observability
# -----------------------------------------------------------------------------
@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    """Log requests and track metrics."""
    start_time = time.perf_counter()
    
    # Get Cloud Run headers for tracing
    trace_header = request.headers.get("X-Cloud-Trace-Context", "")
    
    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        # Log request (structured for Cloud Logging)
        logger.info(
            f"Request completed",
            extra={
                "httpRequest": {
                    "requestMethod": request.method,
                    "requestUrl": str(request.url),
                    "status": response.status_code,
                    "latency": f"{duration_ms:.2f}ms",
                },
                "trace": trace_header,
            }
        )
        
        app_state.record_request(success=response.status_code < 400)
        
        # Add timing header
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
        
        return response
        
    except Exception as e:
        app_state.record_request(success=False)
        logger.error(f"Request failed: {e}")
        raise

# -----------------------------------------------------------------------------
# Health Check Endpoints
# -----------------------------------------------------------------------------

class HealthResponse(BaseModel):
    """Health check response model."""
    status: Literal["healthy", "unhealthy", "degraded"]
    service: str = "panelin-api"
    version: str
    environment: str
    uptime_seconds: float
    timestamp: str

class ReadinessResponse(BaseModel):
    """Readiness check response model."""
    ready: bool
    checks: Dict[str, bool]
    message: str

class LivenessResponse(BaseModel):
    """Liveness check response model."""
    alive: bool
    timestamp: str

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check endpoint",
    description="Returns overall health status. Used by Cloud Run for startup probes."
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint for Cloud Run startup/liveness probes.
    
    Returns:
    - **healthy**: All systems operational
    - **degraded**: Some non-critical systems impaired
    - **unhealthy**: Critical systems down
    """
    uptime = (datetime.now(timezone.utc) - app_state.startup_time).total_seconds()
    
    # Determine health status
    all_healthy = all(app_state.dependencies_healthy.values())
    any_healthy = any(app_state.dependencies_healthy.values())
    
    if all_healthy:
        status = "healthy"
    elif any_healthy:
        status = "degraded"
    else:
        status = "unhealthy"
    
    return HealthResponse(
        status=status,
        version=VERSION,
        environment=ENVIRONMENT,
        uptime_seconds=uptime,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@app.get(
    "/ready",
    response_model=ReadinessResponse,
    tags=["Health"],
    summary="Readiness check endpoint",
    description="Indicates if the service is ready to accept traffic. Used for Cloud Run readiness probes."
)
async def readiness_check() -> ReadinessResponse:
    """
    Readiness check endpoint for Cloud Run readiness probes.
    
    Returns ready=true only when:
    - Application has completed startup
    - All critical dependencies are available
    """
    checks = {
        "startup_complete": app_state.is_ready,
        **app_state.dependencies_healthy
    }
    
    all_ready = all(checks.values())
    
    if not all_ready:
        raise HTTPException(
            status_code=503,
            detail=ReadinessResponse(
                ready=False,
                checks=checks,
                message="Service not ready - dependencies unhealthy"
            ).model_dump()
        )
    
    return ReadinessResponse(
        ready=True,
        checks=checks,
        message="Service ready to accept traffic"
    )

@app.get(
    "/live",
    response_model=LivenessResponse,
    tags=["Health"],
    summary="Liveness check endpoint",
    description="Simple ping to verify the process is alive."
)
async def liveness_check() -> LivenessResponse:
    """
    Liveness probe - returns immediately if process is responsive.
    """
    return LivenessResponse(
        alive=True,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

# -----------------------------------------------------------------------------
# Metrics Endpoint (for Cloud Monitoring custom metrics)
# -----------------------------------------------------------------------------

class MetricsResponse(BaseModel):
    """Application metrics."""
    total_requests: int
    error_count: int
    error_rate: float
    uptime_seconds: float
    last_successful_request: Optional[str]

@app.get(
    "/metrics",
    response_model=MetricsResponse,
    tags=["Observability"],
    summary="Application metrics",
    description="Returns application metrics for monitoring."
)
async def get_metrics() -> MetricsResponse:
    """Returns application metrics."""
    uptime = (datetime.now(timezone.utc) - app_state.startup_time).total_seconds()
    error_rate = (
        app_state.error_count / app_state.total_requests
        if app_state.total_requests > 0 else 0.0
    )
    
    return MetricsResponse(
        total_requests=app_state.total_requests,
        error_count=app_state.error_count,
        error_rate=round(error_rate, 4),
        uptime_seconds=uptime,
        last_successful_request=(
            app_state.last_successful_request.isoformat()
            if app_state.last_successful_request else None
        )
    )

# -----------------------------------------------------------------------------
# API Response Models
# -----------------------------------------------------------------------------

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
    source: str = Field(alias="_source")

class AvailabilityInfo(BaseModel):
    product_id: str
    found: bool
    name: Optional[str] = None
    available: bool
    stock_status: str
    inventory_quantity: Optional[int] = None
    last_updated: Optional[str] = None
    source: str = Field(alias="_source")

class PricingRules(BaseModel):
    tax_rate_uy_iva: float
    currency: str
    delivery_cost_per_m2: float
    minimum_delivery_charge_usd: float
    payment_terms: Dict[str, Any]

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

# -----------------------------------------------------------------------------
# Business API Endpoints
# -----------------------------------------------------------------------------

@app.get("/", tags=["Health"])
def root():
    """Root endpoint - redirects to health."""
    return {"status": "healthy", "service": "Panelin Agent V2 API", "version": VERSION}

@app.get("/products/search", response_model=List[ProductInfo], tags=["Products"])
def search_products(
    q: str = Query(..., description="Query de búsqueda"), 
    max_results: int = 5
):
    """Busca productos basándose en descripción en lenguaje natural."""
    from panelin_agent_v2.tools.product_lookup import find_product_by_query
    return find_product_by_query(q, max_results=max_results)

@app.get("/products/{product_id}/price", response_model=PriceInfo, tags=["Products"])
def get_price(product_id: str):
    """Obtiene el precio exacto de un producto por su ID."""
    from panelin_agent_v2.tools.product_lookup import get_product_price
    price = get_product_price(product_id)
    if not price:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return price

@app.get("/products/{product_id}/availability", response_model=AvailabilityInfo, tags=["Products"])
def get_availability(product_id: str):
    """Verifica disponibilidad y stock de un producto."""
    from panelin_agent_v2.tools.product_lookup import check_product_availability
    return check_product_availability(product_id)

@app.get("/products", response_model=List[ProductInfo], tags=["Products"])
def list_products(family: Optional[str] = None):
    """Lista todos los productos disponibles, opcionalmente filtrados por familia."""
    from panelin_agent_v2.tools.product_lookup import list_all_products
    return list_all_products(family=family)

@app.post("/quotes", tags=["Quotations"])
def create_quote(request: QuoteRequest):
    """Calcula una cotización determinista para paneles."""
    from panelin_agent_v2.tools.quotation_calculator import calculate_panel_quote
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
    from panelin_agent_v2.tools.product_lookup import get_pricing_rules
    return get_pricing_rules()

# -----------------------------------------------------------------------------
# Error Handlers
# -----------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with structured logging."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    app_state.record_request(success=False)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if ENVIRONMENT != "production" else "An unexpected error occurred",
            "request_id": request.headers.get("X-Cloud-Trace-Context", "unknown")
        }
    )

# -----------------------------------------------------------------------------
# Main Entry Point (for local development)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=ENVIRONMENT == "development",
        log_level=LOG_LEVEL.lower()
    )
