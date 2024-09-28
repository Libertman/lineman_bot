from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, or_f
from lexicon.lexicon_ru import LEXICON_RU
from services.services import registration_of_deadlines
from keyboards.keyboards import functions_keyboard, help_start_keyboard, subjects_keyboard, pe_keyboard, economics_keyboard, russia_keyboard, digital_keyboard, english_keyboard
from database.database import deadlines
from services.services import translate_to_date
from datetime import datetime


router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(LEXICON_RU['/start'], reply_markup=help_start_keyboard)
    await registration_of_deadlines(message)


@router.message(or_f(F.text == 'Помощь', F.text == 'ПОМОГИТЕ'))
async def process_help_command(message: Message):
    await message.answer(LEXICON_RU['/help'], reply_markup=functions_keyboard)


@router.message(F.text == 'ДЕДЛАЙНЫ ПО ПРЕДМЕТАМ')
async def process_show_subjects_deadlines(message: Message):
    await message.answer("Выберите предмет", reply_markup=subjects_keyboard)


@router.message(F.text == '⚽️Физическая культура⚽️')
async def process_pe_subject(message: Message):
    current_time = datetime.now()
    all_deadlines = '\n'.join([f"{index}. {deadline.name} -> {deadline.deadline.strftime('%d.%m.%y')}\nОсталось: {translate_to_date(deadline.deadline - current_time)}\n\n" for index, deadline in enumerate(deadlines['Физическая культура'], 1) if deadline.deadline > current_time]) + '\n'
    await message.answer(LEXICON_RU['pe_description'].format(all_deadlines), reply_markup=pe_keyboard)


@router.message(F.text == '🤑Экономическая культура🤑')
async def process_economics_subject(message: Message):
    current_time = datetime.now()
    all_deadlines = '\n'.join([f"{index}. {deadline.name} -> {deadline.deadline.strftime('%d.%m.%y')}\nОсталось: {translate_to_date(deadline.deadline - current_time)}\n\n" for index, deadline in enumerate(deadlines['Экономическая культура'], 1) if deadline.deadline > current_time]) + '\n'
    await message.answer(LEXICON_RU['economics_description'].format(all_deadlines), reply_markup=economics_keyboard)


@router.message(F.text == '💻Цифровая грамотность💻')
async def process_digital_subject(message: Message):
    current_time = datetime.now()
    all_deadlines = '\n'.join([f"{index}. {deadline.name} -> {deadline.deadline.strftime('%d.%m.%y')}\nОсталось: {translate_to_date(deadline.deadline - current_time)}\n\n" for index, deadline in enumerate(deadlines['Цифровая грамотность'], 1) if deadline.deadline > current_time]) + '\n'
    await message.answer(LEXICON_RU['digital_description'].format(all_deadlines), reply_markup=digital_keyboard)


@router.message(F.text == '🇺🇸Английский язык🇺🇸')
async def process_english_subject(message: Message):
    current_time = datetime.now()
    all_deadlines = '\n'.join([f"{index}. {deadline.name} -> {deadline.deadline.strftime('%d.%m.%y')}\nОсталось: {translate_to_date(deadline.deadline - current_time)}\n\n" for index, deadline in enumerate(deadlines['Английский язык'], 1) if deadline.deadline > current_time]) + '\n'
    await message.answer(LEXICON_RU['english_description'].format(all_deadlines), reply_markup=english_keyboard)


@router.message(F.text == '🇷🇺Россия: гос. основание и мировоззрение🇷🇺')
async def process_russia_subject(message: Message):
    current_time = datetime.now()
    first_deadline = deadlines['Россия: государственное основание и мировоззрение'][0]
    all_deadlines = first_deadline.name + f' -> {first_deadline.deadline.strftime("%d.%m.%y")}\nОсталось: {translate_to_date(first_deadline.deadline - current_time)}\n\n' if first_deadline.deadline > current_time else ''
    all_deadlines += '\n'.join([f"{index}. {deadline.name} -> {deadline.deadline.strftime('%d.%m.%y')}\nОсталось: {translate_to_date(deadline.deadline - current_time)} \n\n" for index, deadline in enumerate(deadlines['Россия: государственное основание и мировоззрение'][1:], 9) if deadline.deadline > current_time])
    await message.answer(LEXICON_RU['Россия: государственное основание и мировоззрение'].format(all_deadlines), reply_markup=russia_keyboard)


@router.message(F.photo)
async def process_photo_command(message: Message):
    await message.answer_photo('AgACAgIAAxkBAAOxZNy9k3OeJws7YoOYouRq3nuPDzAAAp3OMRt6ouBKOIxIA6inc1QBAAMCAAN5AAMwBAk')


@router.message(F.sticker)
async def process_sticker_command(message: Message):
    await message.answer_sticker('CAACAgIAAxkBAAO6ZNzAy6gWdfJeLtgN3bY4T3HcmsYAArYmAAIYKJFJVvHiKO8JxjUwBA')
