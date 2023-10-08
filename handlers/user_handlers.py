from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.types.web_app_info import WebAppInfo
from json import loads

from database.db_quick_commands import register_user, get_active_house
from config_data.config import Config, load_config
from keyboards.menu_buttons import create_main_menu, create_info_menu

from lexicon.lexicon_ru import LEXICON


router = Router()
config: Config = load_config('.env')
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')


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
    for i in config.tg_bot.admin_ids:
        await bot.send_message(chat_id=i, text='Новая бронь!')


@router.message(Command(commands='menu'))
async def process_menu_command(message: Message):
    await message.answer(
        text=LEXICON['menu'],
        reply_markup=create_main_menu('info', 'show_my_bookings')
    )


@router.message(Command(commands='test'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON['/test'])
    for i in config.tg_bot.admin_ids:
        await bot.send_message(chat_id=i, text='Тестовое сообщение')


# Этот хэндлер будет срабатывать на нажатие кнопки "Информация о доме"
@router.callback_query(F.data == 'info')
async def get_info_house(callback: CallbackQuery):
    active_house = get_active_house()
    houses = []
    for i in active_house:
        houses.append(i.name + '/*/*/*' + i.link)
    await callback.message.edit_text(
        text=LEXICON['info_house'],
        reply_markup=create_info_menu(*houses)
    )


# Этот хэндлер будет срабатывать на нажатие кнопки "На главную"
@router.callback_query(F.data == 'menu')
async def process_menu_command(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON['menu'],
        reply_markup=create_main_menu('info', 'show_my_bookings')
    )
