from moddingway_api.routes.mod_routes import router as mod_router
from moddingway_api.routes.user_routes import router as user_router
from moddingway_api.routes.banneduser_routes import router as banneduser_router

__all__ = ["user_router", "mod_router", "banneduser_router"]
