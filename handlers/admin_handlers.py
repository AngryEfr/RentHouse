from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.context import FSMContext
from states.states import FSMFillForm

from database.db_quick_commands import register_user, get_active_house, csv_save, get_bookings

from filters.is_admin import IsAdmin
from keyboards.menu_buttons import create_main_menu, create_info_menu
from lexicon.lexicon_ru import LEXICON, LEXICON_BUTTONS


router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

user_dict = {}


# Хэндлер команды /start для админов
@router.message(CommandStart())
async def process_start_admin_command(message: Message, state: FSMContext):
    register_user(message, True)
    await message.answer(text=LEXICON['/start_admin'])
    await state.clear()


# Хэндлер команды /help для админов
@router.message(Command(commands='help'))
async def process_help_admin_command(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['/help_admin'])
    await state.clear()


@router.callback_query(F.data == 'csv')
async def process_cancel_command(callback: CallbackQuery):
    csv_save()
    file = FSInputFile("mydump.csv")
    await callback.message.reply_document(file)


@router.message(Command(commands='menu'))
async def process_menu_command(message: Message):
    await message.answer(
        text=LEXICON['menu_admin'],
        reply_markup=create_main_menu('info', 'show_my_bookings', 'admins')
    )


# Этот хэндлер будет срабатывать на нажатие кнопки "На главную"
@router.callback_query(F.data == 'menu')
async def process_menu_command(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON['menu_admin'],
        reply_markup=create_main_menu('info', 'show_my_bookings', 'admins')
    )


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


@router.callback_query(F.data == 'admins')
async def process_menu_command(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON['admins'],
        reply_markup=create_main_menu('fillform', 'csv', 'bookings',  'menu')
    )


# Обработка команды bookings
@router.callback_query(F.data == 'bookings')
async def get_bookings_list(callback: CallbackQuery, state: FSMContext):
    i = 0
    bookings = get_bookings()
    if bookings:
        result = bookings[i]
        kb_builder = InlineKeyboardBuilder()
        if len(bookings) > i + 1:
            button1 = InlineKeyboardButton(text=LEXICON_BUTTONS['next'], callback_data=str(i + 1))
            kb_builder.add(button1)
        kb_builder.row(InlineKeyboardButton(text='Выслать реквизиты', callback_data='requisites ' + str(result[2])),
                       width=1)
        kb_builder.row(InlineKeyboardButton(text='Подтвердить', callback_data='confirm ' + str(result[2])), width=1)
        kb_builder.row(InlineKeyboardButton(text='Отменить', callback_data='cancel_book ' + str(result[2])), width=1)
        kb_builder.row(InlineKeyboardButton(text='На главную', callback_data='menu'), width=1)
        await callback.message.edit_text(
            text=f'Бронь №{result[0]}\nID пользователя {result[2]}\nЛогин: @{result[3]}\nДом №{result[1]}\nДата брони: '
                 f'{result[4]}\n'
                 f'Дата заселения: {result[5]}\nТелефон: {result[6]}\nОплата: {result[8]}\nПодтверждение: {result[9]}\n'
                 f'Количество дней: {result[10]}',
            reply_markup=kb_builder.as_markup()
        )
        await state.set_state(FSMFillForm.show_bookings)
    else:
        await callback.message.answer('Пока никто не бронировал.')


@router.callback_query(F.data.isdigit(), StateFilter(FSMFillForm.show_bookings))
async def get_bookings_list(callback: CallbackQuery):
    i = int(callback.data)
    bookings = get_bookings()
    if bookings:
        result = bookings[i]
        kb_builder = InlineKeyboardBuilder()
        if i > 0:
            button2 = InlineKeyboardButton(text=LEXICON_BUTTONS['perv'], callback_data=str(i - 1))
            kb_builder.add(button2)
        if len(bookings) > i + 1:
            button1 = InlineKeyboardButton(text=LEXICON_BUTTONS['next'], callback_data=str(i + 1))
            kb_builder.add(button1)
        kb_builder.row(InlineKeyboardButton(text='Выслать реквизиты', callback_data='requisites ' + str(result[2])),
                       width=1)
        kb_builder.row(InlineKeyboardButton(text='Подтвердить', callback_data='confirm ' + str(result[2])), width=1)
        kb_builder.row(InlineKeyboardButton(text='Отменить', callback_data='cancel_book ' + str(result[2])), width=1)
        kb_builder.row(InlineKeyboardButton(text='На главную', callback_data='menu'), width=1)
        await callback.message.edit_text(
            text=f'Бронь №{result[0]}\nID пользователя {result[2]}\nЛогин: @{result[3]}\nДом №{result[1]}\nДата брони: '
                 f'{result[4]}\n'
                 f'Дата заселения: {result[5]}\nТелефон: {result[6]}\nОплата: {result[8]}\nПодтверждение: {result[9]}\n'
                 f'Количество дней: {result[10]}',
            reply_markup=kb_builder.as_markup()
        )
    else:
        await callback.message.answer('Пока никто не бронировал.')
