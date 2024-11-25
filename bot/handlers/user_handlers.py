from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, or_f, StateFilter
from aiogram.fsm.state import default_state
from aiogram.exceptions import TelegramBadRequest
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.keyboards import functions_keyboard, help_start_keyboard, pe_keyboard, economics_keyboard, russia_keyboard, digital_keyboard, english_keyboard, generate_choice_subjects, generate_subjects_deadlines, add_keyboard, check_continue_keyboard, fix_reminder_keyboard, ask_reminders_deadline_keyboard, generate_user_deadlines, generate_manage_user_deadline, change_subjects_keyboard
from database.sql import get_deadlines, get_subject_deadlines, delete_completed_task, insert_new_user, get_user, add_user_deadline_base, delete_user_deadline, update_data, get_deadline, get_user_deadlines
from services.services import translate_to_date, auto_delete_message, check_year, check_month, check_day, check_hour, check_minute, check_reminder, keyboard2list
from states.states import FSMRegistrationUser, FSMAddUserDeadline
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from string import ascii_letters
import logging
import time


router = Router()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='{filename}:{lineno} #{levelname:8} '
                        '[{asctime}] - {name} - {message}', style='{')

template_message_info = {'need_to_delete': [], 'subjects': ['Физическая культура', 'Экономическая культура', 'Россия: гос. осн. и мировоззрение', 'Цифровая грамотность', 'Английский язык']}


# ---------------COMMON HANDLERS---------------


@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(LEXICON_RU['/start'], reply_markup=help_start_keyboard)


@router.message(or_f(F.text == '⚙️Помощь⚙️', F.text == '🙏🏻ПОМОГИТЕ🙏🏻'), StateFilter(default_state))
async def process_help_command(message: Message, state: FSMContext):
    await message.answer(LEXICON_RU['/help'], reply_markup=functions_keyboard)
    if not await get_user(message.chat.id):
        await state.set_state(FSMRegistrationUser.waiting_for_subjects)
        bot_message = await message.bot.send_message(chat_id=message.chat.id, text='📝Вам необходимо пройти небольшую регистрацию📝\n\n📚Выберите предметы, по которым вы хотите получать напоминания о дедлайнах', reply_markup=generate_choice_subjects([]))
        await state.update_data(selected_subjects=[], message_id=bot_message.message_id, last_interaction=int(time.time()))
        await auto_delete_message(message.bot, message.chat.id, bot_message.message_id, state, 300)


@router.message(F.text == '👨🏻‍💻Создатели👨🏻‍💻', StateFilter(default_state))
async def process_authors_command(message: Message):
    await message.answer(LEXICON_RU['authors_description'])


@router.message(F.photo, StateFilter(default_state))
async def process_photo_command(message: Message):
    if message.chat.type == 'private':
        await message.answer_photo('https://www.meme-arsenal.com/memes/504e722544e9173d566732bf258d253f.jpg')


@router.message(F.sticker, StateFilter(default_state))
async def process_sticker_command(message: Message):
    if message.chat.type == 'private':
        await message.answer_sticker('CAACAgIAAxkBAAO6ZNzAy6gWdfJeLtgN3bY4T3HcmsYAArYmAAIYKJFJVvHiKO8JxjUwBA')


# ---------------REGISTRATION HANDLERS---------------


