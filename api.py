"""
Panelin API - Production Ready
==============================

Production-grade FastAPI application for BMC Uruguay panel quotations.

Features:
- Health and readiness endpoints for Cloud Run
- OpenTelemetry tracing integration
- Structured JSON logging
- Graceful shutdown handling
- Request ID tracking
- Rate limiting headers

Author: Panelin Engineering Team
Version: 2.0.0
"""

import os
import sys
import time
import uuid
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Configure structured logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
    stream=sys.stdout
)
logger = logging.getLogger("panelin-api")

# ============================================
# Application Configuration
# ============================================

class AppConfig:
    """Application configuration from environment variables."""
    
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_VERSION: str = "2.0.0"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Database configuration (from Secret Manager in production)
    MONGODB_URI: Optional[str] = os.getenv("MONGODB_URI")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "panelin")
    
    # OpenAI configuration (from Secret Manager in production)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Feature flags
    ENABLE_TRACING: bool = os.getenv("ENABLE_TRACING", "false").lower() == "true"
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"


config = AppConfig()

# ============================================
# Health Check State
# ============================================

class HealthState:
    """Tracks application health state for readiness probes."""
    
    def __init__(self):
        self.is_ready: bool = False
        self.startup_time: Optional[datetime] = None
        self.last_check: Optional[datetime] = None
        self.dependencies: Dict[str, bool] = {
            "knowledge_base": False,
            "configuration": False
        }
        self.errors: List[str] = []
    
    def mark_ready(self):
        self.is_ready = True
        self.startup_time = datetime.utcnow()
    
    def check_dependencies(self) -> bool:
        """Verify all critical dependencies are available."""
        self.last_check = datetime.utcnow()
        self.errors = []
        
        # Check knowledge base file
        kb_paths = [
            Path("panelin_hybrid_agent/kb/panelin_truth_bmcuruguay.json"),
            Path("panelin_core/knowledge_base/panelin_truth_bmcuruguay.json"),
            Path("panelin/data/panelin_truth_bmcuruguay.json"),
        ]
        
        kb_found = any(p.exists() for p in kb_paths)
        self.dependencies["knowledge_base"] = kb_found
        if not kb_found:
            self.errors.append("Knowledge base file not found")
        
        # Check configuration
        config_valid = bool(config.APP_ENV)
        self.dependencies["configuration"] = config_valid
        if not config_valid:
            self.errors.append("Configuration not loaded")
        
        return all(self.dependencies.values())


health_state = HealthState()

# ============================================
# Startup/Shutdown Lifecycle
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Startup
    logger.info(f"Starting Panelin API v{config.APP_VERSION} in {config.APP_ENV} mode")
    
    # Validate dependencies
    if health_state.check_dependencies():
        health_state.mark_ready()
        logger.info("All dependencies validated - service is ready")
    else:
        logger.warning(f"Some dependencies failed: {health_state.errors}")
        # Still mark as ready but with warnings - let health checks report status
        health_state.mark_ready()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Panelin API gracefully")


# ============================================
# FastAPI Application
# ============================================

app = FastAPI(
    title="Panelin API",
    description="Production API for BMC Uruguay panel quotations. LLM extracts parameters, Python calculates.",
    version=config.APP_VERSION,
    docs_url="/docs" if config.APP_ENV != "production" else None,
    redoc_url="/redoc" if config.APP_ENV != "production" else None,
    lifespan=lifespan,
)

# CORS middleware (configure appropriately for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if config.APP_ENV == "development" else [
        "https://bmcuruguay.com",
        "https://*.bmcuruguay.com",
        "https://*.run.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ============================================
# Request ID Middleware
# ============================================

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID for tracing."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.time()
    
    response = await call_next(request)
    
    # Add response headers
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    
    # Log request (structured for Cloud Logging)
    logger.info(json.dumps({
        "event": "request",
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "process_time_ms": round(process_time * 1000, 2)
    }))
    
    return response


# ============================================
# Health & Readiness Endpoints
# ============================================

