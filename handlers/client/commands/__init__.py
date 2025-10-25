from aiogram import Router

router = Router()


from .profile import router as profiles_router
router.include_router(profiles_router)

from .start import router as starts_router
router.include_router(starts_router)

from .info_company import router as info_company_router
router.include_router(info_company_router)
