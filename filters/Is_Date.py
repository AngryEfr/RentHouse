from aiogram.filters import BaseFilter
from aiogram.types import Message


class HasUsernamesFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if 8 <= len(message.text) <= 10:
            if len(message.text.split('.')) == 3:
                date = message.text.split('.')
                if date[0].isdigit() and date[1].isdigit() and date[2].isdigit():
                    if 1 <= int(date[0]) <= 31 and 1 <= int(date[1]) <= 12 and 2023 <= int(date[2]) <= 2100:
                        return True
        elif 19 <= len(message.text) <= 23:
            if len(message.text.split(' - ')) == 2:
                date = message.text.split(' - ')
                date1 = date[0].split('.')
                date2 = date[1].split('.')
                if date1[0].isdigit() and date1[1].isdigit() and date1[2].isdigit() and date2[0].isdigit() and date2[1].isdigit() and date2[2].isdigit():
                    if 1 <= int(date1[0]) <= 31 and 1 <= int(date1[1]) <= 12 and 2023 <= int(date1[2]) <= 2100 and 1 <= int(date2[0]) <= 31 and 1 <= int(date2[1]) <= 12 and 2023 <= int(date2[2]) <= 2100:
                        return True
        else:
            return False
