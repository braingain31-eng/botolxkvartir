
import threading
import subprocess
from flask import Flask
import os

# Создаем минимальное Flask-приложение
app = Flask(__name__)

@app.route('/')
def hello():
    # Эта страница будет отвечать на проверки работоспособности Cloud Run
    return "Bot is running in background.", 200

def run_bot():
    # Эта функция запускает вашего бота в отдельном процессе
    # Мы используем subprocess, чтобы он работал полностью независимо
    print("Starting bot process...")
    try:
        subprocess.run(["python", "main_bot.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Bot process failed with exit code {e.returncode}")
    except FileNotFoundError:
        print("Error: main_bot.py not found. Make sure the file exists.")


if __name__ == '__main__':
    # Запускаем бота в фоновом потоке, чтобы не блокировать веб-сервер
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # Запускаем веб-сервер Gunicorn, как того требует Cloud Run
    # Gunicorn будет запущен из Dockerfile, этот блок для локального теста
    # Но наличие app = Flask() необходимо для Gunicorn
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

