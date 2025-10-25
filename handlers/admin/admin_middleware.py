from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from database.crud import CrudCategory
from keyboards.inline_keyboards import build_cancel_kb
from keyboards.keyboard_creator import make_row_inline_keyboards
from states.states import NewCategoryStates

router = Router()


@router.callback_query(F.data == 'new_category_furniture')
async def new_category_furniture_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.clear()

    prompt = (
        "🆕 <b>Создание категории</b>\n\n"
        "Введите название категории.\n\n"
        "🔹 Подсказка: добавьте эмодзи в начале — меню станет нагляднее.\n\n"
        "Примеры:\n"
        "<code>🛏️ Спальная мебель</code>\n"
        "<code>🍳 Кухонная мебель</code>\n"
        "<code>🛋️ Мягкая мебель</code>\n"
        "<code>📚 Столы и стулья</code>\n"
        "<code>📺 Тумбы и комоды</code>\n"
        "<code>🛏️ Кровати</code>\n"
        "<code>🛏️️ Матрасы</code>\n"
        "<code>🚪 Шкафы</code>\n"
        "Отправьте название или нажмите «Отменить»."
    )

    await callback_query.message.answer(
        text=prompt,
        reply_markup=make_row_inline_keyboards(build_cancel_kb),
    )

    await state.set_state(NewCategoryStates.name_category)


@router.message(NewCategoryStates.name_category)
async def name_category_furniture(message: types.Message, state: FSMContext):
    name_category = (message.text or "").strip()

    if not name_category:
        await message.answer("⚠️ Название не может быть пустым. Введите корректное название категории.")
        return

    crud = CrudCategory()
    exists = await crud.check_category_by_name(name_category)
    if exists:
        await message.answer("⚠️ Категория с таким именем уже существует.")
        return

    await state.update_data(name_category=name_category)

    prompt = (
        f"✅ Название сохранено: <b>{name_category}</b>\n\n"
        "Добавьте <b>краткое описание</b> — одна-две фразы.\n"
        "Описание помогает быстрее понять содержание категории.\n\n"
        "Чтобы отменить — нажмите «Отменить»."
    )

    await message.answer(text=prompt, reply_markup=make_row_inline_keyboards(build_cancel_kb))
    await state.set_state(NewCategoryStates.description_category)


@router.message(NewCategoryStates.description_category)
async def description_category_furniture(message: types.Message, state: FSMContext):
    description_category = (message.text or "").strip()

    if not description_category:
        await message.answer("⚠️ Описание не может быть пустым. Введите описание категории.")
        return

    await state.update_data(description_category=description_category)

    data = await state.get_data()
    name = data.get("name_category", "<без названия>")
    description = description_category

    preview = (
        "🎯 <b>Предпросмотр категории</b>\n\n"
        f"{name}\n"
        f"<i>{description}</i>\n\n"
        "Проверьте данные. Для сохранения нажмите «Сохранить»,\n"
        "или используйте «Отменить», чтобы прервать создание."
    )

    keyboard_for_preview = build_cancel_kb + [("✅ Сохранить", "save_category")]

    await message.answer(text=preview, reply_markup=make_row_inline_keyboards(keyboard_for_preview))


@router.callback_query(F.data == 'save_category')
async def save_category(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    data = await state.get_data()
    name_category = data.get("name_category")
    description_category = data.get("description_category")

    if not name_category or not description_category:
        await callback_query.message.answer("❗ Данные неполные — начните заново.")
        await state.clear()
        return

    crud = CrudCategory()
    add_category = await crud.create_category(name=name_category, description=description_category)

    if add_category:
        await callback_query.answer(text='🎉 Категория сохранена', show_alert=True)
        try:
            await callback_query.message.edit_text("✅ Категория добавлена")
        except Exception:
            await callback_query.message.answer("✅ Категория добавлена")
    else:
        await callback_query.message.answer("❌ Ошибка при сохранении. Обратитесь к администратору.")

    await state.clear()


@router.callback_query(F.data == "cancel_category")
async def cancel_category_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer("Операция отменена ✖️", show_alert=True)
    await state.clear()

    try:
        await callback_query.message.answer("Создание категории отменено.", reply_markup=None)
    except Exception as e:
        try:
            await callback_query.message.answer(f"Не удалось отправить сообщение после отмены: {e}")
        except Exception:
            pass