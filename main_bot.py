import asyncio
import logging
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config
from handlers import start, search, property, agent, payment, reminders, errors, payment_menu

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация Flask приложения
app = Flask(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=config.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Секретный путь для вебхука, чтобы его не могли вызвать посторонние
WEBHOOK_PATH = f"/webhook/{config.TELEGRAM_BOT_TOKEN}"
WEBHOOK_URL = config.WEBHOOK_BASE_URL + WEBHOOK_PATH

async def setup_bot_handlers():
    """Регистрирует все обработчики сообщений для бота."""
    start.register_handlers(dp)
    search.register_handlers(dp)
    property.register_handlers(dp)
    reminders.register_handlers(dp)
    agent.register_handlers(dp)
    payment.register_handlers(dp)
    payment_menu.register_handlers_payment_menu(dp)
    errors.register_handlers(dp)

async def on_startup():
    """Выполняется при старте: установка вебхука."""
    logger.info("Регистрация обработчиков...")
    await setup_bot_handlers()
    logger.info(f"Установка вебхука на URL: {WEBHOOK_URL}")
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

async def on_shutdown():
    """Выполняется при остановке: удаление вебхука."""
    logger.info("Удаление вебхука...")
    await bot.delete_webhook()

@app.route(WEBHOOK_PATH, methods=["POST"])
async def handle_webhook():
    """
    Основная точка входа для вебхуков от Telegram.
    """
    update_data = request.json
    update = types.Update.model_validate(update_data, context={"bot": bot})
    await dp.feed_update(bot, update)
    return jsonify({}), 200

@app.route("/")
def index():
    # Просто для проверки, что сервер работает
    return "Bot is running!", 200

async def main():
    # Этот асинхронный main нужен для локального запуска
    # В облачной среде он не используется напрямую
    await on_startup()
    try:
        # В режиме вебхуков основной цикл не нужен
        # Приложение Flask будет обрабатывать запросы
        logger.info("Бот запущен в режиме вебхука.")
        # Здесь можно было бы запустить сервер, но мы делаем это через Gunicorn
    finally:
        await on_shutdown()


if __name__ == '__main__':
    # Для локального тестирования
    # Важно: этот блок не будет выполняться на Firebase/Cloud Run
    # Для запуска используется WSGI сервер, например, gunicorn

    # Создаем и запускаем асинхронный event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(on_startup())

    # Запуск Flask-приложения
    # В реальном развертывании это будет делать gunicorn, например:
    # gunicorn -w 4 -k uvicorn.workers.UvicornWorker main_bot:app
    app.run(debug=True, port=8080)

    # Обработка завершения
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(on_shutdown())
        loop.close()
