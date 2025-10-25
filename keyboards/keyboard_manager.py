from aiogram.types import BotCommand

# 🎯 Основные команды бота
start_command = BotCommand(
    command='start',
    description='🚀 Запустить бота / перейти в главное меню'
)

profile_command = BotCommand(
    command='profile',
    description='🧾 Профиль пользователя и статистика'
)

# 📋 Список всех команд
commands = [
    start_command,
    profile_command,
]