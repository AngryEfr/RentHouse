from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton,\
    InlineKeyboardMarkup, CallbackQuery, FSInputFile
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types.web_app_info import WebAppInfo

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from states.states import FSMFillForm

from database.db_quick_commands import register_user, get_active_house, get_booking, check_date, csv_save
from json import loads

from utils.utils import change_the_date
from filters.is_admin import IsAdmin
from filters.Is_Date import HasUsernamesFilter
from keyboards.menu_buttons import create_main_menu
from lexicon.lexicon_ru import LEXICON

import datetime

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


# Хэндлер бронирования для админа (создание брони от имени админа для телефонных и иных броней)
@router.message(Command(commands='booking'))
async def process_help_admin_command(message: Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Перейти к бронированию',
                                                           web_app=WebAppInfo(url='/index.html'))]],
                                 resize_keyboard=True)
    await message.answer(text=LEXICON['/booking'], reply_markup=markup)
    await state.clear()


@router.message(F.content_type == 'web_app_data')
async def web_app(message: Message, state: FSMContext):
    res = loads(message.web_app_data.data)
    await message.answer(f'Name: {res["name"]}\nPhone: {res["phone"]}\n')
    await state.clear()


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что эта команда работает внутри машины состояний
@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Отменять нечего. Вы вне машины состояний\n\n'
             'Чтобы перейти к заполнению брони - '
             'отправьте команду /fillform'
    )


@router.message(Command(commands='csv'))
async def process_cancel_command(message: Message):
    csv_save()
    file = FSInputFile("mydump.csv")
    await message.reply_document(file)


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


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы прервали заполнение брони\n\n'
             'Чтобы снова перейти к заполнению  - '
             'отправьте команду /fillform'
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# Этот хэндлер будет срабатывать на команду /fillform
# и переводить бота в состояние ожидания ввода имени
@router.message(Command(commands='fillform'))
async def process_fillform_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text='Пожалуйста, введите имя гостя\n\nДля отмены жми /cancel')
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSMFillForm.fill_name)


@router.message(StateFilter(FSMFillForm.fill_name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенное имя в хранилище по ключу "fill_name"
    await state.update_data(fill_name=message.text)
    active_house = get_active_house()
    buttons: list[InlineKeyboardButton] = []
    for i in active_house:
        buttons.append(InlineKeyboardButton(
            text=i.name,
            callback_data=str(i.id)
        ))
    markup = InlineKeyboardMarkup(
        inline_keyboard=[buttons]
    )

    await message.answer(text='Спасибо!\n\nА теперь выбери дом, просто нажми на кнопку снизу\n\nДля отмены жми /cancel',
                         reply_markup=markup)
    await state.set_state(FSMFillForm.fill_id_house)


# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_name))
async def warning_not_name(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на имя\n\n'
             'Пожалуйста, введите имя гостя\n\n'
             'Если вы хотите прервать заполнение брони - '
             'отправьте команду /cancel'
    )


@router.callback_query(StateFilter(FSMFillForm.fill_id_house), F.data.in_(['1', '2', '3']))
async def process_take_house(callback: CallbackQuery, state: FSMContext):
    await state.update_data(fill_id_house=callback.data)
    await callback.message.delete()
    await callback.message.answer(
        text='Спасибо! А теперь введите даты (один день: "23.09.2023" или период "23.09.2023 - 25.09.2023")\n\n'
             'Для отмены жми /cancel'
    )
    await state.set_state(FSMFillForm.fill_date)


# Этот хэндлер будет срабатывать, если во время выбора дома
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_id_house))
async def warning_not_age(message: Message):
    await message.answer(
        text='Нажмите на кнопку для выбора дома\n\nЕсли вы хотите прервать '
             'заполнение брони - отправьте команду /cancel'
    )