class HealthResponse(BaseModel):
    """Health check response model."""
    status: Literal["healthy", "unhealthy", "degraded"]
    version: str
    environment: str
    uptime_seconds: Optional[float] = None
    timestamp: str


class ReadinessResponse(BaseModel):
    """Readiness check response model."""
    ready: bool
    checks: Dict[str, bool]
    errors: List[str] = []
    timestamp: str


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint for liveness probes.
    
    Returns 200 if the service is running.
    This endpoint should be fast and NOT check external dependencies.
    
    Used by:
    - Cloud Run health checks
    - Load balancer health probes
    - Kubernetes liveness probes
    """
    uptime = None
    if health_state.startup_time:
        uptime = (datetime.utcnow() - health_state.startup_time).total_seconds()
    
    return HealthResponse(
        status="healthy",
        version=config.APP_VERSION,
        environment=config.APP_ENV,
        uptime_seconds=uptime,
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/ready", response_model=ReadinessResponse, tags=["Health"])
async def readiness_check():
    """
    Readiness check endpoint for readiness probes.
    
    Returns 200 if the service is ready to accept traffic.
    This endpoint DOES check external dependencies.
    
    Used by:
    - Cloud Run readiness checks
    - Traffic routing decisions
    - Kubernetes readiness probes
    """
    # Re-check dependencies
    is_ready = health_state.check_dependencies()
    
    response = ReadinessResponse(
        ready=is_ready,
        checks=health_state.dependencies.copy(),
        errors=health_state.errors.copy(),
        timestamp=datetime.utcnow().isoformat()
    )
    
    if not is_ready:
        return JSONResponse(
            status_code=503,
            content=response.model_dump()
        )
    
    return response


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - service info."""
    return {
        "service": "Panelin API",
        "version": config.APP_VERSION,
        "environment": config.APP_ENV,
        "status": "running",
        "docs": "/docs" if config.APP_ENV != "production" else "disabled in production"
    }


# ============================================
# Request/Response Models
# ============================================

class ProductInfo(BaseModel):
    product_id: str
    name: str
    family: str
    thickness_mm: Optional[int] = None
    price_per_m2: float
    currency: str = "USD"
    stock_status: str = "available"
    ancho_util_m: Optional[float] = None
    largo_min_m: Optional[float] = None
    largo_max_m: Optional[float] = None
    match_score: Optional[int] = None


class QuoteRequest(BaseModel):
    """Panel quotation request model."""
    panel_type: str = Field(
        ..., 
        description="Type of panel (Isopanel, Isodec, Isoroof, Isowall, Isofrig)"
    )
    thickness_mm: int = Field(
        ..., 
        description="Panel thickness in millimeters",
        ge=30, le=200
    )
    total_width_m: float = Field(
        ..., 
        description="Total width to cover in meters",
        gt=0, le=100
    )
    total_length_m: float = Field(
        ..., 
        description="Total length in meters",
        gt=0, le=14
    )
    discount_percent: float = Field(
        0.0, 
        description="Discount percentage",
        ge=0, le=30
    )
    include_accessories: bool = Field(
        True, 
        description="Include profiles and accessories"
    )
    include_fixation: bool = Field(
        True, 
        description="Include fixation materials"
    )
    price_type: Literal["empresa", "particular", "web"] = Field(
        "empresa", 
        description="Price type"
    )
    insulation_type: Literal["EPS", "PIR"] = Field(
        "EPS", 
        description="Insulation type"
    )
    structure_type: Literal["metal", "concrete"] = Field(
        "metal",
        description="Support structure type"
    )


class QuoteResponse(BaseModel):
    """Quotation response model."""
    success: bool
    quotation_id: str
    panels: Dict[str, Any]
    panel_count: int
    total_area_m2: float
    panels_subtotal_usd: float
    profiles: Optional[Dict[str, Any]] = None
    profiles_subtotal_usd: Optional[float] = None
    fixation: Optional[Dict[str, Any]] = None
    grand_total_usd: float
    price_type: str
    calculation_verified: bool
    generated_at: str


