import asyncio
import logging
from datetime import datetime as dt
from datetime import timedelta, timezone
from typing import ClassVar

from aiogram import Bot
from aiohttp import ClientSession
from google.oauth2.service_account import Credentials
from gspread.utils import ValueInputOption
from gspread_asyncio import (
    AsyncioGspreadClientManager,
    AsyncioGspreadSpreadsheet,
)
from ke_parser.ke_parser import KEParser
from ke_parser.models import GoogleSheetProduct

from ke_helper_bot.config_reader import config

from . import utils

logger = logging.getLogger(__name__)


class GoogleSheetsWrapper:
    """
    Google Sheets API wrapper for
    parsing task tables and
    fill the report tables
    """

    tz = timezone(timedelta(hours=3))
    message_id: ClassVar[dict[int, int]] = {}
    rows: ClassVar[dict[int, list]] = {}
    records: ClassVar[dict[int, list]] = {}
    stock: ClassVar[dict[int, dict[int, int]]] = {}
    products: ClassVar[dict[int, dict[int, GoogleSheetProduct]]] = {}

    def __init__(
        self,
        bot: Bot,
        ke_parser: KEParser,
        spreadsheet_key: str,
        daily_task_table_id: int,
        daily_report_table_id: int,
        my_shop_task_table_id: int,
        my_shop_report_table_id: int,
        com_shop_task_table_id: int,
        com_shop_report_table_id: int,
        my_notif_table_id: int,
        my_stock_notif_table_id: int,
        com_notif_table_id: int,
        com_stock_notif_table_id: int,
    ) -> None:
        self.bot = bot
        self.ke_parser = ke_parser
        self.spreadsheet_key = spreadsheet_key
        self.daily_task_table_id = daily_task_table_id
        self.daily_report_table_id = daily_report_table_id
        self.my_shop_task_table_id = my_shop_task_table_id
        self.my_shop_report_table_id = my_shop_report_table_id
        self.com_shop_task_table_id = com_shop_task_table_id
        self.com_shop_report_table_id = com_shop_report_table_id
        self.my_notif_table_id = my_notif_table_id
        self.my_stock_notif_table_id = my_stock_notif_table_id
        self.com_notif_table_id = com_notif_table_id
        self.com_stock_notif_table_id = com_stock_notif_table_id
        self.agcm = AsyncioGspreadClientManager(self.__get_creds)

    def __get_creds(self) -> Credentials:
        creds = Credentials.from_service_account_file("creds.json")
        return creds.with_scopes(["https://www.googleapis.com/auth/drive"])

    async def init(self) -> None:
        """Initialize spreadsheet and its tables"""
        agc = await self.agcm.authorize()
        self.ss = await agc.open_by_key(self.spreadsheet_key)
        self.daily_task_table = await self.ss.get_worksheet_by_id(
            self.daily_task_table_id
        )
        self.daily_report_table = await self.ss.get_worksheet_by_id(
            self.daily_report_table_id
        )
        self.my_shop_task_table = await self.ss.get_worksheet_by_id(
            self.my_shop_task_table_id
        )
        self.my_shop_report_table = await self.ss.get_worksheet_by_id(
            self.my_shop_report_table_id
        )
        self.com_shop_task_table = await self.ss.get_worksheet_by_id(
            self.com_shop_task_table_id
        )
        self.com_shop_report_table = await self.ss.get_worksheet_by_id(
            self.com_shop_report_table_id
        )
        self.my_notif_table = await self.ss.get_worksheet_by_id(self.my_notif_table_id)
        self.my_stock_notif_table = await self.ss.get_worksheet_by_id(
            self.my_stock_notif_table_id
        )
        self.com_notif_table = await self.ss.get_worksheet_by_id(
            self.com_notif_table_id
        )
        self.com_stock_notif_table = await self.ss.get_worksheet_by_id(
            self.com_stock_notif_table_id
        )
        logger.info("Spreadsheets were initialized")

    async def notify(self, message: str) -> None:
        """Notify the admins"""
        logger.info("Notifying admins with message: %s", message)
        for admin in config.ADMINS:
            await self.bot.send_message(admin, message, disable_web_page_preview=True)

    async def daily_task(self, chat_id: int | None = None) -> None:
        """Fill the daily report table"""
        logger.info("Running daily task")
        self.records[self.daily_report_table_id] = [
            x for x in await self.daily_task_table.get("B3:G") if len(x) > 3
        ]
        if chat_id is not None:
            msg = await self.bot.send_message(
                chat_id,
                "Прогресс - <b>[0/"
                f"{len(self.records[self.daily_report_table_id])}]</b>",
            )
            self.message_id[self.daily_report_table_id] = msg.message_id

        self.rows[self.daily_report_table_id] = [None] * len(
            self.records[self.daily_report_table_id]
        )

        await self.prepare_daily_cols()

        tasks = []

        async with ClientSession(headers=self.ke_parser.headers) as session:
            for i, record in enumerate(self.records[self.daily_report_table_id]):
                tasks.append(
                    self.parse_daily_data(
                        session, record[0], record[1], record[3], record[5], i, chat_id
                    )
                )
            await asyncio.gather(*tasks)

        await self.daily_report_table.update(
            f"B3:Z{len(self.rows[self.daily_report_table_id])+3}",
            self.rows[self.daily_report_table_id],
            value_input_option=ValueInputOption.user_entered,
            nowait=True,
        )
        if chat_id is not None:
            await self.bot.edit_message_text(
                "✅ Сбор информации завершён!",
                chat_id,
                self.message_id[self.daily_report_table_id],
            )

    async def prepare_daily_cols(self) -> None:
        """
        Prepare columns and headers
        for daily report table
        """
        await self.daily_report_table.insert_cols(
            [
                [
                    dt.now(tz=self.tz).strftime("%d.%m.%Y %H:%M"),
                    "Поисковый запрос",
                ],
                ["", "Наименование"],
                ["Мой Магазин", "Shop"],
                ["", "Характеристика"],
                ["", "ProdID"],
                ["", "SKUID"],
                ["", "Отзывы"],
                ["", "Рейтинг"],
                ["", "Заказы"],
                ["", "Заказы за 7 дн."],
                ["", "Остаток"],
                ["", "Цена"],
                ["", "№ в поиске"],
                ["Магазин Конкурента", "Shop"],
                ["", "Характеристика"],
                ["", "ProdID"],
                ["", "SKUID"],
                ["", "Отзывы"],
                ["", "Рейтинг"],
                ["", "Заказы"],
                ["", "Заказы за 7 дн."],
                ["", "Остаток"],
                ["", "Цена"],
                ["", "№ в поиске"],
                ["", "кол. карточек"],
            ],
            2,
        )
        await utils.format_daily_table(self.ss, self.daily_report_table_id)

    async def parse_daily_data(
        self,
        session: ClientSession,
        name: str,
        search_query: str,
        my_link: str,
        com_link: str,
        index: int,
        chat_id: int | None,
    ) -> None:
        """
        Collect the daily product data
        and saves it to self.rows
        """
        my_prod = await self.ke_parser.get_all_info(session, search_query, my_link)
        com_prod = await self.ke_parser.get_all_info(session, search_query, com_link)
        self.rows[self.daily_report_table_id][index] = [
            f'=ГИПЕРССЫЛКА("https://kazanexpress.ru/search?query={search_query}"'
            f'; "{search_query}")',
            name,
            my_prod.shop,
            my_prod.characteristic,
            my_prod.product_id,
            f'=ГИПЕРССЫЛКА("{my_link}"; "{my_prod.product_skuid}")',
            my_prod.reviews_count,
            my_prod.rating,
            my_prod.order_count,
            my_prod.week_order_count,
            my_prod.stock,
            my_prod.price,
            my_prod.search_position,
            com_prod.shop,
            com_prod.characteristic,
            com_prod.product_id,
            f'=ГИПЕРССЫЛКА("{com_link}"; "{com_prod.product_skuid}")',
            com_prod.reviews_count,
            com_prod.rating,
            com_prod.order_count,
            com_prod.week_order_count,
            com_prod.stock,
            com_prod.price,
            com_prod.search_position,
            com_prod.total_count,
        ]
        progress = len([x for x in self.rows[self.daily_report_table_id] if x])
        if chat_id is not None:
            await self.bot.edit_message_text(
                f"Прогресс - <b>[{progress}/"
                f"{len(self.records[self.daily_report_table_id])}]</b>",
                chat_id,
                self.message_id[self.daily_report_table_id],
            )

    async def shop_task(
        self,
        tasksheet: AsyncioGspreadSpreadsheet,
        reportsheet: AsyncioGspreadSpreadsheet,
        chat_id: int | None = None,
    ) -> None:
        """Fill the shop report tables"""
        shop_names = {
            self.my_shop_report_table_id: "Мой магазин",
            self.com_shop_report_table_id: "Магазин Конкурента",
        }

        logger.info("Running shop task for %s", shop_names[reportsheet.id])

        self.records[reportsheet.id] = list(
            filter(
                lambda x: len(x) > 3 and x[0] and x[2] and x[3],
                await tasksheet.get("B4:E"),
            )
        )
        if chat_id is not None:
            msg = await self.bot.send_message(
                chat_id, f"Прогресс - <b>[0/{len(self.records[reportsheet.id])}]</b>"
            )
            self.message_id[reportsheet.id] = msg.message_id

        self.rows[reportsheet.id] = [None] * len(self.records[reportsheet.id])

        await self.prepare_shop_cols(reportsheet, shop_names[reportsheet.id])

        tasks = []

        async with ClientSession(headers=self.ke_parser.headers) as session:
            for i, record in enumerate(self.records[reportsheet.id]):
                tasks.append(
                    self.parse_shop_data(
                        reportsheet,
                        session,
                        record[0],
                        record[2],
                        record[3],
                        i,
                        chat_id,
                    )
                )

            await asyncio.gather(*tasks)

        await reportsheet.update(
            f"B3:O{len(self.rows[reportsheet.id])+3}",
            self.rows[reportsheet.id],
            value_input_option=ValueInputOption.user_entered,
            nowait=True,
        )
        if chat_id is not None:
            await self.bot.edit_message_text(
                "✅ Сбор информации завершён!", chat_id, self.message_id[reportsheet.id]
            )

    async def prepare_shop_cols(
        self, reportsheet: AsyncioGspreadSpreadsheet, shop: str
    ) -> None:
        """
        Prepare columns and headers
        for shop report tables
        """
        await reportsheet.insert_cols(
            [
                [
                    dt.now(tz=self.tz).strftime("%d.%m.%Y %H:%M"),
                    "Поисковый запрос",
                ],
                [shop, "Наименование"],
                ["", "Shop"],
                ["", "Характеристика"],
                ["", "ProdID"],
                ["", "SKUID"],
                ["", "Отзывы"],
                ["", "Рейтинг"],
                ["", "Заказы"],
                ["", "Заказы за 7 дн."],
                ["", "Остаток"],
                ["", "Цена"],
                ["", "№ в поиске"],
                ["", "кол. карточек"],
            ],
            2,
            nowait=True,
        )

        await utils.format_shop_table(
            self.ss,
            self.my_shop_report_table_id,
            self.com_shop_report_table_id,
            reportsheet.id,
        )

    async def parse_shop_data(
        self,
        reportsheet: AsyncioGspreadSpreadsheet,
        session: ClientSession,
        name: str,
        search_query: str,
        link: str,
        index: int,
        chat_id: int | None,
    ) -> None:
        """
        Collect the shop product data
        and save it to self.rows.
        """
        product = await self.ke_parser.get_all_info(session, search_query, link)
        self.rows[reportsheet.id][index] = [
            f'=ГИПЕРССЫЛКА("https://kazanexpress.ru/search?query={search_query}"'
            f'; "{search_query}")',
            name,
            product.shop,
            product.characteristic,
            product.product_id,
            f'=ГИПЕРССЫЛКА("{link}"; "{product.product_skuid}")',
            product.reviews_count,
            product.rating,
            product.order_count,
            product.week_order_count,
            product.stock,
            product.price,
            product.search_position,
            product.total_count,
        ]
        progress = len([x for x in self.rows[reportsheet.id] if x])
        if chat_id is not None:
            await self.bot.edit_message_text(
                f"Прогресс - <b>[{progress}/"
                f"{len(self.records[reportsheet.id])}]</b>",
                chat_id,
                self.message_id[reportsheet.id],
            )

    async def update_all_tables(self) -> None:
        """Update all the tables"""
        await self.daily_task()
        await self.shop_task(self.my_shop_task_table, self.my_shop_report_table)
        await self.shop_task(self.com_shop_task_table, self.com_shop_report_table)

    async def check_all_stock(self) -> None:
        """Check the stocks of all shops"""
        records = [x for x in await self.my_shop_task_table.get("B4:F") if len(x) > 4]
        await self.check_shop_stock(records, self.my_stock_notif_table)
        records = [x for x in await self.com_shop_task_table.get("B4:F") if len(x) > 4]
        await self.check_shop_stock(records, self.com_stock_notif_table)

    async def check_shop_stock(
        self, records: list, notif_table: AsyncioGspreadSpreadsheet
    ) -> None:
        """Check the stock of the products"""
        for record in records:
            try:
                (
                    prod_id,
                    stock,
                    title,
                    shop,
                    price,
                    char,
                    sku_id,
                ) = await self.ke_parser.get_info(record[3])
                if stock <= int(record[4]):
                    # skip notifying if already notified
                    if stock == self.stock.get(prod_id, {}).get(sku_id):
                        continue

                    self.stock.setdefault(prod_id, {})[sku_id] = stock
                    await self.notify(
                        '<a href="https://docs.google.com/spreadsheets/d/'
                        f'{self.spreadsheet_key}/edit#gid={notif_table.id}">'
                        f"Остаток товара в вашем магазине</a> <b>{shop}</b>\n"
                        f'<i><a href="{record[3]}">{title}</a> <b>{char}</b>'
                        f"</i> достиг минимального ({stock} "
                        f"&lt;= {record[4]} шт.)"
                    )
                    await notif_table.insert_row(
                        [
                            dt.now(tz=self.tz).strftime("%d.%m.%Y %H:%M"),
                            record[0],  # name
                            record[1],  # char
                            shop,
                            record[3],  # link
                            sku_id,
                            stock,
                            price,
                        ],
                        2,
                    )
            except LookupError:
                await self.notify(
                    f"❌ Не удалось определить остаток товара\nСсылка: {record[3]}"
                )

    async def check_all_changes(self) -> None:
        """Check the changes of all shops"""
        records = [x for x in await self.my_shop_task_table.get("B4:F") if len(x) > 3]
        await self.check_shop_changes(records, self.my_notif_table)
        records = [x for x in await self.com_shop_task_table.get("B4:F") if len(x) > 3]
        await self.check_shop_changes(records, self.com_notif_table)

    async def check_shop_changes(
        self, records: list, notif_table: AsyncioGspreadSpreadsheet
    ) -> None:
        """Check the changes of the products"""
        for record in records:
            try:
                async with ClientSession(headers=self.ke_parser.headers) as session:
                    product = await self.ke_parser.get_all_info(
                        session, record[2], record[3]
                    )
                if (
                    product.product_id in self.products
                    and product.product_skuid in self.products[product.product_id]
                ):
                    old_product = self.products[product.product_id][
                        product.product_skuid
                    ]
                    if product.price != old_product.price:
                        await self.notify(
                            f'<b><a href="https://docs.google.com/spreadsheets/d/'
                            f'{self.spreadsheet_key}/edit#gid={self.my_notif_table_id}">'
                            "Изменилась цена в вашем магазине</a></b>\n\n<i>"
                            f"<a href='{record[3]}'>{product.title}</a> "
                            f"<b>{product.characteristic}</b></i>\n\nМагазин: "
                            f"{product.shop}\nОценка: {product.rating} "
                            f"({product.reviews_count} оценок)\nЗаказы:"
                            f"{product.order_count}\nОстаток: {product.stock}\n"
                            f"Цена: {old_product.price} ₽ "
                            f"=&gt; {product.price} ₽"
                        )
                        await notif_table.insert_row(
                            [
                                dt.now(tz=self.tz).strftime("%d.%m.%Y %H:%M"),
                                record[0],
                                record[1],
                                product.shop,
                                record[3],
                                product.product_skuid,
                                old_product.price,
                                product.price,
                            ],
                            2,
                        )
                else:
                    # just add the product to storage
                    # for comparing in the future
                    continue

                self.products.setdefault(product.product_id, {})[
                    product.product_skuid
                ] = product

            except LookupError:
                await self.notify(f"❌ Не удалось найти товар\nСсылка: {record[3]}")
