from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


nearest_button = KeyboardButton(text='БЛИЖАЙШИЕ ДЕДЛАЙНЫ')
subjects_button = KeyboardButton(text='ДЕДЛАЙНЫ ПО ПРЕДМЕТАМ')
help_button = KeyboardButton(text='Помощь')
authors_button = KeyboardButton(text='Создатели')

functions_keyboard = ReplyKeyboardMarkup(
    keyboard=[[nearest_button],
              [subjects_button],
              [help_button, authors_button]],
    resize_keyboard=True,
    one_time_keyboard=True
)

help_start_button = KeyboardButton(text='ПОМОГИТЕ')

help_start_keyboard = ReplyKeyboardMarkup(
    keyboard=[[help_start_button]]
)
