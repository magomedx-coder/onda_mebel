import logging
from aiogram import F, Router, types

from keyboards.inline_keyboards import admin_kb, start_kb
from keyboards.keyboard_creator import make_row_inline_keyboards
from config import ADMIN_USER_IDS

router = Router()


@router.callback_query(F.data == 'settings_bot')
async def settings_bot(callback_query: types.CallbackQuery):
    # Защита: только админы могут открыть админ-панель
    if callback_query.from_user.id not in ADMIN_USER_IDS:
        await callback_query.answer("Нет доступа", show_alert=True)
        return

    await callback_query.answer("▶️")
    try:

        admin_text = (
            "🛠️ <b>Панель администратора</b>\n\n"
            f"Пользователь: <b>{callback_query.from_user.full_name}</b> (<code>{callback_query.from_user.id}</code>)\n\n"
            "Выберите раздел для управления магазином:"
        )

        if callback_query.message:
            try:
                await callback_query.message.edit_text(
                    text=admin_text,
                    reply_markup=make_row_inline_keyboards(admin_kb),
                )

            except Exception:
                await callback_query.message.answer(
                    text=admin_text,
                    reply_markup=make_row_inline_keyboards(admin_kb),
                )
        else:
            await callback_query.message.answer(
                text=admin_text,
                reply_markup=make_row_inline_keyboards(admin_kb),
            )

    except Exception as e:
        logging.exception("Ошибка в settings_bot callback: %s", e)
        await callback_query.message.answer("❌ Произошла ошибка при открытии админ-панели.")


@router.callback_query(F.data == 'admin_back_to_main')
async def admin_back_to_main(callback_query: types.CallbackQuery):
    await callback_query.answer("◀️")

    welcome_text = (
        "🏠 <b>Стартовый экран</b>\n\n"
        "Подберите мебель под ваш стиль и задачи.\n"
        "Откройте нужный раздел и изучайте модели.\n\n"
        "Начнем? 👇"
    )

    # Кнопка настроек показываем только админам
    if callback_query.from_user.id in ADMIN_USER_IDS:
        keyboard = start_kb + [("⚙️ Управление ботом", 'settings_bot')]
    else:
        keyboard = start_kb

    await callback_query.message.edit_text(text=welcome_text, reply_markup=make_row_inline_keyboards(keyboard))