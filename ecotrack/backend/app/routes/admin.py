from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Consumption, AIPlan
from app.schemas import AdminUserOut, UserUpdate, UserOut
from app.services import get_current_user, require_admin, hash_password

router = APIRouter(prefix="/api/admin", tags=["Administración"])


@router.get("/users", response_model=List[AdminUserOut])
def list_all_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """ADMIN: Lista todos los usuarios con sus estadísticas de consumo."""
    users = db.query(User).all()
    result = []
    for user in users:
        consumptions = db.query(Consumption).filter(Consumption.user_id == user.id).all()
        total_carbon = sum(c.carbon_footprint_kg for c in consumptions)
        result.append(AdminUserOut(
            id=user.id, name=user.name, email=user.email,
            company=user.company, is_admin=user.is_admin,
            is_active=user.is_active, created_at=user.created_at,
            total_consumptions=len(consumptions),
            total_carbon_kg=round(total_carbon, 2),
        ))
    return result


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """ADMIN: Modifica datos de cualquier usuario (nombre, empresa, rol, estado)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if data.name is not None:
        user.name = data.name
    if data.company is not None:
        user.company = data.company
    if data.is_admin is not None:
        user.is_admin = data.is_admin
    if data.is_active is not None:
        user.is_active = data.is_active

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """ADMIN: Elimina un usuario y todos sus datos."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")

    db.query(AIPlan).filter(AIPlan.user_id == user_id).delete()
    db.query(Consumption).filter(Consumption.user_id == user_id).delete()
    db.delete(user)
    db.commit()


@router.get("/consumptions", response_model=List[dict])
def list_all_consumptions(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """ADMIN: Ve los consumos de TODOS los usuarios."""
    consumptions = db.query(Consumption).order_by(Consumption.created_at.desc()).all()
    result = []
    for c in consumptions:
        user = db.query(User).filter(User.id == c.user_id).first()
        result.append({
            "id": c.id, "user_id": c.user_id,
            "user_name": user.name if user else "Desconocido",
            "user_email": user.email if user else "",
            "company": user.company if user else "",
            "month": c.month,
            "electricity_kwh": c.electricity_kwh,
            "gas_kwh": c.gas_kwh,
            "water_liters": c.water_liters,
            "transport_km": c.transport_km,
            "carbon_footprint_kg": c.carbon_footprint_kg,
        })
    return result


@router.get("/stats")
def global_stats(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """ADMIN: Estadísticas globales de toda la plataforma."""
    total_users = db.query(User).count()
    total_consumptions = db.query(Consumption).count()
    all_consumptions = db.query(Consumption).all()
    total_carbon = sum(c.carbon_footprint_kg for c in all_consumptions)
    total_plans = db.query(AIPlan).count()

    return {
        "total_users": total_users,
        "total_consumptions": total_consumptions,
        "total_carbon_kg": round(total_carbon, 2),
        "total_ai_plans": total_plans,
        "avg_carbon_per_record": round(total_carbon / total_consumptions, 2) if total_consumptions > 0 else 0,
    }


@router.post("/seed-demo-data", status_code=201)
def seed_demo_data(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """ADMIN: Inserta 12 meses de datos de demostración para el usuario admin."""
    import random
    months = [
        "2025-05", "2025-06", "2025-07", "2025-08", "2025-09", "2025-10",
        "2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04",
    ]
    from app.services.carbon import calculate_carbon_footprint
    created = 0
    for month in months:
        existing = db.query(Consumption).filter(
            Consumption.user_id == admin.id, Consumption.month == month
        ).first()
        if existing:
            continue
        elec = round(random.uniform(280, 620), 1)
        gas = round(random.uniform(150, 480), 1)
        water = round(random.uniform(2800, 7500), 0)
        transport = round(random.uniform(400, 1400), 0)
        carbon = calculate_carbon_footprint(elec, gas, water, transport)
        db.add(Consumption(
            user_id=admin.id, month=month,
            electricity_kwh=elec, gas_kwh=gas,
            water_liters=water, transport_km=transport,
            carbon_footprint_kg=carbon,
            notes="Datos de demostración",
        ))
        created += 1
    db.commit()
    return {"message": f"Se insertaron {created} meses de datos de demostración", "months_created": created}
