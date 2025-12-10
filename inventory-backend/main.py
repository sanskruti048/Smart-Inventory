from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ---------------------------------------------------------
# FastAPI app setup
# ---------------------------------------------------------

app = FastAPI(
    title="Smart Inventory Prediction API",
    description="Backend for Smart Inventory Prediction & Replenishment System",
    version="1.0.0",
)

# CORS – allow your React app + Boltic + local dev
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000",
    "https://asia-south1.api.boltic.io",  # Boltic workflow
    "*",  # Allow all origins for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------

class ItemInput(BaseModel):
    """Input item for prediction (used by /predict-bulk)."""
    sku_id: str
    store_id: str
    current_stock: int
    sales_last_30_days: int
    category: Optional[str] = None
    city: Optional[str] = None


class Prediction(BaseModel):
    """Final prediction object returned to frontend."""
    sku_id: str
    store_id: str
    current_stock: int
    avg_daily_sales: float
    days_to_stockout: float
    status: str
    recommended_reorder_quantity: int
    category: Optional[str] = None
    city: Optional[str] = None
    last_updated: datetime


class PredictBulkRequest(BaseModel):
    """Request body for /predict-bulk."""
    items: List[ItemInput]


class LatestResponse(BaseModel):
    """Response returned by /latest."""
    predictions: List[Prediction]
    last_updated: Optional[datetime]


# Models used specifically for /ingest (data coming from Boltic)

class PredictionIn(BaseModel):
    sku_id: str
    store_id: str
    current_stock: int
    avg_daily_sales: float
    days_to_stockout: float
    status: str
    recommended_reorder_quantity: int
    category: Optional[str] = None
    city: Optional[str] = None


class IngestRequest(BaseModel):
    predictions: List[PredictionIn]


# ---------------------------------------------------------
# In-memory storage
# (Render dyno will reset sometimes; fine for demo)
# ---------------------------------------------------------

LAST_PREDICTIONS: List[Prediction] = []
LAST_UPDATED_AT: Optional[datetime] = None


# ---------------------------------------------------------
# Core prediction logic (same algorithm used everywhere)
# ---------------------------------------------------------

DAYS_WINDOW = 30        # we measure sales over last 30 days
TARGET_DAYS = 14        # we want 14 days of coverage in stock


def compute_prediction(item: ItemInput, as_of: datetime) -> Prediction:
    """Take one item and compute stockout risk + reorder quantity."""
    current_stock = item.current_stock
    sales_last_30 = item.sales_last_30_days

    # avg sales per day
    avg_daily_sales = sales_last_30 / DAYS_WINDOW if DAYS_WINDOW > 0 else float(
        sales_last_30
    )

    # days until stock runs out
    if avg_daily_sales == 0:
        days_to_stockout = float("inf")
    else:
        days_to_stockout = current_stock / avg_daily_sales

    # risk bucket
    if days_to_stockout < 3:
        status = "Critical"
    elif days_to_stockout < 7:
        status = "Warning"
    else:
        status = "Safe"

    # reorder quantity (to cover next TARGET_DAYS days)
    if avg_daily_sales == 0:
        recommended_reorder_quantity = 0
    else:
        desired_stock = TARGET_DAYS * avg_daily_sales
        recommended_reorder_quantity = max(
            0, round(desired_stock - current_stock)
        )

    return Prediction(
        sku_id=item.sku_id,
        store_id=item.store_id,
        current_stock=current_stock,
        avg_daily_sales=avg_daily_sales,
        days_to_stockout=days_to_stockout,
        status=status,
        recommended_reorder_quantity=recommended_reorder_quantity,
        category=item.category,
        city=item.city,
        last_updated=as_of,
    )


# ---------------------------------------------------------
# Endpoints
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring and deployments."""
    return {"status": "healthy", "service": "Smart Inventory API"}


@app.post("/predict-bulk", response_model=LatestResponse)
def predict_bulk(request: PredictBulkRequest):
    """
    Local/manual prediction API.
    You can test this from Swagger UI or Postman.
    Also useful if you want to bypass Boltic and just hit the backend.
    
    Example:
    POST /predict-bulk
    {
      "items": [
        {
          "sku_id": "TSHIRT_RED_M",
          "store_id": "STORE_001",
          "current_stock": 100,
          "sales_last_30_days": 30
        }
      ]
    }
    """
    global LAST_PREDICTIONS, LAST_UPDATED_AT
    now = datetime.utcnow()

    predictions: List[Prediction] = [
        compute_prediction(item, as_of=now) for item in request.items
    ]

    LAST_PREDICTIONS = predictions
    LAST_UPDATED_AT = now

    return LatestResponse(predictions=predictions, last_updated=LAST_UPDATED_AT)


@app.get("/latest", response_model=LatestResponse)
def get_latest():
    """
    Returns the last set of predictions generated, either by /predict-bulk
    or by /ingest (from Boltic).
    This is what your React dashboard calls to display inventory health.
    """
    return LatestResponse(
        predictions=LAST_PREDICTIONS,
        last_updated=LAST_UPDATED_AT,
    )


@app.post("/ingest")
def ingest_predictions(request: IngestRequest):
    """
    BOLTIC INTEGRATION ENDPOINT.
    
    Boltic workflow will POST its computed predictions here.
    Boltic sends data in this format:

    POST /ingest
    {
      "predictions": [
        {
          "sku_id": "TSHIRT_RED_M",
          "store_id": "STORE_001",
          "current_stock": 100,
          "avg_daily_sales": 2.5,
          "days_to_stockout": 40.0,
          "status": "Safe",
          "recommended_reorder_quantity": 50,
          "category": "T-Shirts",
          "city": "Mumbai"
        }
      ]
    }

    We convert those into Prediction objects and update LAST_PREDICTIONS,
    so /latest and the React dashboard see the latest Boltic run.
    
    Returns:
    {
      "status": "ok",
      "count": 5,
      "message": "5 predictions ingested successfully"
    }
    """
    global LAST_PREDICTIONS, LAST_UPDATED_AT
    now = datetime.utcnow()

    converted: List[Prediction] = [
        Prediction(
            sku_id=p.sku_id,
            store_id=p.store_id,
            current_stock=p.current_stock,
            avg_daily_sales=p.avg_daily_sales,
            days_to_stockout=p.days_to_stockout,
            status=p.status,
            recommended_reorder_quantity=p.recommended_reorder_quantity,
            category=p.category,
            city=p.city,
            last_updated=now,
        )
        for p in request.predictions
    ]

    LAST_PREDICTIONS = converted
    LAST_UPDATED_AT = now

    return {
        "status": "ok",
        "count": len(converted),
        "message": f"{len(converted)} predictions ingested successfully"
    }


@app.get("/")
def root():
    """Root endpoint - API info."""
    return {
        "service": "Smart Inventory Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "predict": "/predict-bulk",
            "latest": "/latest",
            "ingest": "/ingest"
        }
    }


# Optional: local dev entrypoint
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
