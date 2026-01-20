from aiogram import Router
from . import user, orders, admin

def setup_handlers() -> Router:
    """Setup all handlers"""
    router = Router()
    
    # Include sub-routers
    router.include_router(admin.router)  # Admin first to catch /admin
    router.include_router(orders.router)
    router.include_router(user.router)
    
    return router

__all__ = ['setup_handlers', 'user', 'orders', 'admin']
