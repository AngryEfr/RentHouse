from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command, CommandStart
from aiogram.types.web_app_info import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from json import loads

from database.db_quick_commands import register_user, get_active_house, get_user_bookings
from config_data.config import Config, load_config
from keyboards.menu_buttons import create_main_menu, create_info_menu

from lexicon.lexicon_ru import LEXICON, LEXICON_BUTTONS


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


# @router.message(Command(commands='test'))
# async def process_help_command(message: Message):
#     await message.answer(text=LEXICON['/test'])
#     for i in config.tg_bot.admin_ids:
#         await bot.send_message(chat_id=i, text='Тестовое сообщение')


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


@router.callback_query(F.data == 'show_my_bookings')
async def get_bookings_list(callback: CallbackQuery):
    i = 0
    bookings = get_user_bookings(callback.from_user.id)
    if bookings:
        result = bookings[i]
        kb_builder = InlineKeyboardBuilder()
        if len(bookings) > i:
            button1 = InlineKeyboardButton(text=LEXICON_BUTTONS['next'], callback_data=str(i + 1))
            kb_builder.add(button1)
        kb_builder.row(InlineKeyboardButton(text='На главную', callback_data='menu'), width=1)
        await callback.message.edit_text(
            text=f'Бронь №{result[0]}\nID пользователя {result[2]}\nДом №{result[1]}\nДата брони: {result[3]}\n'
                 f'Дата заселения: {result[4]}\nОплата: {result[6]}\nПодтверждение: {result[7]}\n'
                 f'Количество дней: {result[8]}',
            reply_markup=kb_builder.as_markup()
        )
    else:
        await callback.message.answer('Вы еще не бронировали.')


@router.callback_query(F.data.isdigit())
async def get_bookings_list(callback: CallbackQuery):
    i = int(callback.data)
    bookings = get_user_bookings(callback.from_user.id)
    if bookings:
        result = bookings[i]
        kb_builder = InlineKeyboardBuilder()
        if i > 0:
            button2 = InlineKeyboardButton(text=LEXICON_BUTTONS['perv'], callback_data=str(i - 1))
            kb_builder.add(button2)
        if len(bookings) > i + 1:
            button1 = InlineKeyboardButton(text=LEXICON_BUTTONS['next'], callback_data=str(i + 1))
            kb_builder.add(button1)
        kb_builder.row(InlineKeyboardButton(text='На главную', callback_data='menu'), width=1)
        await callback.message.edit_text(
            text=f'Бронь №{result[0]}\nID пользователя {result[2]}\nДом №{result[1]}\nДата брони: {result[3]}\n'
                 f'Дата заселения: {result[4]}\nОплата: {result[6]}\nПодтверждение: {result[7]}\n'
                 f'Количество дней: {result[8]}',
            reply_markup=kb_builder.as_markup()
        )
    else:
        await callback.message.answer('Вы еще не бронировали')
