from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon_ru import LEXICON, LEXICON_BUTTONS


def create_main_menu(*buttons: str) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(*[InlineKeyboardButton(
        text=LEXICON_BUTTONS[button] if button in LEXICON_BUTTONS else button,
        callback_data=button) for button in buttons],
                   width=1
    )
    return kb_builder.as_markup()


def create_info_menu(*buttons: str) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for button in buttons:
        button = button.split('/*/*/*')
        kb_builder.row(InlineKeyboardButton(text=button[0], url=button[1]), width=1)
    kb_builder.row(InlineKeyboardButton(text='На главную', callback_data='menu'), width=1)
    return kb_builder.as_markup()
