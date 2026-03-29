from .basic import router as basic_router
from .auth import router as auth_router
from .main_test import router as test_router
from .admin import router as admin_router
from .student import router as student_router


routers = [auth_router, test_router, admin_router, student_router, basic_router]

__all__ = ['routers']