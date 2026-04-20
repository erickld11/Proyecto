from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models.models import Base
from app.routes import auth_router, consumptions_router, dashboard_router

# Crear tablas al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EcoTrack Pro API",
    description="""
## 🌱 EcoTrack Pro — SaaS de Sostenibilidad Empresarial

API REST para gestionar el seguimiento de huella de carbono empresarial.

### Funcionalidades:
- 🔐 Autenticación con JWT y contraseñas cifradas con bcrypt
- 📊 Registro de consumos (electricidad, gas, agua, transporte)
- 🧮 Cálculo automático de huella de carbono (kg CO2)
- 🤖 Planes de acción personalizados con IA (OpenAI GPT)
- 📈 Dashboard con estadísticas y evolución temporal
    """,
    version="1.0.0",
    contact={"name": "EcoTrack Pro", "email": "info@ecotrack.pro"},
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(consumptions_router)
app.include_router(dashboard_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "app": "EcoTrack Pro API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok"}
