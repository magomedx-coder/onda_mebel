import re

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext


from database.crud import FurnitureRepository
from keyboards.inline_keyboards import contry_of_origin_kb, kitchen_subcategory_inline_kb
from keyboards.keyboard_creator import make_row_inline_keyboards

router = Router()

FURNITURE_NAMES = {
    'sleep_furniture': '🛌 Мебель для спальни',
    'kitchen_furniture': '🍽️ Мебель кухни',
    'soft_furniture': '🛋️ Диваны и кресла',
    'tables_chairs': '🍽️ Обеденные группы',
    'cabinets_commodes': '🧰 Комоды и тумбы',
    'bed_furniture': '🛏️ Каркасы кроватей',
    'mattresses': '🧴 Матрасы и топперы',
    'wardrobes': '🚪 Шкафы-купе'
}

KITCHEN_SUBCATEGORIES = {
    'straight_kitchen': '📏 Прямая кухня',
    'corner_kitchen': '📐 Угловая кухня'
}

ORIGIN_NAMES = {
    "russian_origin": "🇷🇺 Россия",
    "turkey_origin": "🇹🇷 Турция"
}

TYPES_WITH_ORIGIN = {'sleep_furniture', 'soft_furniture', 'tables_chairs'}

TYPES_WITH_SUBCATEGORIES = {'kitchen_furniture'}

ITEMS_PER_PAGE = 10


def extract_kitchen_type(description: str) -> tuple:
    match = re.search(r'\[(.*?)\]', description)
    if match:
        kitchen_type = match.group(1)
        clean_description = re.sub(r'\[.*?\]\s*', '', description)
        return kitchen_type, clean_description
    return None, description


async def show_furniture_list(message: types.Message, category_name: str, country: str = "🇷🇺 Россия", kitchen_type: str = None, page: int = 0):
    crud = FurnitureRepository()

    # Сохраняем оригинальное имя категории и нормализованное (без ведущих эмодзи/символов)
    original_category_name = category_name
    normalized_category_name = re.sub(r'^[^A-Za-zА-Яа-яЁё]+\s*', '', original_category_name)

    # Определяем, относится ли категория к кухне (по оригинальному или нормализованному названию)
    is_kitchen = bool(re.search(r"кух", original_category_name.lower()) or re.search(r"кух", normalized_category_name.lower()))

    # Для кухонных категорий по умолчанию страна — Россия
    if is_kitchen:
        country = "🇷🇺 Россия"

    # Последовательно пытаемся получить товары по разным вариантам имени категории
    furniture_list = await crud.get_furniture_by_category_and_country(
        category_name=original_category_name,
        country=country
    )

    if not furniture_list:
        furniture_list = await crud.get_furniture_by_category_and_country(
            category_name=normalized_category_name,
            country=country
        )

    # Fallback: если ничего не нашли по стране, пробуем по категории без фильтра страны
    if not furniture_list:
        furniture_list = await crud.get_furniture_by_category(original_category_name)

    if not furniture_list:
        furniture_list = await crud.get_furniture_by_category(normalized_category_name)

    if kitchen_type and furniture_list:
        furniture_list = [
            furniture for furniture in furniture_list
            if f"[{kitchen_type}]" in (furniture.description or "")
        ]

    if not furniture_list:
        await message.answer("📭 По данной категории пока нет доступных товаров.\n\n"
                             "Ассортимент регулярно обновляется — заглядывайте позже.")
        return

    total_items = len(furniture_list)
    start_index = page * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    paginated_furniture = furniture_list[start_index:end_index]

    for furniture in paginated_furniture:
        displayed_kitchen_type = ""
        if is_kitchen:
            kt, clean_description = extract_kitchen_type(furniture.description or "")
            if kt:
                displayed_kitchen_type = f"🍳 <b>Компоновка кухни:</b> {kt}\n"
        else:
            clean_description = furniture.description or ""

        furniture_text = (
            f"🪑 <b>{original_category_name}</b>\n"
            f"{'─' * 30}\n"
            f"{clean_description}\n\n"
            f"{displayed_kitchen_type}"
            f"🌍 <b>Страна производства:</b> {furniture.country_origin}\n"
            f"📅 <b>Дата добавления:</b> {furniture.created_at.strftime('%d.%m.%Y') if furniture.created_at else 'Не указана'}\n"
            f"{'─' * 30}\n\n"
            f"💬 <b>Для заказа этой мебели:</b>\n"
            f"📲 WhatsApp: https://wa.me/+79280157223\n"
            f".telegram: https://t.me/magomedx\n\n"
            f"✨ <b>Подписывайтесь на нас в Instagram</b>\n"
            f"и будьте в курсе новинок и акций:\n"
            f"📸 https://instagram.com/xmagomed_x"
        )

        photos = await crud.get_furniture_photos(furniture.id)
        if photos:
            media_group = [types.InputMediaPhoto(media=photo.file_id) for photo in photos[:10]]
            try:
                await message.answer_media_group(media_group)
            except Exception:
                for photo in photos[:10]:
                    await message.answer_photo(photo.file_id)
        else:
            await message.answer("📷 Фото пока нет")

        await message.answer(furniture_text, disable_web_page_preview=True)

    keyboard_buttons = [
        [types.KeyboardButton(text="🏠 Главное меню")]
    ]

    if end_index < total_items:
        keyboard_buttons.append([types.KeyboardButton(text="🔄 Еще")])

    reply_markup = types.ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True
    )

    if total_items > ITEMS_PER_PAGE:
        page_info = f"📄 Страница {page + 1} из {((total_items - 1) // ITEMS_PER_PAGE) + 1}\n"
    else:
        page_info = ""

    await message.answer(
        f"{page_info}"
        f"Отображено <b>{len(paginated_furniture)}</b> из <b>{total_items}</b> позиций в этой категории",
        reply_markup=reply_markup
    )


