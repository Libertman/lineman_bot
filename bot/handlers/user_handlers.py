from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, or_f, StateFilter
from aiogram.fsm.state import default_state
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.keyboards import functions_keyboard, help_start_keyboard, subjects_keyboard, pe_keyboard, economics_keyboard, russia_keyboard, digital_keyboard, english_keyboard
from database.sql import get_user_deadlines, get_subject_deadlines, delete_completed_task
from services.services import translate_to_date
from datetime import datetime, timedelta
import logging


router = Router()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='{filename}:{lineno} #{levelname:8} '
                        '[{asctime}] - {name} - {message}', style='{')


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(LEXICON_RU['/start'], reply_markup=help_start_keyboard)


@router.message(or_f(F.text == '⚙️Помощь⚙️', F.text == '🙏🏻ПОМОГИТЕ🙏🏻'), StateFilter(default_state))
async def process_help_command(message: Message):
    await message.answer(LEXICON_RU['/help'], reply_markup=functions_keyboard)


@router.message(F.text == '📚ДЕДЛАЙНЫ ПО ПРЕДМЕТАМ📚', StateFilter(default_state))
async def process_show_subjects_deadlines(message: Message):
    await message.answer("Выберите предмет", reply_markup=subjects_keyboard)


@router.message(F.text == '⏳БЛИЖАЙШИЕ ДЕДЛАЙНЫ⏳', StateFilter(default_state))
async def process_nearest_deadlines_command(message: Message):
    datetime_now = datetime.now() + timedelta(hours=3)
    nearest_list_deadlines = await get_user_deadlines(message.from_user.id)
    imp_index = 3
    while imp_index < len(nearest_list_deadlines) and nearest_list_deadlines[imp_index-1]['deadline'] == nearest_list_deadlines[imp_index]['deadline']:
        imp_index += 1
    return_deadlines = "\n\n".join([f"{ind}) <b><a href='{LEXICON_RU['courses_linkers'][deadline['subject']]['course']}'>{deadline['subject']}</a></b>: {deadline['title']} -> <b>{deadline['deadline'].strftime('%d.%m.%y')}</b>\n<i>Осталось</i>: <u>{translate_to_date(deadline['deadline'] - datetime_now)}</u>\n<a href='{LEXICON_RU['courses_linkers'][deadline['subject']]['answers']}'>ОТВЕТЫ НА КУРС</a>" for ind, deadline in enumerate(nearest_list_deadlines[:imp_index], 1)])
    return_text = f'<b>⏳БЛИЖАЙШИЕ ДЕДЛАЙНЫ⏳</b>\n\n{return_deadlines}'
    return_text += '\n\n...' if imp_index < len(nearest_list_deadlines) else ''
    await message.answer(return_text, reply_markup=functions_keyboard, disable_web_page_preview=True)


@router.message(F.text == '👨🏻‍💻Создатели👨🏻‍💻', StateFilter(default_state))
async def process_authors_command(message: Message):
    await message.answer(LEXICON_RU['authors_description'])


@router.callback_query(F.data == 'pe', StateFilter(default_state))
async def process_pe_subject(callback: CallbackQuery):
    current_time = datetime.now() + timedelta(hours=3)
    subject_deadlines = await get_subject_deadlines("Физическая культура")
    all_deadlines = '\n'.join([f"{index}) {deadline['title']} -> <b>{deadline['deadline'].strftime('%d.%m.%y')}</b>\nОсталось: <u>{translate_to_date(deadline['deadline'] - current_time)}</u>\n" for index, deadline in enumerate(subject_deadlines, 1)])
    await callback.message.edit_text(text=LEXICON_RU['pe_description'].format(all_deadlines), reply_markup=pe_keyboard)


