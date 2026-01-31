"""
Panelin Agent V2 - Production API
==================================
FastAPI application with proper health checks, observability, and security.

Endpoints:
    - /health   : Liveness probe (is the process running?)
    - /ready    : Readiness probe (is the service ready to accept traffic?)
    - /metrics  : Basic metrics endpoint (optional Prometheus-compatible)
    - /         : Root/status endpoint
"""

import os
import time
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Literal
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Configure logging for Cloud Run (structured JSON)
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s","logger":"%(name)s"}',
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Startup/Shutdown Lifecycle
# -----------------------------------------------------------------------------

startup_time: Optional[float] = None
is_ready: bool = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    global startup_time, is_ready
    
    # Startup
    startup_time = time.time()
    logger.info("Starting Panelin API service...")
    
    # Perform startup checks
    try:
        # Validate critical configuration
        _validate_config()
        
        # Load any required resources (e.g., knowledge base)
        await _initialize_resources()
        
        is_ready = True
        logger.info(f"Service ready in {time.time() - startup_time:.2f}s")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        is_ready = False
    
    yield
    
    # Shutdown
    logger.info("Shutting down Panelin API service...")
    is_ready = False


def _validate_config():
    """Validate required configuration."""
    required_vars = []  # Add required env vars here if needed
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {missing}")


async def _initialize_resources():
    """Initialize resources like database connections, caches, etc."""
    # Placeholder for resource initialization
    # Example: await database.connect()
    pass


# -----------------------------------------------------------------------------
# Application Configuration
# -----------------------------------------------------------------------------

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
VERSION = os.getenv("VERSION", "2.0.0")
SERVICE_NAME = "panelin-api"

app = FastAPI(
    title="Panelin Agent V2 API",
    description="Deterministic API for BMC Uruguay panel quotations. Production-ready with health checks and observability.",
    version=VERSION,
    docs_url="/docs" if ENVIRONMENT != "production" else None,  # Disable Swagger in prod
    redoc_url="/redoc" if ENVIRONMENT != "production" else None,
    lifespan=lifespan,
    servers=[
        {
            "url": os.getenv("SERVICE_URL", "https://panelin-api.run.app"),
            "description": f"{ENVIRONMENT.title()} Server",
        }
    ],
)

# -----------------------------------------------------------------------------
# Middleware
# -----------------------------------------------------------------------------

# CORS (configure appropriately for your use case)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_tracking(request: Request, call_next):
    """Add request tracking headers and logging."""
    request_id = request.headers.get("X-Request-ID", f"req-{int(time.time() * 1000)}")
    start_time = time.time()
    
    response = await call_next(request)
    
    # Add tracking headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{(time.time() - start_time) * 1000:.2f}ms"
    
    # Log request (structured for Cloud Logging)
    logger.info(
        f'{request.method} {request.url.path} - {response.status_code} - {(time.time() - start_time) * 1000:.2f}ms'
    )
    
    return response


# -----------------------------------------------------------------------------
# Health Check Models
# -----------------------------------------------------------------------------

class HealthResponse(BaseModel):
    """Health check response."""
    status: Literal["healthy", "unhealthy", "degraded"]
    timestamp: str
    service: str
    version: str
    uptime_seconds: Optional[float] = None
    environment: str


class ReadinessResponse(BaseModel):
    """Readiness check response."""
    ready: bool
    timestamp: str
    checks: Dict[str, bool]
    message: Optional[str] = None


class MetricsResponse(BaseModel):
    """Basic metrics response."""
    uptime_seconds: float
    requests_total: int = 0  # Placeholder for actual metrics
    errors_total: int = 0
    avg_response_time_ms: float = 0.0


