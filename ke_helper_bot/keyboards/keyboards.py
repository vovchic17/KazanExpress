from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Обновление таблиц")],
    [KeyboardButton(text="Определить рейтинг")]
], resize_keyboard=True)

update_tables = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Ежедневный отчёт")],
    [KeyboardButton(text="Отчёт моих магазинов")],
    [KeyboardButton(text="Отчёт магазинов конкурента")],
    [KeyboardButton(text="Все таблицы")],
    [KeyboardButton(text="❌ Отмена")]
], resize_keyboard=True)

cancel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="❌ Отмена")]
], resize_keyboard=True)