@router.callback_query(F.data == 'economics', StateFilter(default_state))
async def process_economics_subject(callback: CallbackQuery):
    current_time = datetime.now() + timedelta(hours=3)
    subject_deadlines = await get_subject_deadlines("Экономическая культура")
    all_deadlines = '\n'.join([f"{index}) {deadline['title']} -> <b>{deadline['deadline'].strftime('%d.%m.%y')}</b>\nОсталось: <u>{translate_to_date(deadline['deadline'] - current_time)}</u>\n" for index, deadline in enumerate(subject_deadlines, 1)])
    await callback.message.edit_text(text=LEXICON_RU['economics_description'].format(all_deadlines), reply_markup=economics_keyboard)


@router.callback_query(F.data == 'digital', StateFilter(default_state))
async def process_digital_subject(callback: CallbackQuery):
    current_time = datetime.now() + timedelta(hours=3)
    subject_deadlines = await get_subject_deadlines("Цифровая грамотность")
    all_deadlines = '\n'.join([f"{index}) {deadline['title']} -> <b>{deadline['deadline'].strftime('%d.%m.%y')}</b>\nОсталось: <u>{translate_to_date(deadline['deadline'] - current_time)}</u>\n" for index, deadline in enumerate(subject_deadlines, 1)])
    await callback.message.edit_text(text=LEXICON_RU['digital_description'].format(all_deadlines), reply_markup=digital_keyboard)


@router.callback_query(F.data == 'english', StateFilter(default_state))
async def process_english_subject(callback: CallbackQuery):
    current_time = datetime.now() + timedelta(hours=3)
    subject_deadlines = await get_subject_deadlines("Английский язык")
    all_deadlines = '\n'.join([f"{index}) {deadline['title']} -> <b>{deadline['deadline'].strftime('%d.%m.%y')}</b>\nОсталось: <u>{translate_to_date(deadline['deadline'] - current_time)}</u>\n" for index, deadline in enumerate(subject_deadlines, 1)])
    await callback.message.edit_text(text=LEXICON_RU['english_description'].format(all_deadlines), reply_markup=english_keyboard)


@router.callback_query(F.data == 'russia', StateFilter(default_state))
async def process_russia_subject(callback: CallbackQuery):
    current_time = datetime.now() + timedelta(hours=3)
    subject_deadlines = await get_subject_deadlines("Россия: государственное основание и мировоззрение")
    all_deadlines = '\n'.join([f"{index}) {deadline['title']} -> <b>{deadline['deadline'].strftime('%d.%m.%y')}</b>\nОсталось: <u>{translate_to_date(deadline['deadline'] - current_time)}</u>\n" for index, deadline in enumerate(subject_deadlines, 1)])
    await callback.message.edit_text(text=LEXICON_RU['russia_description'].format(all_deadlines), reply_markup=russia_keyboard)


@router.callback_query(F.data == 'cancel')
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.edit_text(text="Выберите предмет", reply_markup=subjects_keyboard)


@router.callback_query(F.data == 'already_done')
async def process_already_done_button(callback_query: CallbackQuery):
    message = callback_query.message.text
    if 'ДО ТВОЕГО СОБЫТИЯ' not in message:
        subject_name = message[message.index('ПО КУРСУ')+10:message.index('ТЕМА')-1]
        title = message[message.index('ТЕМА')+6:message.index('ОСТАЛОСЬ')-1]
        if not await delete_completed_task(title, callback_query.from_user.id, subject_name):
            await callback_query.answer(text='Дедлайн истек, так что меня не особо волнует сделал ты задание или нет🙃', show_alert=True)
    else:
        ...
    await callback_query.message.delete()


@router.message(F.photo)
async def process_photo_command(message: Message):
    if message.chat.type == 'private':
        await message.answer_photo('https://www.meme-arsenal.com/memes/504e722544e9173d566732bf258d253f.jpg')


@router.message(F.sticker)
async def process_sticker_command(message: Message):
    if message.chat.type == 'private':
        await message.answer_sticker('CAACAgIAAxkBAAO6ZNzAy6gWdfJeLtgN3bY4T3HcmsYAArYmAAIYKJFJVvHiKO8JxjUwBA')
