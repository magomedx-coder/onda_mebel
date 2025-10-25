import logging

from aiogram import Router, types, filters, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError

# from keyboards.inline_keyboards import start_kb
from keyboards.keyboard_creator import make_row_inline_keyboards

from database.crud import UserCrud, CategoryRepository
from config import ADMIN_USER_IDS

router = Router()


@router.message(filters.Command("start"))
@router.message(F.text == "🏠 Главное меню")
async def start(message: types.Message, state: FSMContext):
    await state.clear()

    intro_text = (
        "✨ <b>Рады видеть вас!</b> ✨\n\n"
        "Здесь вы найдете мебель под любые задачи и стили — от базовых решений до премиум-моделей.\n\n"
        "<b>Разделы каталога:</b>\n"
        "• Спальные комплекты\n"
        "• Кухни разных форм\n"
        "• Диваны и кресла\n"
        "• Обеденные группы\n"
        "• Комоды и тумбы\n"
        "• Шкафы-купе и гардеробные\n\n"
        "<b>Как оформить заказ:</b>\n"
        "1) Выберите раздел\n"
        "2) Откройте модели\n"
        "3) Напишите нам\n\n"
        "ℹ️ Для оформления потребуется имя и номер телефона.\n"
        "↩️ Вернуться в меню можно в любой момент.\n\n"
        "Выберите раздел ниже 👇"
    )

    telegram_id = message.from_user.id
    crud = UserCrud()

    try:
       
        should_be_admin = telegram_id in ADMIN_USER_IDS

        
        added_user = await crud.add_user(
            telegram_id=telegram_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            is_admin=should_be_admin,
        )
        if added_user:
            logging.info("✅ Пользователь %s успешно зарегистрирован. Admin=%s", telegram_id, should_be_admin)
        else:
            # Пользователь уже есть — синхронизируем admin-статус с конфигом
            await crud.set_admin_status(telegram_id, should_be_admin)
            logging.info("👤 Пользователь %s уже существует. Admin статус синхронизирован: %s", telegram_id, should_be_admin)

    except IntegrityError as ie:
        logging.exception("❌ IntegrityError при добавлении пользователя %s: %s", telegram_id, ie)

    except Exception as e:
        logging.exception("❌ Ошибка при добавлении пользователя %s: %s", telegram_id, e)

    user = await crud.get_user_by_telegram_id(message.from_user.id)

   
    categories_repo = CategoryRepository()
    categories = await categories_repo.get_all_categories()
    keyboard_items = [(cat.name, f"open_category_{cat.id}") for cat in categories]
    keyboard_items = [(cat.name, f"open_category_{cat.name}") for cat in categories]

    
    keyboard_items += [
        ("ℹ️ О нас и контакты", "about_company"),
        ("🤝 Оптовикам", "cooperation_company"),
    ]

    
    if user and user.is_admin:
        keyboard_items += [("⚙️ Управление ботом", "settings_bot")]

    await message.answer(
        text=intro_text,
        reply_markup=make_row_inline_keyboards(keyboard_items)
    )