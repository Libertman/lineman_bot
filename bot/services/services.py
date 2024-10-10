from datetime import datetime, timedelta
from database.database import deadlines
from aiogram.types import Message
from lexicon.lexicon_ru import LEXICON_RU
from pytils.numeral import get_plural
from pytz import timezone
import asyncio


async def registration_of_deadlines(message: Message):
    for lesson in deadlines:
        for paragraph in deadlines[lesson]:
            for time_delta in ([21600, 129600] + paragraph.reminder):
                asyncio.create_task(launch_deadlines(message, lesson, paragraph, timedelta(seconds=time_delta)))


async def launch_deadlines(message: Message, lesson: str, paragraph: str, time_delta: timedelta):
    current_time = int(datetime.now(timezone('Europe/Moscow')).timestamp())
    if (paragraph.deadline - time_delta).timestamp() > current_time:
        sleep_time = timedelta(seconds=((paragraph.deadline - time_delta).timestamp() - current_time))
        await asyncio.sleep(sleep_time.days * 86400 + sleep_time.seconds)
        if time_delta.days >= 3:
            await message.answer(text=LEXICON_RU['courses_deadlines']['deadline_far_reminder'].format(lesson, paragraph.name, translate_to_date(time_delta)))
        else:
            await message.answer(text=LEXICON_RU['courses_deadlines']['deadline_common_reminder'].format(lesson, paragraph.name, translate_to_date(time_delta)))
    return

def translate_to_date(delta: float):
    hours = delta.seconds % 86400 // 3600
    minutes = delta.seconds % 3600 // 60
    return f'{get_plural(delta.days, "ДЕНЬ, ДНЯ, ДНЕЙ") + " " if delta.days > 0 else ""}' + f'{get_plural(hours, "ЧАС, ЧАСА, ЧАСОВ") + " " if hours > 0 else ""}' + f'{get_plural(minutes, "МИНУТА, МИНУТЫ, МИНУТ") if minutes > 0 else ""}'
