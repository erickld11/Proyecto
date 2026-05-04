from datetime import datetime
from typing import Optional, List
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
    is_admin: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# ── Consumption ───────────────────────────────────────────────────────────────

class ConsumptionCreate(BaseModel):
    month: str
    electricity_kwh: float = 0.0
    gas_kwh: float = 0.0
    water_liters: float = 0.0
    transport_km: float = 0.0
    notes: Optional[str] = None


class ConsumptionUpdate(BaseModel):
    electricity_kwh: Optional[float] = None
    gas_kwh: Optional[float] = None
    water_liters: Optional[float] = None
    transport_km: Optional[float] = None
    notes: Optional[str] = None


class ConsumptionOut(BaseModel):
    id: int
    user_id: int
    month: str
    electricity_kwh: float
    gas_kwh: float
    water_liters: float
    transport_km: float
    carbon_footprint_kg: float
    notes: Optional[str]
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
    total_records: int
    consumptions: List[ConsumptionOut]
    latest_plan: Optional[AIPlanOut]


# ── Admin ─────────────────────────────────────────────────────────────────────

class AdminUserOut(BaseModel):
    id: int
    name: str
    email: str
    company: Optional[str]
    is_admin: bool
    is_active: bool
    created_at: datetime
    total_consumptions: int
    total_carbon_kg: float

    class Config:
        from_attributes = True
