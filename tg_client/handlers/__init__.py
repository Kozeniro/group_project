from .basic import router as basic_router
from .auth import router as auth_router
from .main_test import router as test_router

routers = [auth_router, test_router, basic_router]

__all__ = ['routers']