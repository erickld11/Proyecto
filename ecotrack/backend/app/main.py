from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
import time
from app.database import engine
from app.models.models import Base
from app.routes import auth_router, consumptions_router, dashboard_router, admin_router


def create_tables_with_retry(retries=10, delay=5):
    """Espera a que MySQL esté listo antes de crear las tablas."""
    for attempt in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            print(f"✅ Tablas creadas correctamente")
            return
        except Exception as e:
            print(f"⏳ Intento {attempt + 1}/{retries} — MySQL no listo aún: {e}")
            time.sleep(delay)
    raise RuntimeError("No se pudo conectar a MySQL después de varios intentos")

create_tables_with_retry()

app = FastAPI(
    title="EcoTrack Pro API",
    description="""
## 🌱 EcoTrack Pro — SaaS de Sostenibilidad Empresarial

### Cómo usar Swagger:
1. Haz **POST /api/auth/login** → copia el `access_token`
2. Pulsa **Authorize** → escribe `Bearer <token>`
3. Ya puedes usar todos los endpoints 🔓

### Funcionalidades:
- 🔐 JWT + bcrypt | 👑 Roles admin/usuario | 📊 CRUD consumos
- 🧮 Cálculo CO2 automático | 🤖 Planes IA | 📈 Dashboard gráficos
- 📥 Exportación CSV | 🌐 Datos de demo | 👥 Gestión usuarios (admin)
    """,
    version="2.0.0",
    docs_url=None,
    redoc_url=None,
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
app.include_router(admin_router)


@app.get("/", tags=["Root"])
def root():
    return {"app": "EcoTrack Pro API", "version": "2.0.0", "docs": "/docs", "redoc": "/redoc"}


@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok"}


@app.get("/openapi.json", include_in_schema=False)
def custom_openapi():
    if app.openapi_schema:
        return JSONResponse(app.openapi_schema)
    schema = get_openapi(title=app.title, version=app.version, description=app.description, routes=app.routes)
    # Añadir esquema de seguridad Bearer
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Pega aquí el access_token obtenido del endpoint /api/auth/login"
        }
    }
    # Aplicar BearerAuth a todos los endpoints que no sean auth
    for path, methods in schema.get("paths", {}).items():
        for method, details in methods.items():
            if method in ("get", "post", "put", "patch", "delete"):
                tags = details.get("tags", [])
                if "Autenticación" not in tags and "Root" not in tags:
                    details["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return JSONResponse(schema)


@app.get("/docs", include_in_schema=False)
def custom_swagger():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="EcoTrack Pro API - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
def custom_redoc():
    return HTMLResponse("""<!DOCTYPE html><html><head><title>EcoTrack Pro - ReDoc</title>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{margin:0}.loading{display:flex;align-items:center;justify-content:center;height:100vh;font-size:1.2rem;color:#2d7a2d;font-family:sans-serif}</style>
</head><body>
<div id="loading" class="loading">🌱 Cargando documentación...</div>
<div id="redoc-container"></div>
<script>
var s=document.createElement('script');
s.src='https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js';
s.onload=function(){
  document.getElementById('loading').style.display='none';
  Redoc.init('/openapi.json',{theme:{colors:{primary:{main:'#2d7a2d'}}}},document.getElementById('redoc-container'));
};
s.onerror=function(){
  document.getElementById('loading').innerHTML='<div style="text-align:center"><h2>⚠️ Sin conexión</h2><p>Usa <a href="/docs">Swagger</a> en su lugar.</p></div>';
};
document.head.appendChild(s);
</script></body></html>""")
