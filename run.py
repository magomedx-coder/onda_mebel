import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import DeleteWebhook
from aiogram.types import BotCommandScopeAllPrivateChats

from handlers import router
from keyboards.keyboard_manager import commands
from config import TOKEN
from database.engine import async_engine, Base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)


async def main():
   
    logging.info("Инициализация базы данных...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("База данных инициализирована успешно")
    
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

   
    dp.include_router(router)

   
    await bot(DeleteWebhook(drop_pending_updates=True))

    
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats())

    # Запуск бота
    print("✅ Бот запущен")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())
    
#ку