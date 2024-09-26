from datetime import datetime
from database.database import deadlines
from aiogram.types import Message
from lexicon.lexicon_ru import LEXICON_RU
from pytils.numeral import get_plural
import asyncio


async def registration_of_deadlines(message: Message):
    tasks = []
    for lesson in deadlines:
        for paragraph in deadlines[lesson]:
            for time_delta in paragraph.reminder:
                tasks.append(launch_deadlines(message, lesson, paragraph, time_delta))
    await asyncio.gather(*tasks)


async def launch_deadlines(message: Message, lesson: str, paragraph: str, time_delta: int):
    current_time = datetime.now()
    if paragraph.deadline - time_delta > current_time:
        await asyncio.sleep((paragraph.deadline - time_delta - current_time).seconds)
        if time_delta == 604_800:
            await message.answer(text=LEXICON_RU['courses_deadlines']['deadline_far_reminder'].format(lesson, paragraph.name))
        else:
            await message.answer(text=LEXICON_RU['courses_deadlines']['deadline_reminder'].format(lesson, paragraph, get_plural(time_delta.hour, "ЧАС, ЧАСА, ЧАСОВ")))


async def launch_user_deadlines(message: Message, name: str, deadline: datetime, time_delta: int):
    current_time = datetime.now()
    await asyncio.sleep((deadline - time_delta - current_time).seconds)
    hours = time_delta.seconds % 86400 // 3600
    minutes = time_delta.seconds % 3600 // 60
    total_delta_time = f'{get_plural(time_delta.days, "ДЕНЬ, ДНЯ, ДНЕЙ") if time_delta.days > 0 else ""}' + f'{get_plural(hours, "ЧАС, ЧАСА, ЧАСОВ") if hours > 0 else ""}' + f'{get_plural(minutes, "МИНУТА, МИНУТЫ, МИНУТ") if minutes > 0 else ""}'
    await message.answer(text=LEXICON_RU['deadline_user_reminder'].format(name, total_delta_time))