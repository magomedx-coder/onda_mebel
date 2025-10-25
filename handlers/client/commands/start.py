import logging

from aiogram import Router, types, filters, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError

from keyboards.inline_keyboards import start_kb
from keyboards.keyboard_creator import make_row_inline_keyboards

from database.crud import UserCrud
from config import ADMIN_USER_IDS

router = Router()


@router.message(filters.Command("start"))
@router.message(F.text == "🏠 Главное меню")
async def start(message: types.Message, state: FSMContext):
    await state.clear()

    welcome_text = (
        "🌟 <b>Добро пожаловать в наш мебельный бот!</b> 🌟\n\n"
        "🛋️ Здесь вы найдете стильную и качественную мебель для любого интерьера.\n\n"
        "📂 <b>Наш каталог включает:</b>\n"
        "• Спальни и матрасы\n"
        "• Кухонные гарнитуры\n"
        "• Мягкую мебель\n"
        "• Столы и стулья\n"
        "• Тумбы и комоды\n"
        "• Шкафы-купе и гардеробные\n\n"
        "🛒 <b>Как сделать заказ:</b>\n"
        "1. Выберите категорию мебели\n"
        "2. Просмотрите модели\n"
        "3. Свяжитесь с нами для заказа\n\n"
        "💬 <i>Для оформления заказа потребуется ваше имя и номер телефона</i>\n"
        "🔄 <i>В любой момент можно вернуться в главное меню</i>\n\n"
        "👇 <b>Выберите категорию из меню ниже:</b>"
    )

    keyboard = start_kb
    telegram_id = message.from_user.id
    crud = UserCrud()

    try:
        # Определяем, должен ли пользователь быть админом по списку ADMIN_USER_IDS
        should_be_admin = telegram_id in ADMIN_USER_IDS

        # Пытаемся добавить пользователя. Если существует, метод вернет None.
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

    if user and user.is_admin:
        keyboard = start_kb + [("⚙️Настройки бота", 'settings_bot')]

    await message.answer(
        text=welcome_text,
        reply_markup=make_row_inline_keyboards(keyboard))