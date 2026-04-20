from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    company: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    company: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# ── Consumption ───────────────────────────────────────────────────────────────

class ConsumptionCreate(BaseModel):
    month: str  # YYYY-MM
    electricity_kwh: float = 0.0
    gas_kwh: float = 0.0
    water_liters: float = 0.0
    transport_km: float = 0.0


class ConsumptionUpdate(BaseModel):
    electricity_kwh: Optional[float] = None
    gas_kwh: Optional[float] = None
    water_liters: Optional[float] = None
    transport_km: Optional[float] = None


class ConsumptionOut(BaseModel):
    id: int
    user_id: int
    month: str
    electricity_kwh: float
    gas_kwh: float
    water_liters: float
    transport_km: float
    carbon_footprint_kg: float
    created_at: datetime

    class Config:
        from_attributes = True


# ── AI Plan ───────────────────────────────────────────────────────────────────

class AIPlanOut(BaseModel):
    id: int
    user_id: int
    consumption_id: Optional[int]
    plan_text: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_carbon_kg: float
    avg_carbon_kg: float
    best_month: Optional[str]
    worst_month: Optional[str]
    consumptions: list[ConsumptionOut]
    latest_plan: Optional[AIPlanOut]
