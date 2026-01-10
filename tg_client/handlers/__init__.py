from .basic import router as basic_router
from .auth import router as auth_router

routers = [auth_router, basic_router]

__all__ = ['routers']