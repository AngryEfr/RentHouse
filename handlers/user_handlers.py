from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, CommandStart
from aiogram.types.web_app_info import WebAppInfo
from json import loads

from database.db_quick_commands import register_user

from lexicon.lexicon_ru import LEXICON


router = Router()


# Хэндлер команды /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    register_user(message, False)
    await message.answer(text=LEXICON['/start'])


# Хэндлер команды /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON['/help'])


# Хэндлер команды /booking - Ссылка для работы с web_app
@router.message(Command(commands='booking'))
async def process_help_admin_command(message: Message):
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Перейти к бронированию',
                                                           web_app=WebAppInfo(url='https://stepik.org'))]],
                                 resize_keyboard=True)
    await message.answer(text=LEXICON['/booking'], reply_markup=markup)


# Хэндлер работы с информацией от web_app
@router.message(F.content_type == 'web_app_data')
async def web_app(message: Message):
    res = loads(message.web_app_data.data)
    await message.answer(f'Name: {res["name"]}\nPhone: {res["phone"]}\n')


@router.message(F.content_type == 'photo')
async def web_app(message: Message):
    await message.answer(text='Интересное фото :)')
