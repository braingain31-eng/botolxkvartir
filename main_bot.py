import asyncio
import logging
import signal
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
from handlers import start, search, property, agent, payment, reminders, errors, payment_menu
# Зависимости для парсера
from utils.olx_parser import parse_olx_listing
from database.firebase_db import get_properties

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

# --- Логика парсера (интегрирована сюда) ---
async def run_olx_parser_logic():
    """Логика парсинга, выполняемая по расписанию."""
    try:
        # Проверка времени, чтобы избежать слишком частых запусков (на всякий случай)
        all_properties = get_properties(limit=1)
        if all_properties:
            latest_property = max(all_properties, key=lambda x: x.get('parsed_at', ''))
            last_parsed_str = latest_property.get('parsed_at')
            if last_parsed_str:
                try:
                    last_parsed_time = datetime.fromisoformat(last_parsed_str.replace('Z', '+00:00'))
                    time_since_last_parse = datetime.now(last_parsed_time.tzinfo) - last_parsed_time
                    if time_since_last_parse < timedelta(hours=5.9):
                        logger.info(f"Парсинг был недавно. Пропускаем запуск.")
                        return
                except Exception as e:
                    logger.warning(f"Ошибка проверки времени последнего парсинга: {e}. Продолжаем.")

        logger.info("Выполняем парсинг OLX по расписанию...")
        added = await parse_olx_listing()
        logger.info(f"Парсинг завершён. Добавлено: {added} объектов")

    except Exception as e:
        logger.error(f"Критическая ошибка при выполнении фонового парсинга: {e}", exc_info=True)


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
@app.before_serving
async def startup_logic():
    """Выполняется при запуске приложения один раз."""
    register_bot_handlers()

    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    logger.info(f"Вебхук установлен на {WEBHOOK_URL}")

    # Планирование задачи парсера
    scheduler.add_job(run_olx_parser_logic, 'interval', hours=6, misfire_grace_time=300)
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
    """Корректная остановка по сигналу SIGTERM от Cloud Run."""
    logger.warning("Получен SIGTERM, инициируется корректная остановка...")
    asyncio.run(shutdown_logic())

# Регистрируем обработчик сигнала SIGTERM
signal.signal(signal.SIGTERM, handle_sigterm)

# --- Маршруты вебхуков ---
@app.route(WEBHOOK_PATH, methods=["POST"])
async def handle_webhook():
    """Основная точка входа для вебхуков Telegram."""
    update = types.Update.model_validate(request.json, context={"bot": bot})
    await dp.feed_update(bot, update)
    return "", 200

@app.route("/")
def index():
    """Эндпоинт для проверки работоспособности Cloud Run."""
    return "Бот запущен и готов к работе!", 200

# Блок if __name__ == '__main__' не используется в Cloud Run,
# так как запуск происходит через Gunicorn.
