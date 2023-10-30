import asyncio
import logging

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config_data.config import Config, load_config
from handlers import admin_handlers, user_handlers, other_handlers
from handlers.apsched import send_message_cron
from keyboards.set_menu import set_main_menu
from pytz import timezone
from apscheduler.triggers.cron import CronTrigger


logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(level=logging.INFO, format='%(filename)s:%(lineno)d #%(levelname)-8s '
                                                                           '[%(asctime)s] - %(name)s - %(message)s')

    logging.info('Starting bot')

    config: Config = load_config('.env')

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher()

    await set_main_menu(bot)

    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(send_message_cron, CronTrigger(hour=9, minute=00, timezone=timezone("Europe/Moscow")))
    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
