from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


# ---------------BUTTONS---------------

# COMMON BUTTONS

# main buttons
nearest_button = KeyboardButton(text='БЛИЖАЙШИЕ ДЕДЛАЙНЫ')
subjects_button = KeyboardButton(text='ДЕДЛАЙНЫ ПО ПРЕДМЕТАМ')
help_button = KeyboardButton(text='Помощь')
authors_button = KeyboardButton(text='Создатели')

# help button
help_start_button = KeyboardButton(text='ПОМОГИТЕ')

# INLINE BUTTONS

# cancel button
cancel_button = InlineKeyboardButton(text='Назад', callback_data='cancel')

# subject buttons
pe_button = InlineKeyboardButton(text='⚽️Физическая культура⚽️', callback_data='pe')
economics_button = InlineKeyboardButton(text='🤑Экономическая культура🤑', callback_data='economics')
russia_button = InlineKeyboardButton(text='🇷🇺Россия: гос. осн. и мировоззрение🇷🇺', callback_data='russia')
digital_button = InlineKeyboardButton(text='💻Цифровая грамотность💻', callback_data='digital')
english_button = InlineKeyboardButton(text='🇺🇸Английский язык🇺🇸', callback_data='english')

# url courses buttons
pe_course = InlineKeyboardButton(text='КУРС ПО ФИЗИЧЕСКОЙ КУЛЬТУРЕ', url="https://openedu.ru/course/spbstu/PHYSCUL/?session=fall_2024")
economics_course = InlineKeyboardButton(text='КУРС ПО ЭКОНОМ. КУЛЬТУРЕ', url="https://openedu.ru/course/spbstu/ECONCULT/?session=fall_2024")
russia_course = InlineKeyboardButton(text='КУРС ПО РОССИИ', url="https://openedu.ru/course/spbstu/ORG/?session=fall_2024")
digital_course = InlineKeyboardButton(text='КУРС ПО ЦИФРОВОЙ ГРАМОТНОСТИ', url="https://openedu.ru/course/spbstu/DIGLIT/?session=fall_2024")
english_course = InlineKeyboardButton(text='КУРС ПО АНГЛИЙСКОМУ', url="https://dl-hum.spbstu.ru/course/view.php?id=11111")

# url answers buttons
pe_answer = InlineKeyboardButton(text='ОТВЕТЫ НА КУРС', url='https://polyvsp.ru/fizra/')
economics_answer = InlineKeyboardButton(text='ОТВЕТЫ НА КУРС', url='https://polyvsp.ru/economkult/')
russia_answer = InlineKeyboardButton(text='ОТВЕТЫ НА КУРС', url='https://vk.com/topic-192577485_49440811')
digital_answer = InlineKeyboardButton(text='ОТВЕТЫ НА КУРС', url='https://polyvsp.ru/cifgram/')
english_answer = InlineKeyboardButton(text='ОТВЕТЫ НА КУРС', url='https://polyphis.ru/english_scr')

# ---------------KEYBOARDS---------------

# COMMON KEYBOARDS

# main keyboard
functions_keyboard = ReplyKeyboardMarkup(
    keyboard=[[nearest_button],
              [subjects_button],
              [help_button, authors_button]],
    resize_keyboard=True
)

# help keyboard
help_start_keyboard = ReplyKeyboardMarkup(
    keyboard=[[help_start_button]],
)

# INLINE KEYBOARDS

# subject keyboard
subjects_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[pe_button],
              [economics_button],
              [russia_button],
              [digital_button],
              [english_button]],
)

# pe keyboard
pe_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[pe_course],
                     [pe_answer],
                     [cancel_button]]
)

# economics keyboard
economics_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[economics_course],
                     [economics_answer],
                     [cancel_button]]
)

# russia keyboard
russia_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[russia_course],
                     [russia_answer],
                     [cancel_button]]
)

# digital keyboard
digital_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[digital_course],
                     [digital_answer],
                     [cancel_button]]
)

# english keyboard
english_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[english_course],
                     [english_answer],
                     [cancel_button]]
)