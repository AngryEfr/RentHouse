from aiogram import Bot
from config_data.config import Config, load_config
from database.db_quick_commands import get_bookings_tomorrow, check_active_user


config: Config = load_config('.env')
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')


async def send_message_cron():
    try:
        result = get_bookings_tomorrow()
        if result:
            for i in result:
                if not check_active_user(i[2]):
                    raise Exception("Бот заблокирован пользователем.")
        else:
            raise Exception("На завтра нет заездов.")
    except Exception as Error:
        for i in config.tg_bot.admin_ids:
            await bot.send_message(chat_id=i, text=f'{Error}')
    else:
        for i in config.tg_bot.admin_ids:
            await bot.send_message(chat_id=i,
                                   text=f'На завтра есть подтвержденное заселение!\n\n'
                                        f'Бронь №{result[0][0]}\nID пользователя {result[0][2]}\nЛогин: @{result[0][3]}'
                                        f'\nДом №{result[0][1]}\nДата брони: {result[0][4]}\nДата заселения: '
                                        f'{result[0][5]}\nТелефон: {result[0][6]}\nРеквизиты отправлены: '
                                        f'{result[0][7]}\nОплата: {result[0][8]}\nПодтверждение заезда: '
                                        f'{result[0][9]}\nКоличество дней: {result[0][10]}')

        await bot.send_message(chat_id=result[0][2], text=f'Спешу напомнить про завтрашнее заселение. Ждём с 14:00.\n\n'
                                                          f'Ознакомьтесь с правилами проживания в /menu -> Информация '
                                                          f'о доме.\n\nС дополнительной информацией можно ознакомиться '
                                                          f'в\n/menu -> Посмотреть мои брони.\n\nТам же есть кнопка '
                                                          f'"Обратной связи".\nСпасибо.')
