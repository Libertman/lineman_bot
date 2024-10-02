from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated
from aiogram.filters import Command, CommandStart, or_f
from lexicon.lexicon_ru import LEXICON_RU
from services.services import registration_of_deadlines
from keyboards.keyboards import functions_keyboard, help_start_keyboard, subjects_keyboard, pe_keyboard, economics_keyboard, russia_keyboard, digital_keyboard, english_keyboard
from database.database import deadlines, nearest_list_deadlines
from services.services import translate_to_date
from datetime import datetime
from database.sql import get_user, update_user
from pytz import timezone
import logging


router = Router()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='{filename}:{lineno} #{levelname:8} '
                        '[{asctime}] - {name} - {message}', style='{')


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(LEXICON_RU['/start'], reply_markup=help_start_keyboard)
    if message.chat.type == 'private':
        flag = get_user(user_id=message.from_user.id)['flag']
        logger.debug(datetime.now())
        if not flag:
            update_user(user_id=message.from_user.id, flag=1)
            await registration_of_deadlines(message)
    else:
        flag = get_user(user_id=message.chat.id)['flag']
        logger.debug(flag)
        if not flag:
            update_user(user_id=message.chat.id, flag=1)
            await registration_of_deadlines(message)


@router.message(or_f(F.text == 'Помощь', F.text == 'ПОМОГИТЕ'))
async def process_help_command(message: Message):
    await message.answer(LEXICON_RU['/help'], reply_markup=functions_keyboard)


@router.message(F.text == 'ДЕДЛАЙНЫ ПО ПРЕДМЕТАМ')
async def process_show_subjects_deadlines(message: Message):
    await message.answer("Выберите предмет", reply_markup=subjects_keyboard)


@router.message(F.text == 'БЛИЖАЙШИЕ ДЕДЛАЙНЫ')
async def process_nearest_deadlines_command(message: Message):
    imp_index = 3
    while imp_index < len(nearest_list_deadlines) and nearest_list_deadlines[imp_index-1].deadline == nearest_list_deadlines[imp_index].deadline:
        imp_index += 1
    return_deadlines = "\n".join([f"{ind}) <b>{deadline.subject}</b>: {deadline.name} -> {deadline.deadline.strftime('%d.%m.%y')}\nОсталось: {translate_to_date(deadline.deadline - datetime.now(timezone('Europe/Moscow')))}" for ind, deadline in enumerate(nearest_list_deadlines[:imp_index], 1)])
    return_text = f'<b>БЛИЖАЙШИЕ ДЕДЛАЙНЫ</b>\n\n{return_deadlines}'
    return_text += '\n\n...' if imp_index < len(nearest_list_deadlines) else ''
    await message.answer(return_text, reply_markup=functions_keyboard)


@router.message(F.text == 'Создатели')
async def process_authors_command(message: Message):
    await message.answer(LEXICON_RU['authors_description'])


@router.callback_query(F.data == 'pe')
async def process_pe_subject(callback: CallbackQuery):
    current_time = datetime.now(timezone('Europe/Moscow'))
    all_deadlines = '\n'.join([f"{index}) {deadline.name} -> <b>{deadline.deadline.strftime('%d.%m.%y')}</b>\nОсталось: {translate_to_date(deadline.deadline - current_time)}\n" for index, deadline in enumerate(filter(lambda x: x.deadline > current_time, deadlines['Физическая культура']), 1)])
    await callback.message.edit_text(text=LEXICON_RU['pe_description'].format(all_deadlines), reply_markup=pe_keyboard)


@router.callback_query(F.data == 'economics')
async def process_economics_subject(callback: CallbackQuery):
    current_time = datetime.now(timezone('Europe/Moscow'))
    all_deadlines = '\n'.join([f"{index}) {deadline.name} -> <b>{deadline.deadline.strftime('%d.%m.%y')}</b>\nОсталось: {translate_to_date(deadline.deadline - current_time)}\n" for index, deadline in enumerate(filter(lambda x: x.deadline > current_time, deadlines['Экономическая культура']), 1)])
    await callback.message.edit_text(text=LEXICON_RU['economics_description'].format(all_deadlines), reply_markup=economics_keyboard)


@router.callback_query(F.data == 'digital')
async def process_digital_subject(callback: CallbackQuery):
    current_time = datetime.now(timezone('Europe/Moscow'))
    all_deadlines = '\n'.join([f"{index}) {deadline.name} -> <b>{deadline.deadline.strftime('%d.%m.%y')}</b>\nОсталось: {translate_to_date(deadline.deadline - current_time)}\n" for index, deadline in enumerate(filter(lambda x: x.deadline > current_time, deadlines['Цифровая грамотность']), 1)])
    await callback.message.edit_text(text=LEXICON_RU['digital_description'].format(all_deadlines), reply_markup=digital_keyboard)


@router.callback_query(F.data == 'english')
async def process_english_subject(callback: CallbackQuery):
    current_time = datetime.now(timezone('Europe/Moscow'))
    all_deadlines = '\n'.join([f"{index}) {deadline.name} -> <b>{deadline.deadline.strftime('%d.%m.%y')}</b>\nОсталось: {translate_to_date(deadline.deadline - current_time)}\n" for index, deadline in enumerate(filter(lambda x: x.deadline > current_time, deadlines['Английский язык']), 1)])
    await callback.message.edit_text(text=LEXICON_RU['english_description'].format(all_deadlines), reply_markup=english_keyboard)


@router.callback_query(F.data == 'russia')
async def process_russia_subject(callback: CallbackQuery):
    current_time = datetime.now(timezone('Europe/Moscow'))
    all_deadlines = '\n'.join([f"{index}) {deadline.name} -> <b>{deadline.deadline.strftime('%d.%m.%y')}</b>\nОсталось: {translate_to_date(deadline.deadline - current_time)}\n" for index, deadline in enumerate(filter(lambda x: x.deadline > current_time, deadlines['Россия: государственное основание и мировоззрение']), 1)])
    await callback.message.edit_text(text=LEXICON_RU['russia_description'].format(all_deadlines), reply_markup=russia_keyboard)


@router.callback_query(F.data == 'cancel')
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.edit_text(text="Выберите предмет", reply_markup=subjects_keyboard)


@router.message(F.photo)
async def process_photo_command(message: Message):
    if message.chat.type == 'private':
        await message.answer_photo('https://www.meme-arsenal.com/memes/504e722544e9173d566732bf258d253f.jpg')


@router.message(F.sticker)
async def process_sticker_command(message: Message):
    if message.chat.type == 'private':
        await message.answer_sticker('CAACAgIAAxkBAAO6ZNzAy6gWdfJeLtgN3bY4T3HcmsYAArYmAAIYKJFJVvHiKO8JxjUwBA')
