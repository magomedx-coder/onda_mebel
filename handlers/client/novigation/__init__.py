from aiogram import Router

router = Router()

from .furniture_manager import router as furniture_manager_router
router.include_router(furniture_manager_router)

from .novigation_handler import router as navigation_router
router.include_router(navigation_router)