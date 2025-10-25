from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from keyboards.inline_keyboards import start_kb
from keyboards.keyboard_creator import make_row_inline_keyboards

router = Router()


@router.callback_query(F.data == "back_to_main")
async def back_to_main_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()

    welcome_text = (
        "🏠 <b>Домашний экран</b>\n\n"
        "Вы находитесь в каталоге мебели.\n"
        "Выберите нужную категорию ниже, чтобы продолжить.\n\n"
        "Навигация осуществляется кнопками под сообщением."
    )

    await callback_query.message.edit_text(
        welcome_text,
        reply_markup=make_row_inline_keyboards(start_kb)
    )
    await callback_query.answer()