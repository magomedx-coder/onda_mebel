from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from database.crud import CategoryRepository, FurnitureRepository
from keyboards.inline_keyboards import country_kb, kitchen_subcategory_kb, more_added_furniture
from keyboards.keyboard_creator import make_row_keyboards, make_row_inline_keyboards
from states.states import NewFurnitureStates
import re

router = Router()


@router.callback_query(F.data == 'new_furniture')
async def new_furniture_function(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.answer()

    text = (
        "🪄 <b>Добавление новой мебели</b>\n\n"
        "📝 <b>Шаг 1 из 5:</b> Описание мебели\n\n"
        "Пожалуйста, введите <b>подробное описание</b> мебели:\n"
        "• Материалы и отделка\n"
        "• Габариты (Д×Ш×В)\n"
        "• Особенности конструкции\n"
        "• Стиль и назначение\n\n"
        "<i>Пример:</i>\n"
        "<code>Элегантный кожаный диван \"Комфорт\" с мягким наполнением, \n"
        "размеры 200×90×85 см, каркас из березовой фанеры, \n"
        "подушки сиденья на пружинном блоке, цвет черный.</code>"
    )

    await callback_query.message.answer(text)
    await state.set_state(NewFurnitureStates.description)


@router.message(NewFurnitureStates.description)
async def get_description_new_furniture(message: types.Message, state: FSMContext):
    description_furniture = (message.text or '').strip()
    if not description_furniture:
        await message.answer("⚠️ <b>Ошибка ввода</b>\n\n"
                             "Описание не может быть пустым. Пожалуйста, введите описание мебели.")
        return

    await state.update_data(description_new_furniture=description_furniture)

    crud = CategoryRepository()
    get_categories = await crud.get_all_categories()
    categories = [category_name.name for category_name in get_categories]

    if not categories:
        await message.answer("📭 <b>Категории не найдены</b>\n\n"
                             "В базе пока нет разделов мебели.\n"
                             "Сначала создайте хотя бы одну категорию в админ-панели.")
        await state.clear()
        return

    text = (
        "✅ <b>Описание принято</b>\n\n"
        "📋 <b>Шаг 2 из 5:</b> Выберите раздел\n\n"
        "Укажите, к какому <b>разделу</b> относится товар из списка ниже 👇"
    )

    await message.answer(text, reply_markup=make_row_keyboards(categories))
    await state.set_state(NewFurnitureStates.category)


@router.message(NewFurnitureStates.category)
async def get_category(message: types.Message, state: FSMContext):
    category_name = (message.text or '').strip()

    if not category_name:
        await message.answer("⚠️ <b>Ошибка выбора</b>\n\n"
                             "Пожалуйста, выберите категорию из предложенного списка.")
        return

    await state.update_data(category_name=category_name)

    if "кухонная" in category_name.lower():
        text = (
            f"🗂 <b>Категория выбрана:</b> {category_name}\n\n"
            f"📋 <b>Шаг 3 из 5:</b> Тип кухни\n\n"
            f"Теперь выберите <b>тип кухни</b> из списка ниже:"
        )

        await message.answer(text, reply_markup=make_row_keyboards(kitchen_subcategory_kb))
        await state.set_state(NewFurnitureStates.kitchen_type)
    else:
        text = (
            f"🗂 <b>Категория выбрана:</b> {category_name}\n\n"
            f"📋 <b>Шаг 3 из 5:</b> Страна производства\n\n"
            f"Теперь укажите <b>страну происхождения</b> мебели 🌍\n"
            f"Выберите из списка ниже:"
        )

        await message.answer(text, reply_markup=make_row_keyboards(country_kb))
        await state.set_state(NewFurnitureStates.country)


@router.message(NewFurnitureStates.kitchen_type)
async def get_kitchen_type(message: types.Message, state: FSMContext):
    kitchen_type = (message.text or '').strip()

    if not kitchen_type:
        await message.answer("⚠️ <b>Ошибка выбора</b>\n\n"
                             "Пожалуйста, выберите тип кухни из предложенного списка.")
        return

    await state.update_data(kitchen_type=kitchen_type)
    await state.update_data(country_name="🇷🇺 Россия")

    text = (
        f"🍳 <b>Тип кухни выбран:</b> {kitchen_type}\n\n"
        f"🌍 <b>Страна производства:</b> 🇷🇺 Россия (по умолчанию)\n\n"
        f"📋 <b>Шаг 4 из 5:</b> Фотографии\n\n"
        f"Теперь отправьте <b>фотографии</b> мебели 📸\n"
        f"• Вы можете отправить несколько фотографий (не более 10)\n"
        f"• Рекомендуется отправлять фото с разных ракурсов\n"
        f"• Каждое фото будет добавлено отдельно\n\n"
        f"Когда закончите, нажмите кнопку <b>«Завершить добавление»</b> ниже."
    )

    finish_button = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="✅ Завершить добавление")]],
        resize_keyboard=True
    )

    await message.answer(text, reply_markup=finish_button)
    await state.set_state(NewFurnitureStates.photos)
    await state.update_data(photos=[])


