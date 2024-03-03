import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config_reader import config
from google_sheets.wrapper import GoogleSheetsWrapper
from handlers.admin import router
from ke_parser.ke_parser import KEParser


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(
        token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    ke_parser = KEParser()
    gs = GoogleSheetsWrapper(
        bot,
        ke_parser,
        config.SPREADSHEET_KEY,
        config.DAILY_TASK_TABLE_ID,
        config.DAILY_REPORT_TABLE_ID,
        config.MY_SHOP_TASK_TABLE_ID,
        config.MY_SHOP_REPORT_TABLE_ID,
        config.COM_SHOP_TASK_TABLE_ID,
        config.COM_SHOP_REPORT_TABLE_ID,
        config.MY_NOTIF_TABLE_ID,
        config.MY_STOCK_NOTIF_TABLE_ID,
        config.COM_NOTIF_TABLE_ID,
        config.COM_STOCK_NOTIF_TABLE_ID,
    )
    dp = Dispatcher(gs=gs, ke_parser=ke_parser)
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.start()
    dp.startup.register(gs.init)
    dp.message.filter(F.from_user.id.in_(config.ADMINS))
    dp.include_router(router)

    scheduler.add_job(gs.update_all_tables, "cron", hour=9)
    scheduler.add_job(gs.check_all_stock, "interval", minutes=2)
    scheduler.add_job(gs.check_all_changes, "interval", minutes=2)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
