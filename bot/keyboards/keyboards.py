from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from lexicon.lexicon_ru import LEXICON_RU


# ---------------BUTTONS---------------


# COMMON BUTTONS

# main buttons
nearest_button = KeyboardButton(text='⏳БЛИЖАЙШИЕ ДЕДЛАЙНЫ⏳')
subjects_button = KeyboardButton(text='📚ДЕДЛАЙНЫ ПО ПРЕДМЕТАМ📚')
help_button = KeyboardButton(text='⚙️Помощь⚙️')
authors_button = KeyboardButton(text='👨🏻‍💻Создатели👨🏻‍💻')

# help button
help_start_button = KeyboardButton(text='🙏🏻ПОМОГИТЕ🙏🏻')

# INLINE BUTTONS

# cancel button
cancel_button = InlineKeyboardButton(text='⬅️НАЗАД', callback_data='cancel')

# subject buttons
pe_button = InlineKeyboardButton(text='⚽️Физическая культура⚽️', callback_data='pe')
economics_button = InlineKeyboardButton(text='🤑Экономическая культура🤑', callback_data='economics')
russia_button = InlineKeyboardButton(text='🇷🇺Россия: гос. осн. и мировоззрение🇷🇺', callback_data='russia')
digital_button = InlineKeyboardButton(text='💻Цифровая грамотность💻', callback_data='digital')
english_button = InlineKeyboardButton(text='🇺🇸Английский язык🇺🇸', callback_data='english')

# url courses buttons
pe_course = InlineKeyboardButton(text='КУРС ПО ФИЗИЧЕСКОЙ КУЛЬТУРЕ', url=LEXICON_RU['courses_linkers']['Физическая культура']['course'])
economics_course = InlineKeyboardButton(text='КУРС ПО ЭКОНОМ. КУЛЬТУРЕ', url=LEXICON_RU['courses_linkers']['Экономическая культура']['course'])
russia_course = InlineKeyboardButton(text='КУРС ПО РОССИИ', url=LEXICON_RU['courses_linkers']['Россия: гос. осн. и мировоззрение']['course'])
digital_course = InlineKeyboardButton(text='КУРС ПО ЦИФРОВОЙ ГРАМОТНОСТИ', url=LEXICON_RU['courses_linkers']['Цифровая грамотность']['course'])
english_course = InlineKeyboardButton(text='КУРС ПО АНГЛИЙСКОМУ', url=LEXICON_RU['courses_linkers']['Английский язык']['course'])

# url answers buttons
pe_answer = InlineKeyboardButton(text='ОТВЕТЫ НА КУРС', url=LEXICON_RU['courses_linkers']['Физическая культура']['answers'])
economics_answer = InlineKeyboardButton(text='ОТВЕТЫ НА КУРС', url=LEXICON_RU['courses_linkers']['Экономическая культура']['answers'])
russia_answer = InlineKeyboardButton(text='ОТВЕТЫ НА КУРС', url=LEXICON_RU['courses_linkers']['Россия: гос. осн. и мировоззрение']['answers'])
digital_answer = InlineKeyboardButton(text='ОТВЕТЫ НА КУРС', url=LEXICON_RU['courses_linkers']['Цифровая грамотность']['answers'])
english_answer = InlineKeyboardButton(text='ОТВЕТЫ НА КУРС', url=LEXICON_RU['courses_linkers']['Английский язык']['answers'])

# change adding deadline
restart_template = InlineKeyboardButton(text='🔄Сбросить🔄', callback_data='restart')
back_template = InlineKeyboardButton(text='↩️Вернуть↩️', callback_data='back')

# cancel template
cancel_template = InlineKeyboardButton(text='❌Отменить заполнение❌', callback_data='cancel_template')

# adding new deadline reminders
yes_reminders_deadline = InlineKeyboardButton(text='✅ ДА ✅', callback_data='yes_reminders_deadline')
no_reminders_deadline = InlineKeyboardButton(text='❌ НЕТ ❌', callback_data='no_reminders_deadline')

# adding new user reminders
yes_reminders_user = InlineKeyboardButton(text='✅ ДА ✅', callback_data='yes_reminders_user')
no_reminders_user = InlineKeyboardButton(text='❌ НЕТ ❌', callback_data='no_reminders_user')

# check stop adding
continue_adding = InlineKeyboardButton(text='✅ ДА ✅', callback_data='continue_adding')

# fix reminder
fix_reminder = InlineKeyboardButton(text='🔧ИЗМЕНИТЬ НАПОМИНАНИЕ🔧', callback_data='fix_reminder')

# select subject for add deadline
pe_add = InlineKeyboardButton(text='Физическая культура', callback_data='pe_add')
economics_add = InlineKeyboardButton(text='Экономическая культура', callback_data='economics_add')
russia_add = InlineKeyboardButton(text='Россия: гос. осн. и мировоззрение', callback_data='russia_add')
digital_add = InlineKeyboardButton(text='Цифровая грамотность', callback_data='digital_add')
english_add  = InlineKeyboardButton(text='Английский язык', callback_data='english_add')

# check user have already done his task
already_done_task = InlineKeyboardButton(text='✅УЖЕ СДЕЛАЛ✅', callback_data='already_done')


# ---------------KEYBOARDS---------------


# COMMON KEYBOARDS

functions_keyboard = ReplyKeyboardMarkup(
    keyboard=[[nearest_button],
              [subjects_button],
              [help_button, authors_button]],
    resize_keyboard=True
)

help_start_keyboard = ReplyKeyboardMarkup(
    keyboard=[[help_start_button]],
)

# INLINE KEYBOARDS

subjects_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[pe_button],
              [economics_button],
              [russia_button],
              [digital_button],
              [english_button]],
)

pe_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[pe_course],
                     [pe_answer],
                     [cancel_button]]
)

economics_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[economics_course],
                     [economics_answer],
                     [cancel_button]]
)

russia_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[russia_course],
                     [russia_answer],
                     [cancel_button]]
)

digital_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[digital_course],
                     [digital_answer],
                     [cancel_button]]
)

english_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[english_course],
                     [english_answer],
                     [cancel_button]]
)

add_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[restart_template, back_template],
                     [cancel_template]]
)

ask_reminders_deadline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[yes_reminders_deadline, no_reminders_deadline]]
)

ask_reminders_user_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[yes_reminders_user, no_reminders_user]]
)

check_continue_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[continue_adding],
                     [cancel_template]]
)

fix_reminder_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[fix_reminder]]
)

add_subject_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[pe_add],
                     [economics_add],
                     [russia_add],
                     [digital_add],
                     [english_add],
                     [cancel_template]]
)

check_already_done = InlineKeyboardMarkup(
    inline_keyboard=[[already_done_task]]
)


def generate_choice_subjects(subjects: list, selected_subjects: list):
    callback_subjects = ['pe_choice', 'economics_choice', 'russia_choice', 'digital_choice', 'english_choice']
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=f'✅{subject}✅' if callback_subject in selected_subjects else subject, callback_data=callback_subject)] for subject, callback_subject in zip(subjects, callback_subjects)] + [[InlineKeyboardButton(text='• ПОДТВЕРДИТЬ •', callback_data='confirm_choice_subjects')], [cancel_template]]
    )