
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.performance_analytics import PerformanceAnalytics
from app.models.usage_analytics import UsageAnalytics
from typing import List, Optional

router = APIRouter()


@app.get("/analytics/performance", response_model=List[PerformanceAnalytics])
def get_performance_analytics(db: Session = Depends(get_db)):
    performance_data = db.query(PerformanceAnalytics).all()
    if not performance_data:
        raise HTTPException(status_code=404, detail="No performance analytics data found")
    return performance_data


@app.get("/analytics/usage", response_model=List[UsageAnalytics])
def get_usage_analytics(db: Session = Depends(get_db)):
    usage_data = db.query(UsageAnalytics).all()
    if not usage_data:
        raise HTTPException(status_code=404, detail="No usage analytics data found")
    return usage_data
