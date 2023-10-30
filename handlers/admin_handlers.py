from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.context import FSMContext
from states.states import FSMFillForm

from config_data.config import Config, load_config
from database.db_quick_commands import register_user, get_active_house, csv_save, get_bookings, send_details_change, \
    check_active_user, change_status_pay, change_status_booking, csv_save_confirmed, get_advert, get_users_id, check_free_date

from filters.is_admin import IsAdmin
from keyboards.menu_buttons import create_main_menu, create_info_menu
from lexicon.lexicon_ru import LEXICON, LEXICON_BUTTONS


router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

config: Config = load_config('.env')
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')


# Хэндлер команды /start для админов
@router.message(CommandStart())
async def process_start_admin_command(message: Message, state: FSMContext):
    register_user(message, True)
    await message.answer(text=LEXICON['/start_admin'])
    await state.clear()


# Хэндлер команды /help для админов
@router.message(Command(commands='help'))
async def process_help_admin_command(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['/help_admin'], disable_web_page_preview=True)
    await state.clear()


@router.message(Command(commands='testadvert'))
async def process_help_admin_command(message: Message, state: FSMContext):

    try:
        if len(message.text) > 12:
            num = message.text[12:]
        else:
            raise Exception("Цифру объявления забыл?")
        if not num.isdigit():
            raise Exception("Только цифру!")
        advert = get_advert(num)
        if not advert:
            raise Exception("Нет такого объявления")

    except Exception as Error:
        await message.answer(text=f'{Error}')
    else:
        await message.answer(text=f'{advert}')
    await state.clear()


@router.message(Command(commands='advert'))
async def process_help_admin_command(message: Message, state: FSMContext):
    try:
        if len(message.text) > 8:
            num = message.text[8:]
        else:
            raise Exception("Цифру объявления забыл?")
        if not num.isdigit():
            raise Exception("Только цифру!")
        users = get_users_id()
        if not users:
            raise Exception("Нет активных участников")
        advert = get_advert(num)
        if not advert:
            raise Exception("Нет такого объявления")

    except Exception as Error:
        await message.answer(text=f'{Error}')
    else:
        for i in users:
            await bot.send_message(chat_id=int(i), text=f'{advert}')
    await state.clear()


@router.callback_query(F.data == 'csv')
async def process_cancel_command(callback: CallbackQuery):
    csv_save()
    file = FSInputFile("mydump.csv")
    await callback.message.reply_document(file)
    await callback.answer()


@router.callback_query(F.data == 'confirmed_bookings')
async def process_cancel_command(callback: CallbackQuery):
    csv_save_confirmed()
    file = FSInputFile("mydump.csv")
    await callback.message.reply_document(file)
    await callback.answer()


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
        reply_markup=create_main_menu('csv', 'bookings', 'confirmed_bookings',  'menu')
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
        kb_builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS['send_details'],
                                            callback_data='send_details'),
                       width=1)
        kb_builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS['confirm_pay'], callback_data='confirm_pay'),
                       width=1)
        kb_builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS['confirm_booking'], callback_data='confirm_booking'),
                       width=1)
        kb_builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS['cancel_booking'], callback_data='cancel_booking'),
                       width=1)
        kb_builder.row(InlineKeyboardButton(text='На главную', callback_data='menu'), width=1)
        await callback.message.edit_text(
            text=f'Бронь №{result[0]}\nID пользователя {result[2]}\nЛогин: @{result[3]}\n'
                 f'Дом №{result[1]}\nДата брони: {result[4]}\nДата заселения: {result[5]}\nТелефон: {result[6]}\n'
                 f'{"Реквизиты отправлены" if result[7] else ("Реквизиты не отправлены"if result[7] is False else "Ожидает реквизиты")}\n'
                 f'{"Оплачено" if result[8] else "Не оплачено"}\n'
                 f'{"Заезд подтвержден" if result[9]else("Заезд отменен" if result[9] is False else "Ожидает подтверждения")}'
                 f'\nЗаезд продлится {result[10]} {"день" if result[10][-1] == "1" else ("дня" if result[10][-1] in ["2", "3", "4"] else "дней")}'
                 f'\nИмя: {result[11]}',
            reply_markup=kb_builder.as_markup()
        )
        await state.set_state(FSMFillForm.show_bookings)
    else:
        await callback.message.answer('Пока никто не бронировал.')
        await callback.answer()


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
        kb_builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS['send_details'],
                                            callback_data='send_details'),
                       width=1)
        kb_builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS['confirm_pay'], callback_data='confirm_pay'),
                       width=1)
        kb_builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS['confirm_booking'], callback_data='confirm_booking'),
                       width=1)
        kb_builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS['cancel_booking'], callback_data='cancel_booking'),
                       width=1)
        kb_builder.row(InlineKeyboardButton(text='На главную', callback_data='menu'), width=1)
        await callback.message.edit_text(
            text=f'Бронь №{result[0]}\nID пользователя {result[2]}\nЛогин: @{result[3]}\n'
                 f'Дом №{result[1]}\nДата брони: {result[4]}\nДата заселения: {result[5]}\nТелефон: {result[6]}\n'
                 f'{"Реквизиты отправлены" if result[7] else ("Реквизиты не отправлены"if result[7] is False else "Ожидает реквизиты")}\n'
                 f'{"Оплачено" if result[8] else "Не оплачено"}\n'
                 f'{"Заезд подтвержден" if result[9]else("Заезд отменен" if result[9] is False else "Ожидает подтверждения")}'
                 f'\nЗаезд продлится {result[10]} {"день" if result[10][-1] == "1" else ("дня" if result[10][-1] in ["2", "3", "4"] else "дней")}'
                 f'\nИмя: {result[11]}',
            reply_markup=kb_builder.as_markup()
        )
    else:
        await callback.message.answer('Пока никто не бронировал.')
        await callback.answer()


