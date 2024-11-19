from datetime import datetime, timedelta
from pytils.numeral import get_plural
from aiogram.fsm.context import FSMContext
import calendar
import asyncio
import time


# async def registration_of_deadlines(message: Message):
#     for lesson in deadlines:
#         for paragraph in deadlines[lesson]:
#             for time_delta in ([21600, 129600] + paragraph.reminder):
#                 asyncio.create_task(launch_deadlines(message, lesson, paragraph, timedelta(seconds=time_delta)))


# async def launch_deadlines(message: Message, lesson: str, paragraph: str, time_delta: timedelta):
#     current_time = int(datetime.now(timezone('Europe/Moscow')).timestamp())
#     if (paragraph.deadline - time_delta).timestamp() > current_time:
#         sleep_time = timedelta(seconds=((paragraph.deadline - time_delta).timestamp() - current_time))
#         await asyncio.sleep(sleep_time.days * 86400 + sleep_time.seconds)
#         if time_delta.days >= 3:
#             await message.answer(text=LEXICON_RU['courses_deadlines']['deadline_far_reminder'].format(lesson, paragraph.name, translate_to_date(time_delta)))
#         else:
#             await message.answer(text=LEXICON_RU['courses_deadlines']['deadline_common_reminder'].format(lesson, paragraph.name, translate_to_date(time_delta)))
#     return



def translate_to_date(delta: timedelta):
    hours = delta.seconds % 86400 // 3600
    minutes = delta.seconds % 3600 // 60
    return f'{get_plural(delta.days, "ДЕНЬ, ДНЯ, ДНЕЙ") + " " if delta.days > 0 else ""}' + f'{get_plural(hours, "ЧАС, ЧАСА, ЧАСОВ") + " " if hours > 0 else ""}' + f'{get_plural(minutes, "МИНУТА, МИНУТЫ, МИНУТ") if minutes > 0 else ""}'


def days_in_month(month: int):
    if month in {1, 3, 5, 7, 8, 10, 12}:
        return 31
    elif month == 2:
        return 28


def check_year(year: int):
    year_now = (datetime.now() + timedelta(hours=3)).year
    if year < year_now or year - year_now > 1:
        return False
    return True


def check_month(year: int, month: int):
    date_now = datetime.now() + timedelta(hours=3)
    if not(1 <= month <= 12) or (year == date_now.year and month < date_now.month):
        return False
    return True


def check_day(year: int, month: int, day: int):
    date_now = datetime.now() + timedelta(hours=3)
    month_days = calendar.monthrange(year, month)[1]
    if not(1 <= day <= month_days) or (date_now.year == year and date_now.month == month and date_now.day > day):
        return False
    return True


def check_hour(year: int, month: int, day: int, hour: int, reminder: bool = False):
    date_now = datetime.now() + timedelta(hours=3)
    if not reminder:
        if not(0 <= hour <= 23) or (date_now.year == year and date_now.month == month and date_now.day == day and date_now.hour > hour):
            return False
        return True
    else:
        if not(0 <= hour <= 23):
            return False
        return True


def check_minute(year: int, month: int, day: int, hour: int, minute: int, reminder: bool = False):
    date_now = datetime.now() + timedelta(hours=3)
    if not reminder:
        if not(0 <= minute <= 59) or (date_now.year == year and date_now.month == month and date_now.day == day and date_now.hour == hour and date_now.minute > minute):
            return False
        return True
    else:
        if not(0 <= minute <= 59):
            return False
        return True


def check_reminder(year: int, month: int, day: int, hour: int, minute: int, reminder: list[int]):
    date_now = datetime.now() + timedelta(hours=3)
    reminder_datetime = datetime(year, month, day, hour, minute) - timedelta(days=reminder[0], hours=reminder[1], minutes=reminder[2])
    if date_now >= reminder_datetime:
        return False
    return True


async def auto_delete_message(bot, chat_id: int, message_id: int, state: FSMContext, timeout: int, check_interval: int = 5):
    while True:
        await asyncio.sleep(check_interval)
        if await state.get_state():
            data = await state.get_data()
            last_interaction = data.get('last_interaction', 0)
            if last_interaction:
                if int(time.time()) - last_interaction >= timeout:
                    try:
                        await bot.delete_message(chat_id, message_id)
                        await state.update_data(last_interaction=None)
                        break
                    except Exception:
                        break
            else:
                break
        else:
            break