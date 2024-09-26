from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from lexicon.lexicon_ru import LEXICON_RU
from services.services import registration_of_deadlines


router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(LEXICON_RU['/start'])
    await registration_of_deadlines(message)


@router.message(F.photo)
async def process_photo_command(message: Message):
    await message.answer_photo('AgACAgIAAxkBAAOxZNy9k3OeJws7YoOYouRq3nuPDzAAAp3OMRt6ouBKOIxIA6inc1QBAAMCAAN5AAMwBAk')


@router.message(F.sticker)
async def process_sticker_command(message: Message):
    await message.answer_sticker('CAACAgIAAxkBAAO6ZNzAy6gWdfJeLtgN3bY4T3HcmsYAArYmAAIYKJFJVvHiKO8JxjUwBA')