@router.message(NewFurnitureStates.country)
async def get_country(message: types.Message, state: FSMContext):
    country_name = (message.text or '').strip()

    if not country_name:
        await message.answer("⚠️ <b>Ошибка выбора</b>\n\n"
                             "Пожалуйста, выберите страну из предложенного списка.")
        return

    await state.update_data(country_name=country_name)

    text = (
        f"🌍 <b>Страна выбрана:</b> {country_name}\n\n"
        f"📋 <b>Шаг 4 из 5:</b> Фотографии\n\n"
        f"Теперь отправьте <b>фотографии</b> мебели 📸\n"
        f"• Вы можете отправить несколько фотографий (не более 10)\n"
        f"• Рекомендуется отправлять фото с разных ракурсов\n"
        f"• Каждое фото будет добавлено отдельно\n\n"
        f"Когда закончите, нажмите кнопку <b>«Завершить добавление»</b> ниже."
    )

    # Создаем кнопку для завершения добавления фотографий
    finish_button = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="✅ Завершить добавление")]],
        resize_keyboard=True
    )

    await message.answer(text, reply_markup=finish_button)
    await state.set_state(NewFurnitureStates.photos)
    await state.update_data(photos=[])


@router.message(NewFurnitureStates.photos)
async def get_photos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])

    if message.text == "✅ Завершить добавление":
        if not photos:
            await message.answer("⚠️ <b>Нет фотографий</b>\n\n"
                                 "Пожалуйста, отправьте хотя бы одну фотографию мебели.")
            return

        description = data.get("description_new_furniture", 'Нет описания')
        category_name = data.get("category_name", "Без категории")
        country_name = data.get("country_name", "Не указана")
        kitchen_type = data.get("kitchen_type")

        if kitchen_type and "кухонная" in category_name.lower():
            description = f"[{kitchen_type}] {description}"

        crud = FurnitureRepository()
        new_furniture = await crud.create_furniture(
            description=description,
            category=category_name,
            country=country_name
        )

        if not new_furniture:
            await message.answer("❌ <b>Ошибка сохранения</b>\n\n"
                                 "Произошла ошибка при сохранении мебели в базу данных.\n"
                                 "Обратитесь к администратору или попробуйте позже.")
            return

        photo_added = await crud.add_photos_to_furniture(new_furniture.id, photos)

        if not photo_added:
            await message.answer("ℹ️ Товар создан, но фото не прикреплены.\n"
                                 "Вы можете добавить изображения позже в разделе редактирования.")
        else:
            await message.answer("✅ <b>Фото сохранены</b>\n\n"
                                 "Все изображения успешно добавлены.")

        text = (
            "🎉 <b>Товар успешно добавлен!</b>\n\n"
            f"📊 <b>Детали добавления:</b>\n"
            f"• Раздел: {category_name}\n"
            f"• Компоновка: {kitchen_type or 'Не указана'}\n"
            f"• Страна происхождения: {country_name}\n"
            f"• Фото: {len(photos)}\n\n"
            f"📝 <b>Описание:</b>\n{description}\n\n"
            f"Спасибо! Запись создана. ✅"
        )

        await message.answer(text, reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
        return

    if message.photo:
        photo_file_id = message.photo[-1].file_id
        photos.append(photo_file_id)
        await state.update_data(photos=photos)

        await message.answer(f"✅ Фото добавлено ({len(photos)}/10)\n\n"
                             f"📸 Отправьте еще фотографии или нажмите «Завершить добавление».")

        if len(photos) >= 10:
            await message.answer("Вы достигли максимального количества фотографий (10).\n"
                                 "Нажмите «Завершить добавление» для сохранения мебели.")
    else:
        await message.answer("⚠️ <b>Неподдерживаемый формат</b>\n\n"
                             "Пожалуйста, отправьте фотографию или нажмите кнопку «Завершить добавление».")


@router.callback_query(F.data == 'remove_furniture')
async def remove_furniture_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.clear()

    
    categories_repo = CategoryRepository()
    all_categories = await categories_repo.get_all_categories()
    if not all_categories:
        await callback_query.message.answer("📭 В каталоге нет категорий для удаления товаров.")
        return

    items = [(cat.name, f"admin_delete_category_{cat.name}") for cat in all_categories]
    
    items.append(("⬅️ В меню", "admin_back_to_main"))

    text = (
        "🗑️ <b>Удаление товаров</b>\n\n"
        "Выберите категорию, в которой хотите удалить товар:" 
    )

    await callback_query.message.answer(text, reply_markup=make_row_inline_keyboards(items))


@router.callback_query(F.data.startswith('admin_delete_category_'))
async def choose_category_for_delete_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()

    category_name = callback_query.data[len('admin_delete_category_'):]
    await state.update_data(delete_category_name=category_name)

    repo = FurnitureRepository()
    furniture_items = await repo.get_furniture_by_category(category_name)

    
    if not furniture_items:
        normalized_name = re.sub(r'^[^A-Za-zА-Яа-яЁё]+\s*', '', category_name)
        if normalized_name != category_name:
            furniture_items = await repo.get_furniture_by_category(normalized_name)

    if not furniture_items:
        await callback_query.message.answer(
            f"📭 В категории <b>{category_name}</b> нет товаров для удаления."
        )
        return

    
    delete_buttons = [
        (f"🗑️ Удалить #{item.id}", f"admin_delete_furniture_{item.id}")
        for item in furniture_items
    ]
    
    delete_buttons.append(("◀️ К категориям", "remove_furniture"))

    await callback_query.message.answer(
        (
            f"📋 Найдено товаров в категории <b>{category_name}</b>: <b>{len(furniture_items)}</b>\n\n"
            "Выберите товар, который нужно удалить:"
        ),
        reply_markup=make_row_inline_keyboards(delete_buttons)
    )


@router.callback_query(F.data.startswith('admin_delete_furniture_'))
async def delete_furniture_item_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()

    item_id_str = callback_query.data[len('admin_delete_furniture_'):]
    try:
        item_id = int(item_id_str)
    except ValueError:
        await callback_query.message.answer("❌ Неверный идентификатор товара для удаления.")
        return

    repo = FurnitureRepository()
    deleted = await repo.delete_furniture(item_id)

    if deleted:
        await callback_query.message.answer(
            f"✅ Товар с ID <b>{item_id}</b> успешно удален."
        )
    else:
        await callback_query.message.answer(
            f"❌ Не удалось удалить товар с ID <b>{item_id}</b>. Возможно, он уже удален."
        )

    
    actions = [
        ("🔄 Удалить еще", "remove_furniture"),
        ("⬅️ В меню", "admin_back_to_main")
    ]
    await callback_query.message.answer(
        "Выберите дальнейшее действие:",
        reply_markup=make_row_inline_keyboards(actions)
    )