@router.message(StateFilter(FSMFillForm.fill_date), HasUsernamesFilter())
async def process_fill_date(message: Message, state: FSMContext):
    try:
        user_dict[message.from_user.id] = await state.get_data()
        date_begin, date_end = change_the_date(message.text)
        if type(date_end) is datetime.date:
            date = date_end - date_begin
            for i in range(date.days):
                if not check_date(date_begin, user_dict[message.from_user.id]['fill_id_house']):
                    await message.answer(
                        text='Даты заняты, проверьте календарь.\n\nЕсли вы хотите прервать '
                             'заполнение брони - отправьте команду /cancel'
                    )
                    return False
                date_begin += datetime.timedelta(days=1)
        elif not check_date(date_begin, user_dict[message.from_user.id]['fill_id_house']):
            await message.answer(
                text='Дата занята, проверьте календарь.\n\nЕсли вы хотите прервать '
                     'заполнение брони - отправьте команду /cancel'
            )
            return False

        await state.set_state(FSMFillForm.confirm)
    except Exception as Error:
        print(Error)
        await message.answer(
            text='Даты заняты, проверьте календарь.\n\nЕсли вы хотите прервать '
                 'заполнение брони - отправьте команду /cancel'
        )

    else:
        await state.update_data(fill_date=message.text)
        await message.delete()
        user_dict[message.from_user.id] = await state.get_data()
        date_begin, date_end = change_the_date(user_dict[message.from_user.id]["fill_date"])
        button_yes = InlineKeyboardButton(
            text='Да',
            callback_data='yes'
        )
        button_no = InlineKeyboardButton(
            text='Нет',
            callback_data='no'
        )
        markup = InlineKeyboardMarkup(
            inline_keyboard=[[button_yes],
                             [button_no]]
        )
        if type(date_end) is str:
            await message.answer(
                text=f'Внести данные в базу?\n'
                     f'Имя: {user_dict[message.from_user.id]["fill_name"]}\n'
                     f'Дом: {user_dict[message.from_user.id]["fill_id_house"]}\n'
                     f'Дата заезда: {date_begin}\n'
                     f'Заезд продлится один день\n',
                reply_markup=markup
            )
        else:
            await message.answer(
                text=f'Внести данные в базу?\n'
                     f'Имя: {user_dict[message.from_user.id]["fill_name"]}\n'
                     f'Дом: {user_dict[message.from_user.id]["fill_id_house"]}\n'
                     f'Дата заезда: {date_begin}\n'
                     f'Заезд продлится дней: {(date_end - date_begin).days}',
                reply_markup=markup
            )


# Этот хэндлер будет срабатывать, если во время введения даты
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_date))
async def warning_not_age(message: Message):
    await message.answer(
        text='Введите корректные данные\n\nЕсли вы хотите прервать '
             'заполнение брони - отправьте команду /cancel'
    )


@router.callback_query(StateFilter(FSMFillForm.confirm), F.data.in_(['yes']))
async def process_take_house(callback: CallbackQuery, state: FSMContext):
    await state.update_data(confirm=callback.data)
    await callback.message.delete()
    date_begin, date_end = change_the_date(user_dict[callback.message.chat.id]["fill_date"])
    try:
        get_booking(callback.message, user_dict[callback.message.chat.id]["fill_name"],
                    user_dict[callback.message.chat.id]["fill_id_house"], date_begin, date_end)
        await callback.message.answer(
            text='Данные внесены в базу.'
        )
        await state.clear()
    except Exception as Error:
        print(Error)
        await callback.message.answer(
            text='Ошибка внесения в базу.'
        )


@router.callback_query(StateFilter(FSMFillForm.confirm), F.data.in_(['no']))
async def process_take_house(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        text='Что снова начать заполнение брони, введите /fillform'
    )
    await state.clear()


# Этот хэндлер будет срабатывать, если во время подтверждения
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.confirm))
async def warning_not_age(message: Message):
    await message.answer(
        text='Нажмите на кнопку для подтверждения\n\nЕсли вы хотите прервать '
             'заполнение брони - отправьте команду /cancel'
    )