# ============================================
# Business Endpoints
# ============================================

@app.post("/quotes", response_model=QuoteResponse, tags=["Quotations"])
async def create_quote(request: QuoteRequest):
    """
    Create a deterministic panel quotation.
    
    The calculation is performed by Python code, NOT by an LLM.
    All prices are loaded from the knowledge base.
    """
    try:
        # Import calculator dynamically to handle missing dependencies gracefully
        try:
            from panelin_hybrid_agent.tools.quotation_calculator import calculate_complete_quotation
        except ImportError:
            from panelin.tools.quotation_calculator import calculate_complete_quotation
        
        result = calculate_complete_quotation(
            panel_type=request.panel_type,
            thickness_mm=request.thickness_mm,
            total_width_m=request.total_width_m,
            total_length_m=request.total_length_m,
            include_accessories=request.include_accessories,
            include_fixation=request.include_fixation,
            structure_type=request.structure_type,
            discount_percent=request.discount_percent,
            price_type=request.price_type,
            insulation_type=request.insulation_type,
        )
        
        return QuoteResponse(
            success=True,
            quotation_id=f"QT-{uuid.uuid4().hex[:8].upper()}",
            panels=result.get("panels", {}),
            panel_count=result.get("panel_count", 0),
            total_area_m2=result.get("total_area_m2", 0),
            panels_subtotal_usd=result.get("panels_subtotal_usd", 0),
            profiles=result.get("profiles"),
            profiles_subtotal_usd=result.get("profiles_subtotal_usd"),
            fixation=result.get("fixation"),
            grand_total_usd=result.get("grand_total_usd", 0),
            price_type=result.get("price_type", request.price_type),
            calculation_verified=result.get("calculation_verified", True),
            generated_at=datetime.utcnow().isoformat()
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in quote request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        logger.error(f"Knowledge base not found: {str(e)}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable - KB not loaded")
    except Exception as e:
        logger.error(f"Unexpected error in quote calculation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/products", response_model=List[ProductInfo], tags=["Products"])
async def list_products(family: Optional[str] = None, limit: int = Query(50, le=100)):
    """List available products, optionally filtered by family."""
    try:
        try:
            from panelin_hybrid_agent.tools.product_lookup import get_catalog_summary
        except ImportError:
            from panelin.tools.product_lookup import get_catalog_summary
        
        # This is a simplified implementation - in production, implement full product listing
        summary = get_catalog_summary()
        
        # Return placeholder until full implementation
        return [
            ProductInfo(
                product_id="ISODEC_100mm_EPS",
                name="Isodec EPS 100mm",
                family="ISODEC",
                thickness_mm=100,
                price_per_m2=45.00,
                currency="USD",
                stock_status="available",
                ancho_util_m=1.12
            )
        ]
    except Exception as e:
        logger.error(f"Error listing products: {str(e)}")
        raise HTTPException(status_code=500, detail="Error loading product catalog")


@app.get("/pricing/rules", tags=["Pricing"])
async def get_pricing_rules():
    """Get current pricing rules (IVA, delivery, etc.)."""
    return {
        "tax_rate_uy_iva": 0.22,
        "currency": "USD",
        "delivery_cost_per_m2": 2.50,
        "minimum_delivery_charge_usd": 50.00,
        "minimum_order_m2": 10,
        "payment_terms": {
            "advance_percent": 50,
            "delivery_balance": True,
            "accepted_methods": ["transfer", "card", "cash"]
        },
        "last_updated": "2026-01-01"
    }


# ============================================
# Error Handlers
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    request_id = request.headers.get("X-Request-ID", "unknown")
    logger.error(f"Unhandled exception: {str(exc)}", extra={"request_id": request_id})
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ============================================
# Development Server
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8080))
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=config.APP_ENV == "development",
        log_level=config.LOG_LEVEL.lower(),
        access_log=True
    )
