from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.exceptions import TelegramBadRequest
from lexicon.lexicon_ru import LEXICON_RU
from config_data.config import settings
from keyboards.keyboards import add_keyboard, ask_reminders_deadline_keyboard, check_continue_keyboard, fix_reminder_keyboard, add_subject_keyboard, generate_choice_subjects
from states.states import FSMAdminAddDeadline, FSMAdminAddUser
from database.sql import add_subject_deadline_base, add_user_base
from string import ascii_letters
from services.services import check_year, check_month, check_day, check_hour, check_minute, check_reminder, auto_delete_message
import logging
import time


admin_router = Router()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='{filename}:{lineno} #{levelname:8} '
                        '[{asctime}] - {name} - {message}', style='{')


admin_ids = list(map(int, settings.ADMIN_IDS.split(', ')))
template_message_info = {'need_to_delete': [], 'subjects': ['Физическая культура', 'Экономическая культура', 'Россия: гос. осн. и мировоззрение', 'Цифровая грамотность', 'Английский язык']}


# --------------------- ADD DEADLINE BY ADMIN ---------------------


@admin_router.message(F.from_user.id.in_(admin_ids), or_f(Command(commands='add_deadline'), Command(commands='add_user')), StateFilter(FSMAdminAddDeadline.filling_deadline_info))
async def process_fake_deadline_start(message: Message, state: FSMContext):
    data = await state.get_data()
    bot_message = await message.answer('❗️Вы <b><u>не завершили</u></b> прошлое заполнение нового дедлайна от имени администратора. Вы хотите продолжить заполнение?', reply_markup=check_continue_keyboard)
    try:
        await bot_message.bot.delete_message(chat_id=message.from_user.id, message_id=data.get('template_id'))
    except TelegramBadRequest:
        pass
    await state.update_data(template_id=bot_message.message_id, last_interaction=int(time.time()), template='❗️Вы <b><u>не завершили</u></b> прошлое заполнение нового дедлайна от имени администратора. Вы хотите продолжить заполнение?')
    await auto_delete_message(message.bot, message.from_user.id, bot_message.message_id, state, 300)


@admin_router.message(F.from_user.id.in_(admin_ids), Command(commands='add_deadline'), StateFilter(default_state))
async def process_add_deadline_start(message: Message, state: FSMContext):
    template_message = await message.answer('Выберите предмет, для которого нужно добавить дедлайн', reply_markup=add_subject_keyboard)
    question_types = {'subject_name': 'str', 'lesson_name': 'str', 'deadline_year': 'int', 'deadline_month': 'int', 'deadline_day': 'int', 'deadline_hour': 'int', 'deadline_minute': 'int'}
    await state.update_data(template='Выберите предмет, для которого нужно добавить дедлайн', template_id=template_message.message_id, question_types=question_types, question_index=0, history=['Выберите предмет, для которого нужно добавить дедлайн'], result_data=[], last_interaction=int(time.time()))
    await state.set_state(FSMAdminAddDeadline.filling_deadline_info)
    await auto_delete_message(message.bot, message.from_user.id, template_message.message_id, state, 300)


