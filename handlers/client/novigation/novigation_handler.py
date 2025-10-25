from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from keyboards.inline_keyboards import start_kb
from keyboards.keyboard_creator import make_row_inline_keyboards

router = Router()


@router.callback_query(F.data == "back_to_main")
async def back_to_main_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()

    welcome_text = (
        "🏠 <b>Главное меню</b>\n\n"
        "👋 Добро пожаловать в наш мебельный магазин!\n\n"
        ".catalog мебели разделен на удобные категории.\n"
        "Выберите интересующую вас категорию ниже:\n\n"
        "🛏️ <b>Спальная мебель</b> - кровати, матрасы\n"
        "🍳 <b>Кухонная мебель</b> - гарнитуры, столы\n"
        "🛋️ <b>Мягкая мебель</b> - диваны, кресла\n"
        "📚 <b>Столы и стулья</b> - обеденные группы\n"
        "📺 <b>Тумбы и комоды</b> - для гостиной\n"
        "🚪 <b>Шкафы</b> - для одежды и хранения\n\n"
        "ℹ️ <b>О компании / Контакты</b> - информация\n"
        "🤝 <b>Сотрудничество</b> - для оптовиков\n\n"
        "📌 <i>Используйте кнопки ниже для навигации</i>"
    )

    await callback_query.message.edit_text(
        welcome_text,
        reply_markup=make_row_inline_keyboards(start_kb)
    )
    await callback_query.answer()