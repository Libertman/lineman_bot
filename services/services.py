from datetime import datetime, timedelta
from database.database import deadlines
from aiogram.types import Message
from lexicon.lexicon_ru import LEXICON_RU
from pytils.numeral import get_plural
import asyncio


async def registration_of_deadlines(message: Message):
    tasks = []
    for lesson in deadlines:
        for paragraph in deadlines[lesson]:
            for time_delta in ([21600, 86400] + paragraph.reminder):
                tasks.append(launch_deadlines(message, lesson, paragraph, timedelta(seconds=time_delta)))
    await asyncio.gather(*tasks)


async def launch_deadlines(message: Message, lesson: str, paragraph: str, time_delta: timedelta):
    current_time = datetime.now()
    if paragraph.deadline - time_delta > current_time:
        sleep_time = paragraph.deadline - time_delta - current_time
        await asyncio.sleep(sleep_time.days * 86400 + sleep_time.seconds)
        if time_delta.days == 7:
            await message.answer(text=LEXICON_RU['courses_deadlines']['deadline_far_reminder'].format(lesson, paragraph.name))
        else:
            await message.answer(text=LEXICON_RU['courses_deadlines']['deadline_common_reminder'].format(lesson, paragraph.name, get_plural(time_delta.seconds % 86400 // 3600, "ЧАС, ЧАСА, ЧАСОВ")))
    return

def translate_to_date(delta: timedelta):
    hours = delta.seconds % 86400 // 3600
    minutes = delta.seconds % 3600 // 60
    return f'{get_plural(delta.days, "ДЕНЬ, ДНЯ, ДНЕЙ") + " " if delta.days > 0 else ""}' + f'{get_plural(hours, "ЧАС, ЧАСА, ЧАСОВ") + " " if hours > 0 else ""}' + f'{get_plural(minutes, "МИНУТА, МИНУТЫ, МИНУТ") if minutes > 0 else ""}'
