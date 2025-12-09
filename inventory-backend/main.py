from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000",
    "http://localhost",
    "*",  # Allow all origins for development; restrict in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Health check endpoint for Render deployment"""
    return {"status": "healthy"}

# -----------------------------
# 1. Request & Response Models
# -----------------------------

class ItemInput(BaseModel):
    sku_id: str
    store_id: str
    current_stock: int
    sales_last_30_days: int

class PredictBulkRequest(BaseModel):
    items: List[ItemInput]

class Prediction(BaseModel):
    sku_id: str
    store_id: str
    current_stock: int
    avg_daily_sales: float
    days_to_stockout: float
    status: str
    recommended_reorder_quantity: int
    last_updated: datetime

class LatestResponse(BaseModel):
    records: List[Prediction]


# -----------------------------
# 2. In-memory storage
# -----------------------------

LAST_PREDICTIONS: List[Prediction] = []


# -----------------------------
# 3. Core prediction logic
# -----------------------------

def compute_prediction(
    item: ItemInput, days_window: int = 30, target_days: int = 14
) -> Prediction:
    current_stock = item.current_stock
    sales_last_30_days = item.sales_last_30_days

    if days_window <= 0:
        days_window = 1

    avg_daily_sales = sales_last_30_days / days_window

    if avg_daily_sales == 0:
        days_to_stockout = float("inf")
    else:
        days_to_stockout = current_stock / avg_daily_sales

    # classify status
    if days_to_stockout < 3:
        status = "Critical"
    elif days_to_stockout < 7:
        status = "Warning"
    else:
        status = "Safe"

    # reorder quantity
    if avg_daily_sales == 0:
        recommended_reorder_quantity = 0
    else:
        desired_stock = target_days * avg_daily_sales
        recommended_reorder_quantity = max(0, int(desired_stock - current_stock))

    return Prediction(
        sku_id=item.sku_id,
        store_id=item.store_id,
        current_stock=current_stock,
        avg_daily_sales=avg_daily_sales,
        days_to_stockout=days_to_stockout,
        status=status,
        recommended_reorder_quantity=recommended_reorder_quantity,
        last_updated=datetime.utcnow(),
    )


# -----------------------------
# 4. API Endpoints
# -----------------------------

@app.post("/predict-bulk", response_model=LatestResponse)
def predict_bulk(request: PredictBulkRequest):
    """
    Takes a list of items and returns predictions.
    Also stores them in LAST_PREDICTIONS for /latest.
    """
    global LAST_PREDICTIONS

    predictions: List[Prediction] = [
        compute_prediction(item) for item in request.items
    ]

    LAST_PREDICTIONS = predictions  # overwrite last results

    return LatestResponse(records=predictions)


@app.get("/latest", response_model=LatestResponse)
def get_latest():
    """
    Returns the last predictions computed.
    """
    return LatestResponse(records=LAST_PREDICTIONS)
