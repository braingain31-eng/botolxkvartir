from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from database.models import SessionLocal, User
from datetime import datetime, timedelta

REMINDERS = [
    "Вы смотрели виллу, но не связались. Прямая бронь — дешевле!",
    "80% жилья — у частников. Только у нас — прямые контакты.",
    "Обновлено 47 новых объектов! Хотите контакты?",
    "«Нашёл бунгало за 40к ₿» — отзыв Алексея",
    "Мы — №1 по охвату в Гоа. Всё в одной базе.",
    "Цены растут! Забронируй по старой цене.",
    "Приведи друга — +3 дня бесплатно!",
    "Последний шанс: оплатите за 10$"
]

async def send_reminders(bot: Bot):
    session = SessionLocal()
    users = session.query(User).filter(
        User.paid_until == None,
        User.viewed_properties != []
    ).all()
    for user in users:
        if user.last_seen < datetime.utcnow() - timedelta(days=1):
            reminder_idx = len(user.viewed_properties) % 8
            await bot.send_message(
                user.user_id,
                REMINDERS[reminder_idx],
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton("Оплатить 10$", callback_data="pay_7")]
                ])
            )
    session.close()

def start_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_reminders, "cron", hour=10, args=[bot])
    scheduler.start()