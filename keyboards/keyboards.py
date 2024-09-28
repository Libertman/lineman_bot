from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


# ---------------BUTTONS---------------

# COMMON BUTTONS

# main buttons
nearest_button = KeyboardButton(text='БЛИЖАЙШИЕ ДЕДЛАЙНЫ')
subjects_button = KeyboardButton(text='ДЕДЛАЙНЫ ПО ПРЕДМЕТАМ')
help_button = KeyboardButton(text='Помощь')
authors_button = KeyboardButton(text='Создатели')

# subject buttons
pe_button = KeyboardButton(text='⚽️Физическая культура⚽️')
economics_button = KeyboardButton(text='🤑Экономическая культура🤑')
russia_button = KeyboardButton(text='🇷🇺Россия: гос. основание и мировоззрение🇷🇺')
digital_button = KeyboardButton(text='💻Цифровая грамотность💻')
english_button = KeyboardButton(text='🇺🇸Английский язык🇺🇸')

# help button
help_start_button = KeyboardButton(text='ПОМОГИТЕ')

# INLINE BUTTONS

# url courses buttons
pe_course = InlineKeyboardButton(text='КУРС ПО ФИЗИЧЕСКОЙ КУЛЬТУРЕ', url="https://openedu.ru/course/spbstu/PHYSCUL/?session=fall_2024")
economics_course = InlineKeyboardButton(text='КУРС ПО ЭКОНОМ. КУЛЬТУРЕ', url="https://openedu.ru/course/spbstu/ECONCULT/?session=fall_2024")
russia_course = InlineKeyboardButton(text='КУРС ПО РОССИИ', url="https://openedu.ru/course/spbstu/ORG/?session=fall_2024")
digital_course = InlineKeyboardButton(text='КУРС ПО ЦИФРОВОЙ ГРАМОТНОСТИ', url="https://openedu.ru/course/spbstu/DIGLIT/?session=fall_2024")
english_course = InlineKeyboardButton(text='КУРС ПО АНГЛИЙСКОМУ', url="https://dl-hum.spbstu.ru/course/view.php?id=11111")

# url answers buttons
pe_answer = InlineKeyboardButton(text='ОТВЕТЫ НА КУРС', url='https://polyphis.ru/physical_education')
economics_answer = InlineKeyboardButton(text='ОТВЕТЫ НА КУРС', url='https://polyphis.ru/economic')
russia_answer = InlineKeyboardButton(text='ОТВЕТЫ НА КУРС', url='https://vk.com/topic-192577485_49440811')
digital_answer = InlineKeyboardButton(text='ОТВЕТЫ НА КУРС', url='https://polyphis.ru/digital_literacy')
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

# subject keyboard
subjects_keyboard = ReplyKeyboardMarkup(
    keyboard=[[pe_button],
              [economics_button],
              [russia_button],
              [digital_button],
              [english_button]],
    resize_keyboard=True
)

# INLINE KEYBOARDS

# pe keyboard
pe_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[pe_course],
                     [pe_answer]]
)

# economics keyboard
economics_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[economics_course],
                     [economics_answer]]
)

# russia keyboard
russia_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[russia_course],
                     [russia_answer]]
)

# digital keyboard
digital_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[digital_course],
                     [digital_answer]]
)

# english keyboard
english_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[english_course],
                     [english_answer]]
)