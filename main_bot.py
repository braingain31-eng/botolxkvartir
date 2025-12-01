import asyncio
import logging
import signal
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
from handlers import start, search, property, agent, payment, reminders, errors, payment_menu
# Импортируем логику парсера
from main_parser import run_olx_parser_logic

# --- Базовая настройка ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
bot = Bot(token=config.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
scheduler = AsyncIOScheduler()

WEBHOOK_PATH = f"/webhook/{config.TELEGRAM_BOT_TOKEN}"
WEBHOOK_URL = config.WEBHOOK_BASE_URL + WEBHOOK_PATH

# --- Регистрация обработчиков ---
def register_bot_handlers():
    """Регистрирует все обработчики сообщений для бота."""
    start.register_handlers(dp)
    search.register_handlers(dp)
    property.register_handlers(dp)
    reminders.register_handlers(dp)
    agent.register_handlers(dp)
    payment.register_handlers(dp)
    payment_menu.register_handlers_payment_menu(dp)
    errors.register_handlers(dp)
    logger.info("Обработчики бота зарегистрированы.")

# --- Жизненный цикл приложения (запуск и остановка) ---
async def startup_logic():
    """Выполняется при запуске приложения."""
    register_bot_handlers()

    # Установка вебхука
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    logger.info(f"Вебхук установлен на {WEBHOOK_URL}")

    # Планирование задачи парсера
    scheduler.add_job(run_olx_parser_logic, 'interval', hours=6, misfire_grace_time=300) # 5 минут запаса
    scheduler.start()
    logger.info("Планировщик запущен. Парсер OLX будет запускаться каждые 6 часов.")

async def shutdown_logic():
    """Выполняется при остановке приложения."""
    logger.info("Начинается остановка...")
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Планировщик остановлен.")
    await bot.delete_webhook()
    logger.info("Вебхук удален.")

def handle_sigterm(*args):
    """Корректная остановка по сигналу SIGTERM."""
    logger.warning("Получен SIGTERM, инициируется корректная остановка...")
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(shutdown_logic())
    except RuntimeError:
        logger.info("Нет запущенного цикла asyncio, запускаю остановку синхронно.")
        asyncio.run(shutdown_logic())

# --- Маршруты вебхуков ---
@app.route(WEBHOOK_PATH, methods=["POST"])
async def handle_webhook():
    """Основная точка входа для вебхуков Telegram."""
    update = types.Update.model_validate(request.json, context={"bot": bot})
    await dp.feed_update(bot, update)
    return jsonify({}), 200

@app.route("/")
def index():
    """Эндпоинт для проверки работоспособности Cloud Run."""
    return "Бот запущен!", 200

# --- Основное выполнение ---
# Этот блок выполняется при загрузке модуля.
# С `gunicorn --preload` он запускается один раз в главном процессе.
try:
    logger.info("Запуск приложения...")
    # Регистрация обработчика сигнала для корректной остановки
    signal.signal(signal.SIGTERM, handle_sigterm)
    # Запуск логики старта
    asyncio.run(startup_logic())
    logger.info("Приложение успешно запущено.")
except Exception as e:
    logger.critical(f"КРИТИЧЕСКАЯ ОШИБКА: Ошибка во время запуска: {e}", exc_info=True)

# Блок if __name__ == '__main__' предназначен для локальной разработки
# и не будет использоваться в окружении Cloud Run.
if __name__ == '__main__':
    # Эта часть не предназначена для production.
    # Для локального тестирования используйте Gunicorn:
    # gunicorn --bind 127.0.0.1:8080 --workers 1 -k uvicorn.workers.UvicornWorker main_bot:app
    # Затем используйте ngrok для проброса порта 8080 и установки вебхука.
    pass
