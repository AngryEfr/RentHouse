from aiogram import Router
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, MEMBER, LEFT

from database.db_quick_commands import change_status_active


router = Router()


# Этот хэндлер изменяет статус пользователя на неактивного
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def process_user_blocked_bot(event: ChatMemberUpdated):
    change_status_active(event, False)


# Этот хэндлер изменяет статус пользователя на активного
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def process_user_blocked_bot(event: ChatMemberUpdated):
    change_status_active(event, True)


# Этот хэндлер изменяет статус пользователя на неактивного
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=LEFT))
async def process_user_blocked_bot(event: ChatMemberUpdated):
    change_status_active(event, False)


# Этот хэндлер будет реагировать на любые сообщения пользователя,
# не предусмотренные логикой работы бота
@router.message()
async def send_echo(message: Message):
    await message.answer(f'Я не понимаю, попробуй нажать внизу кнопку с командами. Для помощи - /help')
