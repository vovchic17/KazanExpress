from gspread_asyncio import AsyncioGspreadSpreadsheet

from . import cell_formatter


async def format_daily_table(ss: AsyncioGspreadSpreadsheet, sheet_id: int) -> None:
    """Apply all cell styles for the daily table"""
    await cell_formatter.update(
        ss,
        cell_formatter.update_size(
            sheet_id,
            [
                150,
                110,
                110,
                100,
                60,
                60,
                30,
                30,
                30,
                30,
                30,
                40,
                30,
                110,
                100,
                60,
                60,
                30,
                30,
                30,
                30,
                30,
                40,
                30,
                30,
            ],
        ),
        cell_formatter.merge(sheet_id, 1, 3, 14),
        cell_formatter.merge(sheet_id, 1, 14, 25),
        cell_formatter.rotate(sheet_id, 2, 7, 14, 90),
        cell_formatter.rotate(sheet_id, 2, 19, 26, 90),
        cell_formatter.update_borders(sheet_id, 0, 2, 0, 1000000, "SOLID"),
        cell_formatter.update_borders(sheet_id, 2, 1000000, 0, 1000000, "DASHED"),
        cell_formatter.boolean_rule(sheet_id, 2, 1000000, 7, 12, "=GT(H3;S3)", "green"),
        cell_formatter.boolean_rule(sheet_id, 2, 1000000, 7, 12, "=LT(H3;S3)", "red"),
        cell_formatter.boolean_rule(sheet_id, 2, 1000000, 12, 14, "=GT(M3;X3)", "red"),
        cell_formatter.boolean_rule(
            sheet_id, 2, 1000000, 12, 14, "=LT(M3;X3)", "green"
        ),
        cell_formatter.text_equal_rule(
            sheet_id, 1, 1000000, 1, 1000000, "no", "yellow"
        ),
        cell_formatter.text_equal_rule(
            sheet_id,
            1,
            1000000,
            1,
            1000000,
            "Не найдено",
            "yellow",
        ),
    )


async def format_shop_table(
    ss: AsyncioGspreadSpreadsheet,
    my_shop_report_table_id: int,
    com_shop_report_table_id: int,
    sheet_id: int,
) -> None:
    """Apply all cell styles for the shop table"""
    boolean_rules = {
        my_shop_report_table_id: [
            cell_formatter.boolean_rule(
                my_shop_report_table_id,
                2,
                1000000,
                7,
                11,
                "=GT(H3;V3)",
                "green",
            ),
            cell_formatter.boolean_rule(
                my_shop_report_table_id, 2, 1000000, 7, 11, "=LT(H3;V3)", "red"
            ),
            cell_formatter.boolean_rule(
                my_shop_report_table_id,
                2,
                1000000,
                12,
                14,
                "=GT(M3;AA3)",
                "red",
            ),
            cell_formatter.boolean_rule(
                my_shop_report_table_id,
                2,
                1000000,
                12,
                14,
                "=LT(M3;AA3)",
                "green",
            ),
        ],
        com_shop_report_table_id: [
            cell_formatter.boolean_rule(
                com_shop_report_table_id,
                2,
                1000000,
                7,
                11,
                "=GT(H3;V3)",
                "red",
            ),
            cell_formatter.boolean_rule(
                com_shop_report_table_id,
                2,
                1000000,
                7,
                11,
                "=LT(H3;V3)",
                "green",
            ),
            cell_formatter.boolean_rule(
                com_shop_report_table_id,
                2,
                1000000,
                12,
                14,
                "=GT(M3;AA3)",
                "green",
            ),
            cell_formatter.boolean_rule(
                com_shop_report_table_id,
                2,
                1000000,
                12,
                14,
                "=LT(M3;AA3)",
                "red",
            ),
        ],
    }

    await cell_formatter.update(
        ss,
        cell_formatter.update_size(
            sheet_id,
            [150, 110, 110, 100, 60, 60, 30, 30, 30, 30, 30, 40, 30, 30],
        ),
        cell_formatter.merge(sheet_id, 1, 2, 15),
        cell_formatter.rotate(sheet_id, 2, 7, 15, 90),
        cell_formatter.update_borders(sheet_id, 0, 2, 0, 1000000, "SOLID"),
        cell_formatter.update_borders(sheet_id, 2, 1000000, 0, 1000000, "DASHED"),
        cell_formatter.text_equal_rule(
            sheet_id, 1, 1000000, 1, 1000000, "no", "yellow"
        ),
        cell_formatter.text_equal_rule(
            sheet_id, 1, 1000000, 1, 1000000, "Не найдено", "yellow"
        ),
        *boolean_rules[sheet_id],
    )
