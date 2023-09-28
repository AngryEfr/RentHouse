from aiogram.filters import BaseFilter
from aiogram.types import Message
import re


class HasUsernamesFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if " - " not in message.text:
            if check_date_format(message.text):
                return True
        else:

            pattern = r"\d{2}\.\d{2}\.\d{4}\s-\s\d{2}\.\d{2}\.\d{4}"  # Паттерн для проверки формата
            match = re.match(pattern, message.text)
            if match:
                date_parts = message.text.split(' - ')
                start_date = date_parts[0]
                end_date = date_parts[1]
                if check_date_format(start_date) and check_date_format(end_date):
                    return True
            return False


def check_date_format(date):
    pattern = r"\d{2}\.\d{2}\.\d{4}"  # Паттерн для проверки формата
    match = re.match(pattern, date)
    if match:
        date_parts = date.split('.')
        day = int(date_parts[0])
        month = int(date_parts[1])
        year = int(date_parts[2])
        if month in [1, 3, 5, 7, 8, 10, 12]:
            if day <= 31:
                return True
        elif month in [4, 6, 9, 11]:
            if day <= 30:
                return True
        elif month == 2:
            if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
                if day <= 29:
                    return True
            else:
                if day <= 28:
                    return True
    return False