# -----------------------------------------------------------------------------
# Health Endpoints
# -----------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Liveness probe - indicates if the service process is running.
    
    Cloud Run uses this to determine if the container is alive.
    Should return 200 OK if the process is running, regardless of dependency status.
    """
    global startup_time
    
    uptime = time.time() - startup_time if startup_time else 0
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        service=SERVICE_NAME,
        version=VERSION,
        uptime_seconds=round(uptime, 2),
        environment=ENVIRONMENT,
    )


@app.get("/ready", response_model=ReadinessResponse, tags=["Health"])
async def readiness_check():
    """
    Readiness probe - indicates if the service is ready to accept traffic.
    
    Cloud Run uses this to determine if traffic should be routed to this instance.
    Checks dependencies (database, external services, etc.).
    """
    global is_ready
    
    checks = {
        "initialization": is_ready,
        "configuration": _check_configuration(),
        # Add more checks as needed:
        # "database": await _check_database(),
        # "external_api": await _check_external_api(),
    }
    
    all_ready = all(checks.values())
    
    response = ReadinessResponse(
        ready=all_ready,
        timestamp=datetime.now(timezone.utc).isoformat(),
        checks=checks,
        message="Service ready" if all_ready else "Service not ready - check failed dependencies",
    )
    
    if not all_ready:
        return JSONResponse(
            status_code=503,
            content=response.model_dump(),
        )
    
    return response


def _check_configuration() -> bool:
    """Check if configuration is valid."""
    # Add configuration validation logic
    return True


@app.get("/metrics", response_model=MetricsResponse, tags=["Health"])
async def metrics():
    """
    Basic metrics endpoint.
    
    For production, consider integrating with Cloud Monitoring or Prometheus.
    """
    global startup_time
    
    return MetricsResponse(
        uptime_seconds=round(time.time() - startup_time, 2) if startup_time else 0,
        requests_total=0,  # Implement actual counters
        errors_total=0,
        avg_response_time_ms=0.0,
    )


# -----------------------------------------------------------------------------
# Root Endpoint
# -----------------------------------------------------------------------------

@app.get("/", tags=["Status"])
async def root():
    """Root endpoint - basic service information."""
    return {
        "service": SERVICE_NAME,
        "version": VERSION,
        "environment": ENVIRONMENT,
        "status": "operational",
        "docs": "/docs" if ENVIRONMENT != "production" else None,
        "health": "/health",
        "ready": "/ready",
    }


# -----------------------------------------------------------------------------
# Business Logic Endpoints (Import from existing tools)
# -----------------------------------------------------------------------------

# Try to import existing tools if available
try:
    from panelin_agent_v2.tools.quotation_calculator import (
        calculate_panel_quote,
        QuotationResult,
        AccessoriesResult,
    )
    from panelin_agent_v2.tools.product_lookup import (
        find_product_by_query,
        get_product_price,
        check_product_availability,
        list_all_products,
        get_pricing_rules,
    )
    TOOLS_AVAILABLE = True
except ImportError:
    logger.warning("panelin_agent_v2 tools not found - using stub endpoints")
    TOOLS_AVAILABLE = False


# -----------------------------------------------------------------------------
# Request/Response Models
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


class AvailabilityInfo(BaseModel):
    product_id: str
    found: bool
    name: Optional[str] = None
    available: bool
    stock_status: str
    inventory_quantity: Optional[int] = None
    last_updated: Optional[str] = None


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
    discount_percent: float = Field(0.0, description="Porcentaje de descuento aplicable", ge=0, le=30)
    include_accessories: bool = Field(False, description="Incluir cálculo de accesorios")
    include_tax: bool = Field(True, description="Incluir IVA (22%)")
    installation_type: Literal["techo", "pared"] = Field("techo", description="Tipo de instalación")


# -----------------------------------------------------------------------------
# Business Endpoints
# -----------------------------------------------------------------------------

if TOOLS_AVAILABLE:
    @app.get("/products/search", response_model=List[ProductInfo], tags=["Products"])
    async def search_products(
        q: str = Query(..., description="Query de búsqueda"),
        max_results: int = Query(5, ge=1, le=20),
    ):
        """Busca productos basándose en descripción en lenguaje natural."""
        return find_product_by_query(q, max_results=max_results)

    @app.get("/products/{product_id}/price", response_model=PriceInfo, tags=["Products"])
    async def get_price(product_id: str):
        """Obtiene el precio exacto de un producto por su ID."""
        price = get_product_price(product_id)
        if not price:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return price

    @app.get("/products/{product_id}/availability", response_model=AvailabilityInfo, tags=["Products"])
    async def get_availability(product_id: str):
        """Verifica disponibilidad y stock de un producto."""
        return check_product_availability(product_id)

    @app.get("/products", response_model=List[ProductInfo], tags=["Products"])
    async def list_products(family: Optional[str] = None):
        """Lista todos los productos disponibles, opcionalmente filtrados por familia."""
        return list_all_products(family=family)

    @app.post("/quotes", tags=["Quotations"])
    async def create_quote(request: QuoteRequest):
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
    async def get_rules():
        """Obtiene las reglas de precios vigentes (IVA, envíos, etc.)."""
        return get_pricing_rules()
else:
    # Stub endpoints when tools are not available
    @app.get("/products", tags=["Products"])
    async def list_products_stub():
        """Stub endpoint - tools not available."""
        return {"message": "Product tools not configured", "status": "stub"}


# -----------------------------------------------------------------------------
# Error Handlers
# -----------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with proper logging."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if ENVIRONMENT != "production" else "An error occurred",
            "request_id": request.headers.get("X-Request-ID", "unknown"),
        },
    )


# -----------------------------------------------------------------------------
# Main Entry Point (for local development)
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=ENVIRONMENT == "development",
        log_level="info",
    )
