"""
Panelin V3 API - FastAPI wrapper for quotation calculator
==========================================================

FastAPI service that exposes the Panelin V3 quotation calculator via REST API.
Designed for deployment on Google Cloud Run.

ENDPOINTS:
- POST /v3/quote - Calculate panel quotation
- GET /health - Health check endpoint
- GET / - API documentation
"""

import sys
from pathlib import Path

# Add the 03_PYTHON_TOOLS directory to Python path
tools_path = Path(__file__).parent.parent.parent / "03_PYTHON_TOOLS"
sys.path.insert(0, str(tools_path))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal
import os
from decimal import Decimal

# Import the calculator after path is set
from quotation_calculator_v3 import calculate_panel_quote

app = FastAPI(
    title="Panelin V3 API",
    description="BMC Uruguay Panel Quotation Calculator API",
    version="3.1.0"
)


class QuoteRequest(BaseModel):
    """Request model for quotation calculation"""
    product_id: str = Field(..., description="Product identifier (e.g., 'ISOPANEL_EPS_50mm')")
    length_m: float = Field(..., gt=0, description="Panel length in meters")
    width_m: float = Field(..., gt=0, description="Total width to cover in meters")
    quantity: int = Field(1, ge=1, description="Number of panels/installations")
    discount_percent: float = Field(0.0, ge=0, le=30, description="Discount percentage")
    include_accessories: bool = Field(False, description="Include accessories in calculation")
    include_tax: bool = Field(True, description="Include IVA (22%)")
    installation_type: Literal["techo", "pared"] = Field("techo", description="Installation type")
    validate_span: bool = Field(True, description="Validate autoportancia limits")


class QuoteResponse(BaseModel):
    """Response model for quotation"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """API documentation and welcome message"""
    return {
        "service": "Panelin V3 API",
        "version": "3.1.0",
        "endpoints": {
            "/v3/quote": "POST - Calculate panel quotation",
            "/health": "GET - Health check",
            "/docs": "Swagger UI documentation",
            "/redoc": "ReDoc documentation"
        },
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {
        "status": "healthy",
        "service": "panelin-v3-api",
        "version": "3.1.0"
    }


@app.post("/v3/quote", response_model=QuoteResponse)
async def calculate_quote(request: QuoteRequest):
    """
    Calculate panel quotation with full validation.
    
    Returns deterministic calculation results including:
    - Panel specifications and pricing
    - Autoportancia validation
    - Accessories (if requested)
    - Tax calculations
    """
    try:
        # Call the deterministic calculator
        result = calculate_panel_quote(
            product_id=request.product_id,
            length_m=request.length_m,
            width_m=request.width_m,
            quantity=request.quantity,
            discount_percent=request.discount_percent,
            include_accessories=request.include_accessories,
            include_tax=request.include_tax,
            installation_type=request.installation_type,
            validate_span=request.validate_span
        )
        
        # Convert Decimal values to float for JSON serialization
        serializable_result = _convert_decimals_to_float(result)
        
        return QuoteResponse(
            success=True,
            data=serializable_result
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


def _convert_decimals_to_float(obj):
    """Recursively convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: _convert_decimals_to_float(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_decimals_to_float(item) for item in obj]
    else:
        return obj


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