@router.callback_query(F.data.in_(['pe_choice', 'economics_choice', 'russia_choice', 'digital_choice', 'english_choice']), StateFilter(FSMRegistrationUser.waiting_for_subjects))
async def process_get_subjects_button(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_subjects = data.get("selected_subjects")
    if callback_query.data in selected_subjects:
        selected_subjects.remove(callback_query.data)
    else:
        selected_subjects.append(callback_query.data)

    await state.update_data(selected_subjects=selected_subjects, last_interaction=int(time.time()))
    await callback_query.message.edit_reply_markup(reply_markup=generate_choice_subjects(selected_subjects))


@router.callback_query(F.data == 'confirm_choice_subjects', StateFilter(FSMRegistrationUser.waiting_for_subjects))
async def process_confirm_subjects_button(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    subjects_data = []
    for subject_callback in data.get('selected_subjects'):
        subjects_data.append(['Физическая культура', 'Экономическая культура', 'Россия: гос. осн. и мировоззрение', 'Цифровая грамотность', 'Английский язык'][('pe_choice', 'economics_choice', 'russia_choice', 'digital_choice', 'english_choice').index(subject_callback)])
    await state.clear()
    await callback_query.message.edit_text(text='🎉<b>Регистрация завершена</b>🎉\n\nВам будут приходить напоминания по выбранным предметам')
    chat = callback_query.message.chat
    if chat.type == 'private':
        username = chat.username if chat.username else ''
        fullname = chat.full_name
    else:
        username = None
        fullname = chat.title
    if await get_user(callback_query.message.chat.id):
        await update_data(callback_query.message.chat.id, subject_names=subjects_data)
    else:
        await insert_new_user(callback_query.message.chat.id, username, fullname, subjects_data)


@router.message(StateFilter(FSMRegistrationUser.waiting_for_subjects))
async def process_fake_registration_callback(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('last_interaction'):
        bot_message = await message.answer('❗️Вы <b><u>не завершили</u></b> прошлое заполнение <u>анкеты регистрации</u>. Вы хотите продолжить заполнение?', reply_markup=check_continue_keyboard)
        try:
            await bot_message.bot.delete_message(chat_id=message.chat.id, message_id=data.get('message_id'))
        except TelegramBadRequest:
            pass
        await state.update_data(template_id=bot_message.message_id, last_interaction=int(time.time()), template=None)
        await auto_delete_message(bot_message.bot, bot_message.chat.id, bot_message.message_id, state, 300)
    else:
        await message.delete()
        await state.update_data(last_interaction=int(time.time()))


@router.callback_query(F.data == 'cancel_template', StateFilter(FSMRegistrationUser.waiting_for_subjects))
async def process_cancel_change_subjects(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await state.clear()
    await callback_query.answer()


@router.callback_query(F.data == 'continue_adding', StateFilter(FSMRegistrationUser.waiting_for_subjects))
async def process_continue_registration(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback_query.message.edit_text(text='📚Выберите предметы, по которым вы хотите получать напоминания о дедлайнах', reply_markup=generate_choice_subjects(data.get('selected_subjects')))
    await state.update_data(last_interaction=int(time.time()))


@router.callback_query(StateFilter(FSMRegistrationUser.waiting_for_subjects))
async def process_fake_registration_callback(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get('last_interaction'):
        bot_message = await callback_query.message.answer('❗️Вы <b><u>не завершили</u></b> прошлое заполнение <u>анкеты регистрации</u>. Вы хотите продолжить заполнение?', reply_markup=check_continue_keyboard)
        try:
            await bot_message.bot.delete_message(chat_id=callback_query.message.chat.id, message_id=data.get('message_id'))
        except TelegramBadRequest:
            pass
        await state.update_data(template_id=bot_message.message_id, last_interaction=int(time.time()), template=None)
        await auto_delete_message(callback_query.message.bot, callback_query.message.chat.id, bot_message.message_id, state, 10)
    else:
        await callback_query.answer(text='Вы не завершили заполнение анкеты регистрации. После этого мы сможете воспользоваться функциями бота😊', show_alert=True)
        await state.update_data(last_interaction=int(time.time()))


# ---------------ADD USER DEADLINE---------------


@router.message(F.text == '🎯ДОБАВИТЬ СОБСТВЕННЫЙ ДЕДЛАЙН🎯', StateFilter(default_state))
async def process_user_deadline_start(message: Message, state: FSMContext):
    template_message = await message.answer(LEXICON_RU['pattern_add_user_deadline'], reply_markup=add_keyboard)
    question_types = {'title': 'str', 'deadline_year': 'int', 'deadline_month': 'int', 'deadline_day': 'int', 'deadline_hour': 'int', 'deadline_minute': 'int', 'reminder_day': 'int', 'reminder_hour': 'int', 'reminder_minute': 'int'}
    await state.update_data(template=LEXICON_RU['pattern_add_user_deadline'], template_id=template_message.message_id, question_types=question_types, question_index=0, history=[LEXICON_RU['pattern_add_user_deadline']], result_data=[], last_interaction=int(time.time()))
    await state.set_state(FSMAddUserDeadline.filling_deadline_info)
    await auto_delete_message(message.bot, message.chat.id, template_message.message_id, state, 300)


@router.message(F.text == '🎯ДОБАВИТЬ СОБСТВЕННЫЙ ДЕДЛАЙН🎯', StateFilter(FSMAddUserDeadline.filling_deadline_info))
async def process_user_deadline_fake(message: Message, state: FSMContext):
    data = await state.get_data()
    bot_message = await message.answer('❗️Вы <b><u>не завершили</u></b> прошлое заполнение своего дедлайна. Вы хотите продолжить заполнение?', reply_markup=check_continue_keyboard)
    try:
        await bot_message.bot.delete_message(chat_id=message.chat.id, message_id=data.get('template_id'))
    except TelegramBadRequest:
        pass
    await state.update_data(template_id=bot_message.message_id, last_interaction=int(time.time()), template=None)
    await auto_delete_message(message.bot, message.chat.id, bot_message.message_id, state, 300)


@router.message(StateFilter(FSMAddUserDeadline.filling_deadline_info))
async def process_handle_add_user_deadline(message: Message, state: FSMContext):
    data = await state.get_data()
    template_message_id = data.get('template_id')
    template = data.get('template')
    if template_message_info['need_to_delete']:
        for m_id in template_message_info['need_to_delete']:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=m_id)
            except TelegramBadRequest:
                pass
        template_message_info['need_to_delete'].clear()
    if not data.get('last_interaction'):
        await message.delete()
        bot_message = await message.answer('❗️Вы <b><u>не завершили</u></b> прошлое заполнение своего дедлайна. Вы хотите продолжить заполнение?', reply_markup=check_continue_keyboard)
        await state.update_data(template_id=bot_message.message_id, last_interaction=int(time.time()), template=None)
        await auto_delete_message(message.bot, message.chat.id, bot_message.message_id, state, 300)
        return
    if not template:
        await message.delete()
        return
    if message.text in ('⏳БЛИЖАЙШИЕ ДЕДЛАЙНЫ⏳', '📚ДЕДЛАЙНЫ ПО ПРЕДМЕТАМ📚', '⚙️Помощь⚙️', '👨🏻‍💻Создатели👨🏻‍💻', '🎯ДОБАВИТЬ СОБСТВЕННЫЙ ДЕДЛАЙН🎯', '👑СВОИ ДЕДЛАЙНЫ👑', '🐵АККАУНТ🐵'):
        await message.delete()
        bot_message = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=template_message_id, text='❗️Вы <b><u>не завершили</u></b> прошлое заполнение своего дедлайна. Вы хотите продолжить заполнение?', reply_markup=check_continue_keyboard)
        await state.update_data(last_interaction=int(time.time()), template=None)
        return

    user_input = message.text
    question_types_keys = list(data.get('question_types').keys())
    question_types_values = list(data.get('question_types').values())
    question_index = data.get('question_index')
    history = data.get('history')
    result_data = data.get('result_data')

    check_letters = ascii_letters + ' абвгдеёжзийклмнопрстуфхцчшщъыьэюя' + 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'.upper()

    if (question_types_values[question_index] == 'int' and not user_input.isdigit()) or (question_types_values[question_index] == 'str' and not any(char in check_letters for char in user_input)):
        await message.delete()
        prohib_message = await message.answer("🚫Тип введенного значения не соответствует допустимому. Введите заново значение")
        template_message_info['need_to_delete'].append(prohib_message.message_id)
        return
    elif question_types_values[question_index] == 'int' and ((question_types_keys[question_index] == 'deadline_year' and not check_year(int(user_input))) or
                                                             (question_types_keys[question_index] == 'deadline_month' and not check_month(result_data[1], int(user_input))) or
                                                             (question_types_keys[question_index] == 'deadline_day' and not check_day(result_data[1], result_data[2], int(user_input))) or
                                                             (question_types_keys[question_index] == 'deadline_hour' and not check_hour(result_data[1], result_data[2], result_data[3], int(user_input))) or
                                                             (question_types_keys[question_index] == 'deadline_minute' and not check_minute(result_data[1], result_data[2], result_data[3], result_data[4], int(user_input))) or
                                                             (question_types_keys[question_index].startswith('reminder_hour') and not check_hour(0, 0, 0, int(user_input), reminder=True)) or
                                                             (question_types_keys[question_index].startswith('reminder_minute') and not check_minute(0, 0, 0, 0, int(user_input), reminder=True))):
        await message.delete()
        prohib_message = await message.answer("🚫Введенное числовое значение не соответствует необходимому промежутку времени. Введите заново значение")
        template_message_info['need_to_delete'].append(prohib_message.message_id)
        return

    new_template = template.replace('❓', user_input, 1)

    await message.delete()
    await message.bot.edit_message_text(chat_id=message.chat.id, message_id=template_message_id, text=new_template, reply_markup=add_keyboard)
    result_data = result_data + [int(user_input)] if question_types_values[question_index] == 'int' else result_data + [user_input]
    history = history + [new_template]
    question_index = question_index + 1
    await state.update_data(history=history, question_index=question_index, template=new_template, result_data=result_data, last_interaction=int(time.time()))
    if not '❓' in new_template:
        if not check_reminder(result_data[1], result_data[2], result_data[3], result_data[4], result_data[5], [result_data[-3], result_data[-2], result_data[-1]]):
            await message.bot.edit_message_text(chat_id=message.chat.id, message_id=template_message_id, text="🚫Упс, введенное вами напоминание прошло", reply_markup=fix_reminder_keyboard)
            history = history[:-3]
            result_data = result_data[:-3]
            question_index = question_index - 3
            await state.update_data(history=history, result_data=result_data, question_index=question_index, template="🚫Упс, введенное вами напоминание прошло")
            return
        if result_data[-3] == result_data[-2] == result_data[-1] == 0:
            await message.bot.edit_message_text(chat_id=message.chat.id, message_id=template_message_id, text="🚫Упс, вы ввели напоминание совпадающее с дедлайном. \n\n⚡️Не думаю, что вы способны выполнять дела со скоростью света)", reply_markup=fix_reminder_keyboard)
            history = history[:-3]
            result_data = result_data[:-3]
            question_index = question_index - 3
            await state.update_data(history=history, result_data=result_data, question_index=question_index, template=None)
            return
        await message.bot.edit_message_text(chat_id=message.chat.id, message_id=template_message_id, text=f'Заполнение анкеты почти завершено\n\nНужно ли добавить еще напоминания к данному дедлайну?', reply_markup=ask_reminders_deadline_keyboard)
        await state.update_data(template=None)


@router.callback_query(F.data == 'restart', StateFilter(FSMAddUserDeadline.filling_deadline_info))
async def process_restart_template_user_deadline(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get('question_index') == 0:
        await callback_query.answer(text='Вы даже не начали добавлять информацию. Зачем обновлять анкету?😐', show_alert=True)
    await callback_query.message.edit_text(text=LEXICON_RU['pattern_add_user_deadline'], reply_markup=add_keyboard)
    await state.update_data(template=LEXICON_RU['pattern_add_user_deadline'], question_index=0, history=[LEXICON_RU['pattern_add_user']], result_data=[], last_interaction=int(time.time()))


@router.callback_query(F.data == 'back', StateFilter(FSMAddUserDeadline.filling_deadline_info))
async def process_back_template_user_deadline(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    history = data.get('history')
    question_index = data.get('question_index') - 1
    history = history[:-1]
    result_data = data.get('result_data')
    selected_subjects = data.get('selected_subjects')
    await state.update_data(question_index=question_index, template=history[-1], history=history, result_data=result_data[:-1], last_interaction=int(time.time()))
    if selected_subjects is None:
        if not '❓' in history[-1]:
            history = history[:-1]
        await state.update_data(history=history, template=history[-1])
        await callback_query.message.edit_text(text=history[-1], reply_markup=add_keyboard)


@router.callback_query(F.data == 'cancel_template', StateFilter(FSMAddUserDeadline.filling_deadline_info))
async def process_cancel_template_user_deadline(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await state.clear()
    await callback_query.answer()


@router.callback_query(F.data == 'yes_reminders_deadline', StateFilter(FSMAddUserDeadline.filling_deadline_info))
async def process_add_reminder_user_deadline(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    history = data.get('history')
    template = history[-1] + '\n> <u>Напоминание</u>:\n   • день: <b>❓</b>\n   • час: <b>❓</b>\n   • минута: <b>❓</b>'
    history = history + [template]
    question_types = data.get('question_types')
    number_of_reminder = (len(question_types) - 9) // 3 + 1
    question_types = question_types | {f'reminder_day{number_of_reminder}': 'int', f'reminder_hour{number_of_reminder}': 'int', f'reminder_minute{number_of_reminder}': 'int'}
    await state.update_data(template=template, history=history, question_types=question_types, last_interaction=int(time.time()))
    await callback_query.message.edit_text(text=template, reply_markup=add_keyboard)


@router.callback_query(F.data == 'no_reminders_deadline', StateFilter(FSMAddUserDeadline.filling_deadline_info))
async def process_stop_filling_user_deadline(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    result_data = data.get('result_data')
    if not check_minute(result_data[2], result_data[3], result_data[4], result_data[5], result_data[6]):
        await callback_query.message.edit_text(text='🫠Упс, видимо пока вы заполняли анкету, дедлайн <i><b>истек</b></i>(\n\nЗаполнение дедлайна отменено')
        await state.clear()
        return
    reminder_list = sorted([result_data[6+i:6+i+3] for i in range(0, len(result_data) - 8, 3)])
    for index, reminder in enumerate(reminder_list):
        if not check_reminder(result_data[1], result_data[2], result_data[3], result_data[4], result_data[5], [reminder[-3], reminder[-2], reminder[-1]]):
            history = data.get('history')[:7]
            question_index = data.get('question_index')
            result_data = data.get('result_data')
            new_template = history[6]
            for j in range(index):
                history += [new_template + f'> <u>Напоминание</u>:\n   • день: <b>❓</b>\n   • час: <b>❓</b>\n   • минута: <b>❓</b>', new_template + f'\n> <u>Напоминание</u>:\n   • день: <b>{reminder_list[j][0]}</b>\n   • час: <b>❓</b>\n   • минута: <b>❓</b>', new_template + f'\n> <u>Напоминание</u>:\n   • день: <b>{reminder_list[j][0]}</b>\n   • час: <b>{reminder_list[j][1]}</b>\n   • минута: <b>❓</b>', new_template + f'\n> <u>Напоминание</u>:\n   • день: <b>{reminder_list[j][0]}</b>\n   • час: <b>{reminder_list[j][1]}</b>\n   • минута: <b>{reminder_list[j][2]}</b>']
                new_template = new_template + f'\n> <u>Напоминание</u>:\n   • день: <b>{reminder_list[j][0]}</b>\n   • час: <b>{reminder_list[j][1]}</b>\n   • минута: <b>{reminder_list[j][2]}</b>'
            new_template += '\n> <u>Напоминание</u>:\n   • день: <b>❓</b>\n   • час: <b>❓</b>\n   • минута: <b>❓</b>'
            history = history + [new_template]
            result_data = result_data[:7]
            for part in reminder_list[:index]:
                result_data.extend(part)
            await state.update_data(template=None, history=history, question_index=question_index-((len(reminder_list) - index)*3), result_data=result_data, last_interaction=int(time.time()))
            await callback_query.message.edit_text(text='🫠Упс, видимо пока вы заполняли анкету, некоторые напоминания <i><b>истекли</b></i>(', reply_markup=fix_reminder_keyboard)
            return
    template_message_info['need_to_delete'] = []
    await callback_query.message.edit_text(text=f'✅Заполнение анкеты добавления своего дедлайна <u><b>завершено</b></u>!')
    result_dict = {}
    for key, value in zip(data.get('question_types').keys(), result_data):
        result_dict[key] = value
    await add_user_deadline_base(callback_query.message.chat.id, result_dict)
    await state.clear()


@router.callback_query(F.data == 'continue_adding', StateFilter(FSMAddUserDeadline.filling_deadline_info))
async def process_continue_filling_button(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    history = data.get('history')
    result_data = data.get('result_data')
    question_index = data.get('question_index')
    await state.update_data(template=history[-1])
    await callback_query.message.edit_text(text=history[-1], reply_markup=add_keyboard)
    if '❓' not in history[-1]:
        if not check_reminder(result_data[2], result_data[3], result_data[4], result_data[5], result_data[6], [result_data[-3], result_data[-2], result_data[-1]]):
            await callback_query.message.edit_text(text="🚫Упс, введенное вами напоминание прошло", reply_markup=fix_reminder_keyboard)
            history = history[:-3]
            result_data = result_data[:-3]
            question_index = question_index - 3
            await state.update_data(history=history, result_data=result_data, question_index=question_index, template=None)
            return
        if result_data[-3] == result_data[-2] == result_data[-1] == 0:
            await callback_query.message.edit_text(text="🚫Упс, вы ввели напоминание совпадающее с дедлайном. \n\n⚡️Не думаю, что вы способны выполнять дела со скоростью света)", reply_markup=fix_reminder_keyboard)
            history = history[:-3]
            result_data = result_data[:-3]
            question_index = question_index - 3
            await state.update_data(history=history, result_data=result_data, question_index=question_index, template=None)
            return
        await state.update_data(template=None)
        await callback_query.message.edit_text(text=f'Заполнение анкеты почти завершено\n\nНужно ли добавить еще напоминания к данному дедлайну?', reply_markup=ask_reminders_deadline_keyboard)
    await state.update_data(template_id=callback_query.message.message_id, last_interaction=int(time.time()))
    template_message_info['need_to_delete'] = []
    await callback_query.answer()


@router.callback_query(F.data == 'fix_reminder', StateFilter(FSMAddUserDeadline.filling_deadline_info))
async def process_fix_reminder_button(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    history = data.get('history')
    await state.update_data(last_interaction=int(time.time()), template=history[-1])
    await callback_query.message.edit_text(text=history[-1], reply_markup=add_keyboard)


# ---------------MANAGING DEADLINES---------------


@router.message(F.text == '📚ДЕДЛАЙНЫ ПО ПРЕДМЕТАМ📚', StateFilter(default_state))
async def process_show_subjects_deadlines(message: Message):
    user_data = await get_user(message.chat.id)
    if user_data['subject_names']:
        await message.answer("📚<b>ДЕДЛАЙНЫ ПО ПРЕДМЕТАМ</b>📚\n\nВыберите предмет", reply_markup=generate_subjects_deadlines(user_data['subject_names']))
    else:
        await message.answer("📚<b>ДЕДЛАЙНЫ ПО ПРЕДМЕТАМ</b>📚\n\nВы не выбрали ни единого предмета😧")


@router.message(F.text == '⏳БЛИЖАЙШИЕ ДЕДЛАЙНЫ⏳', StateFilter(default_state))
async def process_nearest_deadlines_command(message: Message):
    datetime_now = datetime.now() + timedelta(hours=3)
    nearest_list_deadlines = await get_deadlines(message.chat.id)
    imp_index = 3
    while imp_index < len(nearest_list_deadlines) and nearest_list_deadlines[imp_index-1]['deadline'] == nearest_list_deadlines[imp_index]['deadline']:
        imp_index += 1
    list_of_deadlines = []
    for deadline in nearest_list_deadlines[:imp_index]:
        if deadline['type']:
            list_of_deadlines.append(f"<b><a href='{LEXICON_RU['courses_linkers'][deadline['subject']]['course']}'>{deadline['subject']}</a></b>: {deadline['title']} -> <b>{deadline['deadline'].strftime('%d.%m.%y')}</b>\n<i>Осталось</i>: <u>{translate_to_date(deadline['deadline'] - datetime_now)}</u>\n<a href='{LEXICON_RU['courses_linkers'][deadline['subject']]['answers']}'>ОТВЕТЫ НА КУРС</a>")
        else:
            list_of_deadlines.append(f"{deadline['title']} -> <b>{deadline['deadline'].strftime('%d.%m.%y')}</b>\n<i>Осталось</i>: <u>{translate_to_date(deadline['deadline'] - datetime_now)}</u>")
    return_deadlines = "\n\n".join([f"{ind}) {description}" for ind, description in enumerate(list_of_deadlines, 1)])
    if return_deadlines:
        return_text = f'<b>⏳БЛИЖАЙШИЕ ДЕДЛАЙНЫ⏳</b>\n\n{return_deadlines}'
        return_text += '\n\n...' if imp_index < len(nearest_list_deadlines) else ''
        await message.answer(return_text, reply_markup=functions_keyboard, disable_web_page_preview=True)
    else:
        return_text = f'<b>⏳БЛИЖАЙШИЕ ДЕДЛАЙНЫ⏳</b>\n\nУ вас нет дедлайнов😧'
        await message.answer(return_text, reply_markup=functions_keyboard)


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
    subject_deadlines = await get_subject_deadlines("Россия: гос. осн. и мировоззрение")
    all_deadlines = '\n'.join([f"{index}) {deadline['title']} -> <b>{deadline['deadline'].strftime('%d.%m.%y')}</b>\nОсталось: <u>{translate_to_date(deadline['deadline'] - current_time)}</u>\n" for index, deadline in enumerate(subject_deadlines, 1)])
    await callback.message.edit_text(text=LEXICON_RU['russia_description'].format(all_deadlines), reply_markup=russia_keyboard)


@router.callback_query(F.data == 'cancel', StateFilter(default_state))
async def process_cancel_press(callback: CallbackQuery):
    user_data = await get_user(callback.message.chat.id)
    await callback.message.edit_text(text="📚<b>ДЕДЛАЙНЫ ПО ПРЕДМЕТАМ</b>📚\n\nВыберите предмет", reply_markup=generate_subjects_deadlines(user_data['subject_names']))


@router.callback_query(F.data.endswith('already_done'), StateFilter(default_state))
async def process_already_done_button(callback_query: CallbackQuery):
    deadline_data = await get_deadline(int(callback_query.data[:-12]))
    if not deadline_data:
        await callback_query.answer(text='Дедлайн истек, так что меня не особо волнует сделал ты задание или нет🙃', show_alert=True)
        await callback_query.message.delete()
        return
    if deadline_data['is_subject']:
        await delete_completed_task(deadline_data['title'], callback_query.message.chat.id, deadline_data['reminders'], deadline_data['subject_name'])
    else:
        await delete_completed_task(deadline_data['title'], callback_query.message.chat.id, deadline_data['reminders'])
    await callback_query.message.delete()


@router.message(F.text == '👑СВОИ ДЕДЛАЙНЫ👑', StateFilter(default_state))
async def process_display_user_deadlines(message: Message):
    deadlines = await get_user_deadlines(message.chat.id)
    if deadlines:
        await message.answer(f'👑<b>СВОИ ДЕДЛАЙНЫ</b>👑', reply_markup=generate_user_deadlines(deadlines))
    else:
        await message.answer(f'👑<b>СВОИ ДЕДЛАЙНЫ</b>👑\n\nУ вас нет дедлайнов😧')


@router.callback_query(F.data.endswith('us_dead'), StateFilter(default_state))
async def process_display_description_user_deadline(callback_query: CallbackQuery):
    deadlines = await get_user_deadlines(callback_query.message.chat.id)
    if keyboard2list(callback_query.message.reply_markup) != keyboard2list(generate_user_deadlines(deadlines)):
        await callback_query.answer(text='Сообщение устарело(\nНе будь консерватором, воспользуйся новой функцией😘', show_alert=True)
        return
    index_of_deadline = int(callback_query.data[:-7])
    needed_deadline = await get_deadline(index_of_deadline)
    await callback_query.message.edit_text(f'✨<b>ВАШ ДЕДЛАЙН</b>✨\n\n📝 <b>{needed_deadline["title"]}</b>\n📅 <b>{needed_deadline["date"].strftime("%Y.%m.%d %H:%M:%S")}</b>\n🔔 <b>{", ".join([translate_to_date(timedelta(seconds=reminder)).lower() for reminder in needed_deadline["reminders"]])}</b>', reply_markup=generate_manage_user_deadline(index_of_deadline))


@router.callback_query(F.data.endswith('us_dead_del'), StateFilter(default_state))
async def process_delete_user_deadline(callback_query: CallbackQuery):
    index_of_deadline = int(callback_query.data[:-11])
    if not await get_deadline(index_of_deadline):
        await callback_query.answer(text='Дедлайна не существует(\nА ты - да, наслаждайся моментом✨', show_alert=True)
        return
    await delete_user_deadline(callback_query.message.chat.id, index_of_deadline)
    await callback_query.answer(text='✅Ваш дедлайн успешно удален', show_alert=True)
    new_deadlines = await get_user_deadlines(callback_query.message.chat.id)
    if new_deadlines:
        await callback_query.message.edit_text(f'👑<b>СВОИ ДЕДЛАЙНЫ</b>👑', reply_markup=generate_user_deadlines(new_deadlines))
    else:
        await callback_query.message.edit_text(f'👑<b>СВОИ ДЕДЛАЙНЫ</b>👑\n\nУ вас нет дедлайнов😧')


@router.callback_query(F.data == 'us_dead_back', StateFilter(default_state))
async def process_back_user_deadline(callback_query: CallbackQuery):
    deadlines = await get_user_deadlines(callback_query.message.chat.id)
    if deadlines:
        await callback_query.message.edit_text(f'👑<b>СВОИ ДЕДЛАЙНЫ</b>👑', reply_markup=generate_user_deadlines(deadlines))
    else:
        await callback_query.message.edit_text(f'👑<b>СВОИ ДЕДЛАЙНЫ</b>👑\n\nУ вас нет дедлайнов😧')


@router.message(F.text == '🐵АККАУНТ🐵', StateFilter(default_state))
async def process_display_account(message: Message):
    user = await get_user(message.chat.id)
    deadlines = await get_user_deadlines(message.chat.id)
    courses = "\n".join([f"{index}) <a href='{LEXICON_RU['courses_linkers'][subject]['course']}'>{subject}</a>" for index, subject in enumerate(user["subject_names"], 1)])
    await message.answer(text=f'🐵<b>АККАУНТ</b>🐵\n\n    👤 <b>{user["fullname"]}</b>\n\n📚 <b><u>Ваши курсы:</u></b>\n{courses}\n📊 <b><u>Количество ваших дедлайнов:</u></b> {len(deadlines)}', reply_markup=change_subjects_keyboard)


@router.callback_query(F.data == 'change_subjects', StateFilter(default_state))
async def process_change_subjects(callback_query: CallbackQuery, state: FSMContext):
    current_subjects = (await get_user(callback_query.message.chat.id))['subject_names']
    await state.set_state(FSMRegistrationUser.waiting_for_subjects)
    subjects_data = []
    for subject_name in current_subjects:
        subjects_data.append(('pe_choice', 'economics_choice', 'russia_choice', 'digital_choice', 'english_choice')[['Физическая культура', 'Экономическая культура', 'Россия: гос. осн. и мировоззрение', 'Цифровая грамотность', 'Английский язык'].index(subject_name)])
    await callback_query.message.edit_text(text='📚Выберите предметы, по которым вы хотите получать напоминания о дедлайнах', reply_markup=generate_choice_subjects(subjects_data))
    await state.update_data(selected_subjects=subjects_data, message_id=callback_query.message.message_id, last_interaction=int(time.time()))
    await callback_query.answer()
    await auto_delete_message(callback_query.message.bot, callback_query.message.chat.id, callback_query.message.message_id, state, 300)
