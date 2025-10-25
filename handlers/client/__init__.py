from aiogram import Router

router = Router()

from .commands import router as commands_router
router.include_router(commands_router)

from .novigation import router as furniture_handlers_router
router.include_router(furniture_handlers_router)