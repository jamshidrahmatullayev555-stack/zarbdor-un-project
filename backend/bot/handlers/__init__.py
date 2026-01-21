from aiogram import Dispatcher
from . import user, orders, admin, catalog


def register_all_handlers(dp: Dispatcher):
    """Register all bot handlers to the dispatcher"""
    # Include routers in order of priority
    # Admin handlers first to catch /admin
    dp.include_router(admin.router)
    # Orders handlers
    dp.include_router(orders.router)
    # Catalog handlers
    dp.include_router(catalog.router)
    # User handlers last (catches general messages)
    dp.include_router(user.router)


__all__ = ['register_all_handlers', 'user', 'orders', 'admin', 'catalog']
