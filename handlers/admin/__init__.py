from aiogram import Router


router = Router()

from .admin_panel import router as main_admin_router
router.include_router(main_admin_router)

from .admin_cooperation import router as cooperation
router.include_router(cooperation)

from .admin_middleware import router as admin_middleware
router.include_router(admin_middleware)

from .manage_order import router as manage_order
router.include_router(manage_order)

from .manage_products import router as manage_products
router.include_router(manage_products)