from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Consumption, AIPlan
from app.schemas import DashboardStats
from app.services import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardStats)
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Estadísticas del usuario para el dashboard con gráficos."""
    consumptions = db.query(Consumption).filter(
        Consumption.user_id == current_user.id
    ).order_by(Consumption.month.asc()).all()

    if not consumptions:
        return DashboardStats(
            total_carbon_kg=0, avg_carbon_kg=0,
            best_month=None, worst_month=None,
            total_records=0, consumptions=[], latest_plan=None,
        )

    total = sum(c.carbon_footprint_kg for c in consumptions)
    avg = total / len(consumptions)
    best = min(consumptions, key=lambda c: c.carbon_footprint_kg)
    worst = max(consumptions, key=lambda c: c.carbon_footprint_kg)

    latest_plan = db.query(AIPlan).filter(
        AIPlan.user_id == current_user.id
    ).order_by(AIPlan.created_at.desc()).first()

    return DashboardStats(
        total_carbon_kg=round(total, 2),
        avg_carbon_kg=round(avg, 2),
        best_month=best.month,
        worst_month=worst.month,
        total_records=len(consumptions),
        consumptions=list(reversed(consumptions)),
        latest_plan=latest_plan,
    )
