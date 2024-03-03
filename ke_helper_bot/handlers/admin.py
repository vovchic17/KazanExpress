from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from google_sheets.wrapper import GoogleSheetsWrapper
from ke_parser.ke_parser import KEParser
from keyboards import keyboards as kb
from states import FSM

router = Router(name=__name__)


@router.message(F.text == "❌ Отмена")
async def cancel(message: Message, state: FSMContext) -> None:
    await message.answer("❌ Действие отменено", reply_markup=kb.menu)
    await state.clear()


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Привет, это бот Анализ Конкурента КЕ", reply_markup=kb.menu
    )


@router.message(F.text == "Обновление таблиц", StateFilter(None))
async def tables_update(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Какую таблицу обновить?", reply_markup=kb.update_tables
    )
    await state.set_state(FSM.update_tables)


@router.message(F.text == "Ежедневный отчёт", FSM.update_tables)
async def update_daily(
    message: Message, state: FSMContext, gs: GoogleSheetsWrapper
) -> None:
    await message.answer("🕒 Обновление запущено...", reply_markup=kb.menu)
    await state.clear()
    await gs.daily_task(message.from_user.id)
    await message.answer(
        "✅ Таблица <b><a href='"
        f"https://docs.google.com/spreadsheets/d/{gs.spreadsheet_key}/edit#gid={gs.daily_report_table_id}"
        "'>Ежедневный отчёт</a></b> успешно обновлена",
        disable_web_page_preview=True
    )


@router.message(F.text == "Отчёт моих магазинов", FSM.update_tables)
async def update_my_shop(
    message: Message, state: FSMContext, gs: GoogleSheetsWrapper
) -> None:
    await message.answer("🕒 Обновление запущено...", reply_markup=kb.menu)
    await state.clear()
    await gs.shop_task(
        gs.my_shop_task_table,
        gs.my_shop_report_table,
        message.from_user.id
    )
    await message.answer(
        "✅ Таблица <b><a href='"
        f"https://docs.google.com/spreadsheets/d/{gs.spreadsheet_key}/edit#gid={gs.my_shop_report_table_id}"
        "'>Отчёт моих магазинов</a></b> успешно обновлена",
        disable_web_page_preview=True
    )


@router.message(F.text == "Отчёт магазинов конкурента", FSM.update_tables)
async def update_com_shop(
    message: Message, state: FSMContext, gs: GoogleSheetsWrapper
) -> None:
    await message.answer("🕒 Обновление запущено...", reply_markup=kb.menu)
    await state.clear()
    await gs.shop_task(
        gs.com_shop_task_table,
        gs.com_shop_report_table,
        message.from_user.id
    )
    await message.answer(
        "✅ Таблица <b><a href="
        f"\"https://docs.google.com/spreadsheets/d/{gs.spreadsheet_key}/edit#gid={gs.com_shop_report_table_id}"
        "\">Отчёт магазинов конкурента</a></b> успешно обновлена",
        disable_web_page_preview=True
    )


@router.message(F.text == "Все таблицы", FSM.update_tables)
async def update_all_tables(
    message: Message, state: FSMContext, gs: GoogleSheetsWrapper
) -> None:
    await update_daily(message, state, gs)
    await update_my_shop(message, state, gs)
    await update_com_shop(message, state, gs)


@router.message(FSM.update_tables)
async def update_unknown(message: Message) -> None:
    await message.answer(
        "❌ Я вас не понимаю, выберите таблицу для обновления",
        reply_markup=kb.update_tables,
    )


@router.message(F.text == "Определить рейтинг", StateFilter(None))
async def get_rating(message: Message, state: FSMContext) -> None:
    await message.answer("Введите ссылку на товар", reply_markup=kb.cancel)
    await state.set_state(FSM.get_ratings)


@router.message(FSM.get_ratings)
async def get_ratings(
    message: Message, state: FSMContext, ke_parser: KEParser
) -> None:
    await message.answer("🕒 Ищу данные...", reply_markup=kb.menu)
    try:
        ratings = await ke_parser.get_ratings_info(message.text)
        print(ratings)
        res = f"<b><a href=\"{ratings.link}\">{ratings.title}</a></b> "\
                f"({ratings.rating}⭐️)\n"
        for sku_item in ratings.items:
            res += f"{sku_item.characteristic} {sku_item.rating}⭐️\n"
            res += f"SKUID: {sku_item.sku_id}\n"
            res += f"Заказов: {sku_item.orders}\n"
            res += f"Отзывов: {sku_item.reviews}\n\n"
        await message.answer(
            res, reply_markup=kb.menu, disable_web_page_preview=True
        )
    except LookupError:
        await message.answer(
            "❌ Ошибка при получении рейтингов", reply_markup=kb.menu
        )
    await state.clear()


@router.message(F.content_type == ContentType.ANY)
async def unknown(message: Message):
    await message.answer("❌ Я вас не понимаю", reply_markup=kb.menu)
