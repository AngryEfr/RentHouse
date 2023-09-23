from aiogram.filters import BaseFilter
from aiogram.types import Message
from environs import Env


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        env: Env = Env()
        env.read_env('.env')
        for i in env('ADMIN_IDS').split(', '):
            if message.from_user.id == int(i):
                return True
        return False
