from app.routes.auth import router as auth_router
from app.routes.consumptions import router as consumptions_router
from app.routes.dashboard import router as dashboard_router

__all__ = ["auth_router", "consumptions_router", "dashboard_router"]
