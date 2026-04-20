from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
    ForeignKey, Text, Boolean,
)
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """Usuario de la plataforma."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    company = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    consumptions = relationship("Consumption", back_populates="user", cascade="all, delete")
    ai_plans = relationship("AIPlan", back_populates="user", cascade="all, delete")


class Consumption(Base):
    """Registro de consumo energético."""

    __tablename__ = "consumptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    month = Column(String(7), nullable=False)  # formato: 2025-01
    electricity_kwh = Column(Float, default=0.0)
    gas_kwh = Column(Float, default=0.0)
    water_liters = Column(Float, default=0.0)
    transport_km = Column(Float, default=0.0)
    # Huella de carbono calculada en kg CO2
    carbon_footprint_kg = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="consumptions")


class AIPlan(Base):
    """Plan de acción personalizado generado por IA."""

    __tablename__ = "ai_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    consumption_id = Column(Integer, ForeignKey("consumptions.id"), nullable=True)
    plan_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="ai_plans")