@admin_router.message(F.from_user.id.in_(admin_ids), StateFilter(FSMAdminAddDeadline.filling_deadline_info))
async def process_handle_add_deadline_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    template_message_id = data.get('template_id')
    template = data.get('template')
    if template_message_info['need_to_delete']:
        for m_id in template_message_info['need_to_delete']:
            try:
                await message.bot.delete_message(chat_id=message.from_user.id, message_id=m_id)
            except TelegramBadRequest:
                pass
        template_message_info['need_to_delete'].clear()
    if not data.get('last_interaction'):
        await message.delete()
        bot_message = await message.answer('❗️Вы <b><u>не завершили</u></b> прошлое заполнение нового дедлайна от имени администратора. Вы хотите продолжить заполнение?', reply_markup=check_continue_keyboard)
        await state.update_data(template_id=bot_message.message_id, last_interaction=int(time.time()), template='❗️Вы <b><u>не завершили</u></b> прошлое заполнение нового дедлайна от имени администратора. Вы хотите продолжить заполнение?')
        await auto_delete_message(message.bot, message.from_user.id, bot_message.message_id, state, 300)
        return
    if not template.startswith('<i><b>ДОБАВЛЕНИЕ ДЕДЛАЙНА КУРСА</b> от имени администратора</i>'):
        await message.delete()
        return
    if message.text in ('⏳БЛИЖАЙШИЕ ДЕДЛАЙНЫ⏳', '📚ДЕДЛАЙНЫ ПО ПРЕДМЕТАМ📚', '⚙️Помощь⚙️', '👨🏻‍💻Создатели👨🏻‍💻'):
        await message.delete()
        bot_message = await message.bot.edit_message_text(chat_id=message.from_user.id, message_id=template_message_id, text='❗️Вы <b><u>не завершили</u></b> прошлое заполнение нового дедлайна от имени администратора. Вы хотите продолжить заполнение?', reply_markup=check_continue_keyboard)
        await state.update_data(last_interaction=int(time.time()), template='❗️Вы <b><u>не завершили</u></b> прошлое заполнение от имени администратора. Вы хотите продолжить заполнение?')
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
                                                             (question_types_keys[question_index] == 'deadline_month' and not check_month(result_data[2], int(user_input))) or
                                                             (question_types_keys[question_index] == 'deadline_day' and not check_day(result_data[2], result_data[3], int(user_input))) or
                                                             (question_types_keys[question_index] == 'deadline_hour' and not check_hour(result_data[2], result_data[3], result_data[4], int(user_input))) or
                                                             (question_types_keys[question_index] == 'deadline_minute' and not check_minute(result_data[2], result_data[3], result_data[4], result_data[5], int(user_input))) or
                                                             (question_types_keys[question_index].startswith('reminder_hour') and not check_hour(0, 0, 0, int(user_input), reminder=True)) or
                                                             (question_types_keys[question_index].startswith('reminder_minute') and not check_minute(0, 0, 0, 0, int(user_input), reminder=True))):
        await message.delete()
        prohib_message = await message.answer("🚫Введенное числовое значение не соответствует необходимому промежутку времени. Введите заново значение")
        template_message_info['need_to_delete'].append(prohib_message.message_id)
        return

    new_template = template.replace('❓', user_input, 1)

    await message.delete()
    await message.bot.edit_message_text(chat_id=message.from_user.id, message_id=template_message_id, text=new_template, reply_markup=add_keyboard)
    result_data = result_data + [int(user_input)] if question_types_values[question_index] == 'int' else result_data + [user_input]
    history = history + [new_template]
    question_index = question_index + 1
    await state.update_data(history=history, question_index=question_index, template=new_template, result_data=result_data, last_interaction=int(time.time()))
    if not '❓' in new_template:
        if len(result_data) > 7:
            if not check_reminder(result_data[2], result_data[3], result_data[4], result_data[5], result_data[6], [result_data[-3], result_data[-2], result_data[-1]]):
                await message.bot.edit_message_text(chat_id=message.from_user.id, message_id=template_message_id, text="🚫Упс, введенное вами напоминание прошло", reply_markup=fix_reminder_keyboard)
                history = history[:-3]
                result_data = result_data[:-3]
                question_index = question_index - 3
                await state.update_data(history=history, result_data=result_data, question_index=question_index, template="🚫Упс, введенное вами напоминание прошло")
                return
            if result_data[-3] == result_data[-2] == result_data[-1] == 0:
                await message.bot.edit_message_text(chat_id=message.from_user.id, message_id=template_message_id, text="🚫Упс, вы ввели напоминание совпадающее с дедлайном. \n\n⚡️Не думаю, что вы способны выполнять дела со скоростью света)", reply_markup=fix_reminder_keyboard)
                history = history[:-3]
                result_data = result_data[:-3]
                question_index = question_index - 3
                await state.update_data(history=history, result_data=result_data, question_index=question_index, template="🚫Упс, вы ввели напоминание совпадающее с дедлайном. \n\n⚡️Не думаю, что вы способны выполнять дела со скоростью света)")
                return
            if (result_data[-3] == 0 and result_data[-2] == 6 and result_data[-1] == 0) or (result_data[-3] == 0 and result_data[-2] == 3 and result_data[-1] == 0):
                await message.bot.edit_message_text(chat_id=message.from_user.id, message_id=template_message_id, text="🚫Упс, вы ввели напоминание совпадающее с одним из основных (3 часа, 6 часов)", reply_markup=fix_reminder_keyboard)
                history = history[:-3]
                result_data = result_data[:-3]
                question_index = question_index - 3
                await state.update_data(history=history, result_data=result_data, question_index=question_index, template="🚫Упс, вы ввели напоминание совпадающее с одним из основных (3 часа, 6 часов)")
                return
        await message.bot.edit_message_text(chat_id=message.from_user.id, message_id=template_message_id, text=f'Заполнение анкеты почти завершено\n\nНужно ли добавить напоминания помимо основных (за 3 часа, 6 часов) и добавленных вами к данному дедлайну?', reply_markup=ask_reminders_deadline_keyboard)
        await state.update_data(template='Заполнение анкеты почти завершено\n\nНужно ли добавить напоминания помимо основных (за 3 часа, 6 часов) и добавленных вами к данному дедлайну?')


