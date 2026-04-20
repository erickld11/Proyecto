from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Consumption, AIPlan
from app.schemas import ConsumptionCreate, ConsumptionUpdate, ConsumptionOut, AIPlanOut, DashboardStats
from app.services import get_current_user, calculate_carbon_footprint, get_carbon_breakdown, generate_action_plan

router = APIRouter(prefix="/api/consumptions", tags=["Consumos"])


@router.post("", response_model=ConsumptionOut, status_code=201)
def create_consumption(
    data: ConsumptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Registra un nuevo consumo mensual y calcula la huella de carbono."""
    existing = db.query(Consumption).filter(
        Consumption.user_id == current_user.id,
        Consumption.month == data.month,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Ya existe un registro para {data.month}")

    carbon = calculate_carbon_footprint(
        data.electricity_kwh, data.gas_kwh,
        data.water_liters, data.transport_km,
    )

    consumption = Consumption(
        user_id=current_user.id,
        month=data.month,
        electricity_kwh=data.electricity_kwh,
        gas_kwh=data.gas_kwh,
        water_liters=data.water_liters,
        transport_km=data.transport_km,
        carbon_footprint_kg=carbon,
    )
    db.add(consumption)
    db.commit()
    db.refresh(consumption)
    return consumption


@router.get("", response_model=List[ConsumptionOut])
def list_consumptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todos los consumos del usuario autenticado."""
    return db.query(Consumption).filter(
        Consumption.user_id == current_user.id
    ).order_by(Consumption.month.desc()).all()


@router.get("/{consumption_id}", response_model=ConsumptionOut)
def get_consumption(
    consumption_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene un consumo específico del usuario."""
    consumption = db.query(Consumption).filter(
        Consumption.id == consumption_id,
        Consumption.user_id == current_user.id,
    ).first()
    if not consumption:
        raise HTTPException(status_code=404, detail="Consumo no encontrado")
    return consumption


@router.patch("/{consumption_id}", response_model=ConsumptionOut)
def update_consumption(
    consumption_id: int,
    data: ConsumptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza un registro de consumo y recalcula la huella."""
    consumption = db.query(Consumption).filter(
        Consumption.id == consumption_id,
        Consumption.user_id == current_user.id,
    ).first()
    if not consumption:
        raise HTTPException(status_code=404, detail="Consumo no encontrado")

    if data.electricity_kwh is not None:
        consumption.electricity_kwh = data.electricity_kwh
    if data.gas_kwh is not None:
        consumption.gas_kwh = data.gas_kwh
    if data.water_liters is not None:
        consumption.water_liters = data.water_liters
    if data.transport_km is not None:
        consumption.transport_km = data.transport_km

    consumption.carbon_footprint_kg = calculate_carbon_footprint(
        consumption.electricity_kwh, consumption.gas_kwh,
        consumption.water_liters, consumption.transport_km,
    )
    db.commit()
    db.refresh(consumption)
    return consumption


@router.delete("/{consumption_id}", status_code=204)
def delete_consumption(
    consumption_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina un registro de consumo."""
    consumption = db.query(Consumption).filter(
        Consumption.id == consumption_id,
        Consumption.user_id == current_user.id,
    ).first()
    if not consumption:
        raise HTTPException(status_code=404, detail="Consumo no encontrado")
    db.delete(consumption)
    db.commit()


@router.post("/{consumption_id}/ai-plan", response_model=AIPlanOut)
def generate_plan(
    consumption_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Genera un plan de acción con IA para un consumo específico."""
    consumption = db.query(Consumption).filter(
        Consumption.id == consumption_id,
        Consumption.user_id == current_user.id,
    ).first()
    if not consumption:
        raise HTTPException(status_code=404, detail="Consumo no encontrado")

    # Buscar consumo del mes anterior para comparar
    consumptions = db.query(Consumption).filter(
        Consumption.user_id == current_user.id,
    ).order_by(Consumption.month.asc()).all()

    previous_carbon = None
    for i, c in enumerate(consumptions):
        if c.id == consumption_id and i > 0:
            previous_carbon = consumptions[i - 1].carbon_footprint_kg

    plan_text = generate_action_plan(
        month=consumption.month,
        electricity_kwh=consumption.electricity_kwh,
        gas_kwh=consumption.gas_kwh,
        water_liters=consumption.water_liters,
        transport_km=consumption.transport_km,
        carbon_kg=consumption.carbon_footprint_kg,
        previous_carbon_kg=previous_carbon,
    )

    plan = AIPlan(
        user_id=current_user.id,
        consumption_id=consumption_id,
        plan_text=plan_text,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/breakdown/{consumption_id}")
def get_breakdown(
    consumption_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Devuelve el desglose de emisiones por categoría."""
    consumption = db.query(Consumption).filter(
        Consumption.id == consumption_id,
        Consumption.user_id == current_user.id,
    ).first()
    if not consumption:
        raise HTTPException(status_code=404, detail="Consumo no encontrado")

    return get_carbon_breakdown(
        consumption.electricity_kwh, consumption.gas_kwh,
        consumption.water_liters, consumption.transport_km,
    )