@router.callback_query(F.data == 'send_details')
async def process_send_details(callback: CallbackQuery):
    try:
        if not check_active_user(int(callback.message.text.split()[4])):
            raise Exception("Бот заблокирован пользователем.")
        if not send_details_change(callback.message.text.split()[1][1:]):
            raise Exception("Ошибка отправки.")
        if check_free_date(callback.message.text.split()[14]):
            raise Exception("Дата занята!")

    except Exception as Error:
        await callback.answer(f'{Error}', show_alert=True)
    else:
        await bot.send_message(chat_id=int(callback.message.text.split()[4]), text=LEXICON['send_details'], disable_web_page_preview=True)
        await callback.answer('Реквизиты отправлены', show_alert=True)


@router.callback_query(F.data == 'confirm_pay')
async def process_confirm_pay(callback: CallbackQuery):
    try:
        if not change_status_pay(callback.message.text.split()[1][1:]):
            raise Exception("Уже подтверждено!")

    except Exception as Error:
        await callback.answer(f'{Error}', show_alert=True)
    else:
        await bot.send_message(chat_id=int(callback.message.text.split()[4]), text=LEXICON['send_confirm_pay'])
        await callback.answer('Информация об успешной оплате отправлена.', show_alert=True)


@router.callback_query(F.data == 'confirm_booking')
async def process_booking_status(callback: CallbackQuery):
    try:
        if check_free_date(callback.message.text.split()[14]):
            raise Exception("Дата занята!")
        if not change_status_booking(callback.message.text.split()[1][1:], True):
            raise Exception("Уже подтверждено!")

    except Exception as Error:
        await callback.answer(f'{Error}', show_alert=True)
    else:
        await bot.send_message(chat_id=int(callback.message.text.split()[4]),
                               text=f'Ваш заезд подтвержден!\n\n<b>Ожидаем Вас '
                                    f'{".".join(reversed(callback.message.text.split()[14].split("-")))} с '
                                    f'14:00.</b>\n\nОзнакомьтесь с правилами проживания в /menu -> Информация о доме.'
                                    f'\n\nС дополнительной информацией можно ознакомиться в\n/menu -> Посмотреть мои '
                                    f'брони.\n\nТам же есть кнопка "Обратной связи".\nСпасибо.')
        await callback.answer('Информация о подтверждении бронирования отправлена.', show_alert=True)


@router.callback_query(F.data == 'cancel_booking')
async def process_booking_status(callback: CallbackQuery):
    try:
        if not change_status_booking(callback.message.text.split()[1][1:], False):
            raise Exception("Не было подтверждено!")

    except Exception as Error:
        await callback.answer(f'{Error}', show_alert=True)
    else:
        await bot.send_message(chat_id=int(callback.message.text.split()[4]), text=LEXICON['send_cancel_booking'])
        await callback.answer('Информация об отмене бронирования отправлена.', show_alert=True)
