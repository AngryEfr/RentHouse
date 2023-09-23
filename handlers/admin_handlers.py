from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, CommandStart
from aiogram.types.web_app_info import WebAppInfo

from filters.is_admin import IsAdmin
from lexicon.lexicon_ru import LEXICON

router = Router()
router.message.filter(IsAdmin())


# Этот хэндлер будет реагировать на любые сообщения пользователя,
# не предусмотренные логикой работы бота
@router.message(CommandStart())
async def process_start_admin_command(message: Message):
    await message.answer(text=LEXICON['/start_admin'])


@router.message(Command(commands='help'))
async def process_help_admin_command(message: Message):
    await message.answer(text=LEXICON['/help_admin'])


@router.message(Command(commands='booking'))
async def process_help_admin_command(message: Message):
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Перейти к бронированию',
                                                           web_app=WebAppInfo(url='/index.html'))]],
                                 resize_keyboard=True)
    await message.answer(text=LEXICON['/booking'], reply_markup=markup)