@router.callback_query(F.data.in_(FURNITURE_NAMES.keys()))
async def furniture_callback(callback_query: types.CallbackQuery, state: FSMContext):
    furniture_type = callback_query.data
    await state.update_data(type_furniture=furniture_type)
    await state.update_data(current_page=0)  # Тут сброс пагинации

    if furniture_type in TYPES_WITH_SUBCATEGORIES:
        await callback_query.message.edit_text(
            "Выберите тип кухонной мебели:",
            reply_markup=make_row_inline_keyboards(kitchen_subcategory_inline_kb)
        )

    elif furniture_type in TYPES_WITH_ORIGIN:
        await callback_query.message.edit_text(
            "Отлично! Теперь выберите страну производства:",
            reply_markup=make_row_inline_keyboards(contry_of_origin_kb)
        )

    else:
        category_name = FURNITURE_NAMES.get(furniture_type, 'Спальная мебель')
        await show_furniture_list(callback_query.message, category_name)

    await callback_query.answer()


@router.callback_query(F.data.in_(KITCHEN_SUBCATEGORIES.keys()))
async def kitchen_subcategory_callback(callback_query: types.CallbackQuery, state: FSMContext):
    kitchen_type_key = callback_query.data
    kitchen_type = KITCHEN_SUBCATEGORIES.get(kitchen_type_key, 'Кухня')

    await state.update_data(kitchen_subcategory=kitchen_type_key)
    await state.update_data(selected_kitchen_type=kitchen_type)
    await state.update_data(current_page=0)  # Тут сброс пагинации

    await show_furniture_list(
        callback_query.message,
        "🍳 Кухонная мебель",
        "🇷🇺 Россия",
        kitchen_type
    )

    await callback_query.answer()


@router.callback_query(F.data.in_(ORIGIN_NAMES.keys()))
async def origin_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    furniture_type = user_data.get('type_furniture', 'sleep_furniture')
    origin_type = callback_query.data

    await state.update_data(origin_type=origin_type)
    await state.update_data(current_page=0)  # Сброс пагинации

    category_name = FURNITURE_NAMES.get(furniture_type, 'Спальная мебель')
    origin_name = ORIGIN_NAMES.get(origin_type, '🇷🇺 Россия')
    kitchen_type = user_data.get('selected_kitchen_type')

    await show_furniture_list(callback_query.message, category_name, origin_name, kitchen_type)

    await callback_query.answer()


@router.message(F.text == "🔄 Еще")
async def more_furniture_handler(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    # Если пользователь выбрал динамическую категорию, используем сохраненное имя
    selected_category_name = user_data.get('selected_category_name')
    if selected_category_name:
        category_name = selected_category_name
    else:
        furniture_type = user_data.get('type_furniture', 'sleep_furniture')
        category_name = FURNITURE_NAMES.get(furniture_type, 'Спальная мебель')

    origin_type = user_data.get('origin_type')
    origin_name = ORIGIN_NAMES.get(origin_type, '🇷🇺 Россия') if origin_type else "🇷🇺 Россия"
    kitchen_type = user_data.get('selected_kitchen_type')
    current_page = user_data.get('current_page', 0)

    new_page = current_page + 1
    await state.update_data(current_page=new_page)

    await show_furniture_list(message, category_name, origin_name, kitchen_type, new_page)


@router.callback_query(F.data.startswith("open_category_"))
async def open_dynamic_category(callback_query: types.CallbackQuery, state: FSMContext):
    # Извлекаем имя категории из callback_data
    category_full = callback_query.data[len("open_category_"):]
    category_name = (category_full or "").strip()

    # Сохраняем состояние и сбрасываем пагинацию
    await state.update_data(type_furniture="dynamic_category")
    await state.update_data(selected_category_name=category_name)
    await state.update_data(current_page=0)

    # Показываем список мебели для выбранной категории (со встроенной нормализацией)
    await show_furniture_list(callback_query.message, category_name)

    await callback_query.answer()