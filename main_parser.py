from flask import Flask, request
import asyncio
import logging
from utils.olx_parser import parse_olx_listing
from database.firebase_db import get_properties
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

async def run_olx_parser_logic():
    """Логика парсинга, адаптированная для запуска в облачной функции."""
    try:
        # Проверка времени последнего парсинга остается, чтобы избежать слишком частых запусков
        all_properties = get_properties(limit=1)
        if all_properties:
            latest_property = max(all_properties, key=lambda x: x.get('parsed_at', ''))
            last_parsed_str = latest_property.get('parsed_at')
            if last_parsed_str:
                try:
                    last_parsed_time = datetime.fromisoformat(last_parsed_str.replace('Z', '+00:00'))
                    time_since_last_parse = datetime.now(last_parsed_time.tzinfo) - last_parsed_time
                    if time_since_last_parse < timedelta(hours=5.9):  # Небольшой запас
                        logger.info(f"Парсинг был недавно. Пропускаем запуск.")
                        return "Parsing was recent. Skipped.", 200
                except Exception as e:
                    logger.warning(f"Ошибка проверки времени последнего парсинга: {e}. Продолжаем.")

        logger.info("Выполняем парсинг OLX...")
        added = await parse_olx_listing()
        logger.info(f"Парсинг завершён. Добавлено: {added} объектов")
        return f"Parsing finished. Added {added} items.", 200

    except Exception as e:
        logger.error(f"Критическая ошибка при выполнении парсинга: {e}")
        return f"Error during parsing: {e}", 500

@app.route("/", methods=['GET', 'POST'])
def handle_request():
    """
    Основная точка входа для облачной функции.
    Cloud Scheduler будет отправлять сюда запросы.
    """
    logger.info("Функция парсера вызвана.")
    # Запускаем асинхронную логику в синхронном контексте Flask
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response_text, status_code = loop.run_until_complete(run_olx_parser_logic())
    loop.close()
    return response_text, status_code

if __name__ == "__main__":
    # Этот блок для локального тестирования функции, он не будет использоваться в Cloud Functions
    app.run(debug=True, port=8081)