@admin_router.callback_query(F.from_user.id.in_(admin_ids), F.data == 'restart', or_f(StateFilter(FSMAdminAddDeadline.filling_deadline_info), StateFilter(FSMAdminAddUser.filling_user_info)))
async def process_restart_template_deadline(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get('selected_subjects') is None:
        await callback_query.message.edit_text(text='Выберите предмет, для которого нужно добавить дедлайн', reply_markup=add_subject_keyboard)
        await state.update_data(template='Выберите предмет, для которого нужно добавить дедлайн', question_index=0, history=[LEXICON_RU['pattern_add_deadline']], result_data=[], last_interaction=int(time.time()))
    else:
        await callback_query.message.edit_text(text='Выберите из предложенного списка курсы, по которым пользователь будет получать дедлайны', reply_markup=generate_choice_subjects(template_message_info['subjects'], []))
        await state.update_data(template='Выберите из предложенного списка курсы, по которым пользователь будет получать дедлайны', question_index=0, history=[LEXICON_RU['pattern_add_user']], result_data=[], last_interaction=int(time.time()), selected_subjects=[])


@admin_router.callback_query(F.from_user.id.in_(admin_ids), F.data == 'back', or_f(StateFilter(FSMAdminAddDeadline.filling_deadline_info), StateFilter(FSMAdminAddUser.filling_user_info)))
async def process_back_template_deadline(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    history = data.get('history')
    question_index = data.get('question_index') - 1
    history = history[:-1]
    result_data = data.get('result_data')
    selected_subjects = data.get('selected_subjects')
    await state.update_data(question_index=question_index, template=history[-1], history=history, result_data=result_data[:-1], last_interaction=int(time.time()))
    if selected_subjects is None:
        if question_index == 0:
            await callback_query.message.edit_text(text='Выберите предмет, для которого нужно добавить дедлайн', reply_markup=add_subject_keyboard)
            await state.update_data(template='Выберите предмет, для которого нужно добавить дедлайн')
        else:
            if not '❓' in history[-1]:
                history = history[:-1]
            await state.update_data(history=history, template=history[-1])
            await callback_query.message.edit_text(text=history[-1], reply_markup=add_keyboard)
    else:
        if question_index == 0:
            await callback_query.message.edit_text(text='Выберите из предложенного списка курсы, по которым пользователь будет получать дедлайны', reply_markup=generate_choice_subjects(template_message_info['subjects'], selected_subjects))
            await state.update_data(template='Выберите из предложенного списка курсы, по которым пользователь будет получать дедлайны')
        else:
            await callback_query.message.edit_text(text=history[-1], reply_markup=add_keyboard)


@admin_router.callback_query(F.from_user.id.in_(admin_ids), F.data == 'cancel_template', or_f(StateFilter(FSMAdminAddDeadline.filling_deadline_info), StateFilter(FSMAdminAddUser.filling_user_info)))
async def process_cancel_template_deadline(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await state.clear()
    await callback_query.answer()


@admin_router.callback_query(F.from_user.id.in_(admin_ids), F.data == 'yes_reminders_deadline', StateFilter(FSMAdminAddDeadline.filling_deadline_info))
async def process_add_reminder_deadline(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    history = data.get('history')
    template = history[-1] + '\n> <u>Напоминание (помимо основных)</u>:\n   • день: <b>❓</b>\n   • час: <b>❓</b>\n   • минута: <b>❓</b>'
    history = history + [template]
    question_types = data.get('question_types')
    number_of_reminder = (len(question_types) - 7) // 3 + 1
    question_types = question_types | {f'reminder_day{number_of_reminder}': 'int', f'reminder_hour{number_of_reminder}': 'int', f'reminder_minute{number_of_reminder}': 'int'}
    await state.update_data(template=template, history=history, question_types=question_types, last_interaction=int(time.time()))
    await callback_query.message.edit_text(text=template, reply_markup=add_keyboard)


@admin_router.callback_query(F.from_user.id.in_(admin_ids), F.data == 'no_reminders_deadline', StateFilter(FSMAdminAddDeadline.filling_deadline_info))
async def process_stop_filling_deadline(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    result_data = data.get('result_data')
    if not check_minute(result_data[2], result_data[3], result_data[4], result_data[5], result_data[6]):
        await callback_query.message.edit_text(text='🫠Упс, видимо пока вы заполняли анкету, дедлайн <i><b>истек</b></i>(\n\nЗаполнение дедлайна отменено')
        await state.clear()
        return
    reminder_list = sorted([result_data[7+i:7+i+3] for i in range(0, len(result_data) - 9, 3)])
    for index, reminder in enumerate(reminder_list):
        if not check_reminder(result_data[2], result_data[3], result_data[4], result_data[5], result_data[6], [reminder[-3], reminder[-2], reminder[-1]]):
            history = data.get('history')[:8]
            question_index = data.get('question_index')
            result_data = data.get('result_data')
            new_template = history[7]
            for j in range(index):
                history += [f'> <u>Напоминание (помимо основных)</u>:\n   • день: <b>❓</b>\n   • час: <b>❓</b>\n   • минута: <b>❓</b>', new_template + f'\n> <u>Напоминание (помимо основных)</u>:\n   • день: <b>{reminder_list[j][0]}</b>\n   • час: <b>❓</b>\n   • минута: <b>❓</b>', new_template + f'\n> <u>Напоминание (помимо основных)</u>:\n   • день: <b>{reminder_list[j][0]}</b>\n   • час: <b>{reminder_list[j][1]}</b>\n   • минута: <b>❓</b>', new_template + f'\n> <u>Напоминание (помимо основных)</u>:\n   • день: <b>{reminder_list[j][0]}</b>\n   • час: <b>{reminder_list[j][1]}</b>\n   • минута: <b>{reminder_list[j][2]}</b>']
                new_template = new_template + f'\n> <u>Напоминание (помимо основных)</u>:\n   • день: <b>{reminder_list[j][0]}</b>\n   • час: <b>{reminder_list[j][1]}</b>\n   • минута: <b>{reminder_list[j][2]}</b>'
            new_template += '\n> <u>Напоминание (помимо основных)</u>:\n   • день: <b>❓</b>\n   • час: <b>❓</b>\n   • минута: <b>❓</b>'
            history = history + [new_template]
            result_data = result_data[:7]
            for part in reminder_list[:index]:
                result_data.extend(part)
            await state.update_data(template='🫠Упс, видимо пока вы заполняли анкету, некоторые напоминания <i><b>истекли</b></i>(', history=history, question_index=question_index-((len(reminder_list) - index)*3), result_data=result_data, last_interaction=int(time.time()))
            await callback_query.message.edit_text(text='🫠Упс, видимо пока вы заполняли анкету, некоторые напоминания <i><b>истекли</b></i>(', reply_markup=fix_reminder_keyboard)
            return

    await callback_query.message.edit_text(text=f'✅Заполнение анкеты добавления нового дедлайна курса от имени администратора <b>завершено</b>! Дедлайн добавлен всем пользователям курса')
    result_dict = {}
    for key, value in zip(data.get('question_types').keys(), result_data):
        result_dict[key] = value
    await add_subject_deadline_base(result_dict)
    await state.clear()


@admin_router.callback_query(F.from_user.id.in_(admin_ids), F.data == 'continue_adding', or_f(StateFilter(FSMAdminAddDeadline.filling_deadline_info), StateFilter(FSMAdminAddUser.filling_user_info)))
async def process_continue_filling_button(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    history = data.get('history')
    result_data = data.get('result_data')
    question_index = data.get('question_index')
    if data.get('selected_subjects') is None:
        if question_index == 0:
            await state.update_data(template='Выберите предмет, для которого нужно добавить дедлайн')
            await callback_query.message.edit_text(text='Выберите предмет, для которого нужно добавить дедлайн', reply_markup=add_subject_keyboard)
        else:
            await state.update_data(template=history[-1])
            await callback_query.message.edit_text(text=history[-1], reply_markup=add_keyboard)
        if '❓' not in history[-1]:
            if len(result_data) > 7:
                if not check_reminder(result_data[2], result_data[3], result_data[4], result_data[5], result_data[6], [result_data[-3], result_data[-2], result_data[-1]]):
                    await callback_query.message.edit_text(text="🚫Упс, введенное вами напоминание прошло", reply_markup=fix_reminder_keyboard)
                    history = history[:-3]
                    result_data = result_data[:-3]
                    question_index = question_index - 3
                    await state.update_data(history=history, result_data=result_data, question_index=question_index, template="🚫Упс, введенное вами напоминание прошло")
                    return
                if result_data[-3] == result_data[-2] == result_data[-1] == 0:
                    await callback_query.message.edit_text(text="🚫Упс, вы ввели напоминание совпадающее с дедлайном. \n\n⚡️Не думаю, что вы способны выполнять дела со скоростью света)", reply_markup=fix_reminder_keyboard)
                    history = history[:-3]
                    result_data = result_data[:-3]
                    question_index = question_index - 3
                    await state.update_data(history=history, result_data=result_data, question_index=question_index, template="🚫Упс, вы ввели напоминание совпадающее с дедлайном. \n\n⚡️Не думаю, что вы способны выполнять дела со скоростью света)")
                    return
                if (result_data[-3] == 0 and result_data[-2] == 6 and result_data[-1] == 0) or (result_data[-3] == 0 and result_data[-2] == 3 and result_data[-1] == 0):
                    await callback_query.message.edit_text(text="🚫Упс, вы ввели напоминание совпадающее с одним из основных (3 часа, 6 часов)", reply_markup=fix_reminder_keyboard)
                    history = history[:-3]
                    result_data = result_data[:-3]
                    question_index = question_index - 3
                    await state.update_data(history=history, result_data=result_data, question_index=question_index, template="🚫Упс, вы ввели напоминание совпадающее с одним из основных (3 часа, 6 часов)")
                    return
            await state.update_data(template='Заполнение анкеты почти завершено\n\nНужно ли добавить напоминания помимо основных (3 часа, 6 часов) и добавленных вами к данному дедлайну?')
            await callback_query.message.edit_text(text=f'Заполнение анкеты почти завершено\n\nНужно ли добавить напоминания помимо основных (3 часа, 6 часов) и добавленных вами к данному дедлайну?', reply_markup=ask_reminders_deadline_keyboard)
    else:
        if question_index == 0:
            subjects_data = data.get('selected_subjects')
            await state.update_data(template='Выберите из предложенного списка курсы, по которым пользователь будет получать дедлайны')
            await callback_query.message.edit_text(text='Выберите из предложенного списка курсы, по которым пользователь будет получать дедлайны', reply_markup=generate_choice_subjects(template_message_info['subjects'], subjects_data))
        else:
            await state.update_data(template=history[-1])
            await callback_query.message.edit_text(text=history[-1], reply_markup=add_keyboard)
    await state.update_data(template_id=callback_query.message.message_id, last_interaction=int(time.time()))
    template_message_info['need_to_delete'] = []
    await callback_query.answer()


@admin_router.callback_query(F.from_user.id.in_(admin_ids), F.data == 'fix_reminder', StateFilter(FSMAdminAddDeadline.filling_deadline_info))
async def process_fix_reminder_button(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    history = data.get('history')
    await state.update_data(last_interaction=int(time.time()), template=history[-1])
    await callback_query.message.edit_text(text=history[-1], reply_markup=add_keyboard)


@admin_router.callback_query(F.from_user.id.in_(admin_ids), F.data.in_(['pe_add', 'economics_add', 'russia_add', 'digital_add', 'english_add']), StateFilter(FSMAdminAddDeadline.filling_deadline_info))
async def process_subject_name_button(callback_query: CallbackQuery, state: FSMContext):
    calldata = callback_query.data
    result_subject = template_message_info['subjects'][('pe_add', 'economics_add', 'russia_add', 'digital_add', 'english_add').index(calldata)]
    new_template = LEXICON_RU['pattern_add_deadline'].replace('❓', result_subject, 1)
    await state.update_data(template=new_template, history=[LEXICON_RU['pattern_add_deadline']]+[new_template], question_index=1, result_data=[result_subject], last_interaction=int(time.time()))
    await callback_query.message.edit_text(text=new_template, reply_markup=add_keyboard)


# --------------------- ADD USER BY ADMIN ---------------------


@admin_router.message(F.from_user.id.in_(admin_ids), Command(commands='add_user'), StateFilter(default_state))
async def process_start_add_user(message: Message, state: FSMContext):
    template_message = await message.answer('Выберите из предложенного списка курсы, по которым пользователь будет получать дедлайны', reply_markup=generate_choice_subjects(template_message_info['subjects'], []))
    question_types = {'subject_names': 'str', 'id': 'int', 'username': 'str', 'fullname': 'str'}
    await state.update_data(template='Выберите из предложенного списка курсы, по которым пользователь будет получать дедлайны', template_id=template_message.message_id, question_types=question_types, question_index=0, history=[LEXICON_RU['pattern_add_user']], result_data=[], last_interaction=int(time.time()), selected_subjects=[])
    await state.set_state(FSMAdminAddUser.filling_user_info)
    await auto_delete_message(message.bot, message.from_user.id, template_message.message_id, state, 300)


@admin_router.message(F.from_user.id.in_(admin_ids), or_f(Command(commands='add_user'), Command(commands='add_deadline')), StateFilter(FSMAdminAddUser.filling_user_info))
async def process_fake_start_add_user(message: Message, state: FSMContext):
    data = await state.get_data()
    bot_message = await message.answer('❗️Вы <b><u>не завершили</u></b> прошлое заполнение нового пользователя от имени администратора. Вы хотите продолжить заполнение?', reply_markup=check_continue_keyboard)
    try:
        await bot_message.bot.delete_message(chat_id=message.from_user.id, message_id=data.get('template_id'))
    except TelegramBadRequest:
        pass
    await state.update_data(template_id=bot_message.message_id, last_interaction=int(time.time()), template='❗️Вы <b><u>не завершили</u></b> прошлое заполнение нового пользователя от имени администратора. Вы хотите продолжить заполнение?')
    await auto_delete_message(message.bot, message.from_user.id, bot_message.message_id, state, 300)


@admin_router.message(F.from_user.id.in_(admin_ids), StateFilter(FSMAdminAddUser.filling_user_info))
async def process_handle_add_user_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    template_message_id = data.get('template_id')
    template = data.get('template')
    if template_message_info['need_to_delete']:
        for m_id in template_message_info['need_to_delete']:
            try:
                await message.bot.delete_message(chat_id=message.from_user.id, message_id=m_id)
            except TelegramBadRequest:
                pass
        template_message_info['need_to_delete'].clear()
    if not data.get('last_interaction'):
        await message.delete()
        bot_message = await message.answer('❗️Вы <b><u>не завершили</u></b> прошлое заполнение нового пользователя от имени администратора. Вы хотите продолжить заполнение?', reply_markup=check_continue_keyboard)
        await state.update_data(template_id=bot_message.message_id, last_interaction=int(time.time()), template='❗️Вы <b><u>не завершили</u></b> прошлое заполнение нового пользователя от имени администратора. Вы хотите продолжить заполнение?')
        await auto_delete_message(message.bot, message.from_user.id, bot_message.message_id, state, 300)
        return
    if not template.startswith('<i><b>ДОБАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯ</b> от имени администратора</i>'):
        await message.delete()
        return
    if message.text in ('⏳БЛИЖАЙШИЕ ДЕДЛАЙНЫ⏳', '📚ДЕДЛАЙНЫ ПО ПРЕДМЕТАМ📚', '⚙️Помощь⚙️', '👨🏻‍💻Создатели👨🏻‍💻'):
        await message.delete()
        bot_message = await message.bot.edit_message_text(chat_id=message.from_user.id, message_id=template_message_id, text='❗️Вы <b><u>не завершили</u></b> прошлое заполнение нового пользователя от имени администратора. Вы хотите продолжить заполнение?', reply_markup=check_continue_keyboard)
        await state.update_data(last_interaction=int(time.time()), template='❗️Вы <b><u>не завершили</u></b> прошлое заполнение нового пользователя от имени администратора. Вы хотите продолжить заполнение?')
        return

    user_input = message.text
    question_types_values = list(data.get('question_types').values())
    question_index = data.get('question_index')
    history = data.get('history')
    result_data = data.get('result_data')

    if (question_types_values[question_index] == 'int' and not user_input.isdigit()):
        await message.delete()
        prohib_message = await message.answer("🚫Тип введенного значения не соответствует допустимому. Введите заново значение")
        template_message_info['need_to_delete'].append(prohib_message.message_id)
        return

    new_template = template.replace('❓', user_input, 1)

    await message.delete()
    await message.bot.edit_message_text(chat_id=message.from_user.id, message_id=template_message_id, text=new_template, reply_markup=add_keyboard)
    result_data = result_data + [int(user_input)] if question_types_values[question_index] == 'int' else result_data + [user_input]
    await state.update_data(history=history + [new_template], question_index=question_index + 1, template=new_template, result_data=result_data, last_interaction=int(time.time()))
    if not '❓' in new_template:
        await message.bot.edit_message_text(chat_id=message.from_user.id, message_id=template_message_id, text=f'✅Заполнение анкеты добавления нового пользователя <b>завершено</b>! Все нынешние дедлайны курсов, выбранные этим пользователем, добавлены.')
        result_dict = {}
        for key, value in zip(data.get('question_types').keys(), result_data):
            result_dict[key] = value
        await add_user_base(result_dict)
        await state.clear()


@admin_router.callback_query(F.from_user.id.in_(admin_ids), F.data.in_(['pe_choice', 'economics_choice', 'russia_choice', 'digital_choice', 'english_choice']), StateFilter(FSMAdminAddUser.filling_user_info))
async def process_get_subjects_button(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_subjects = data.get("selected_subjects")
    if callback_query.data in selected_subjects:
        selected_subjects.remove(callback_query.data)
    else:
        selected_subjects.append(callback_query.data)

    await state.update_data(selected_subjects=selected_subjects, last_interaction=int(time.time()))
    await callback_query.message.edit_reply_markup(reply_markup=generate_choice_subjects(template_message_info['subjects'], selected_subjects))


@admin_router.callback_query(F.from_user.id.in_(admin_ids), F.data == 'confirm_choice_subjects', StateFilter(FSMAdminAddUser.filling_user_info))
async def process_confirm_subjects_button(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    question_index = data.get('question_index')
    history = data.get('history')
    subjects_data = []
    for subject_callback in data.get('selected_subjects'):
        subjects_data.append(template_message_info['subjects'][('pe_choice', 'economics_choice', 'russia_choice', 'digital_choice', 'english_choice').index(subject_callback)])
    new_template = LEXICON_RU['pattern_add_user'].replace('❓', ';\n'.join(subjects_data) if len(subjects_data) > 0 else 'нет', 1)
    await state.update_data(question_index=question_index+1, history=history + [new_template], template=new_template, result_data=[subjects_data], last_interaction=int(time.time()))
    await callback_query.message.edit_text(text=new_template, reply_markup=add_keyboard)
