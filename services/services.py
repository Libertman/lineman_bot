from datetime import datetime
from database.database import deadlines
from aiogram.types import Message
from lexicon.lexicon_ru import LEXICON_RU
import asyncio


async def registration_of_deadlines(message: Message):
    tasks = []
    for lesson in deadlines:
        for paragraph in deadlines[lesson]:
            for time_delta in (21600, 86400):
                tasks.append(launch_deadlines(message, lesson, paragraph, time_delta))
    await asyncio.gather(*tasks)


async def launch_deadlines(message: Message, lesson: str, paragraph: str, time_delta: int):
    current_time = datetime.now()
    if deadlines[lesson][paragraph] - time_delta > current_time:
        await asyncio.sleep(time_delta)
        if time_delta == 604_800:
            await message.answer(text=LEXICON_RU['deadline_far_reminder'].format(lesson, paragraph, len(paragraph.split('\n'))))
        else:
            await message.answer(text=LEXICON_RU['deadline_reminder'].format(lesson, paragraph, time_delta // 60 // 60))
