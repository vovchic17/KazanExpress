from gspread_asyncio import AsyncioGspreadSpreadsheet


async def update(spreadsheet: AsyncioGspreadSpreadsheet, *requests: list[dict]) -> None:
    await spreadsheet.batch_update(
        {"requests": [r for r_list in requests for r in r_list]}, nowait=True
    )


def update_size(sheet_id: int, col_sizes: list[int]) -> list[dict]:
    return [
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": col,
                    "endIndex": col + 1,
                },
                "properties": {"pixelSize": size},
                "fields": "pixelSize",
            }
        }
        for col, size in enumerate(col_sizes, 1)
    ]


def merge(
    sheet_id: int,
    row: int,
    start_col: int,
    end_col: int,
) -> list[dict]:
    return [
        {
            "mergeCells": {
                "mergeType": "MERGE_ALL",
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": row - 1,
                    "endRowIndex": row,
                    "startColumnIndex": start_col,
                    "endColumnIndex": end_col,
                },
            }
        }
    ]


def rotate(
    sheet_id: int, row: int, start_col: int, end_col: int, angle: int
) -> list[dict]:
    return [
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": row - 1,
                    "endRowIndex": row,
                    "startColumnIndex": start_col,
                    "endColumnIndex": end_col,
                },
                "cell": {"userEnteredFormat": {"textRotation": {"angle": angle}}},
                "fields": "userEnteredFormat/textRotation",
            }
        }
    ]


def update_borders(
    sheet_id: int,
    start_row: int,
    end_row: int,
    start_col: int,
    end_col: int,
    style: str,
) -> list[dict]:
    return [
        {
            "updateBorders": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": start_row,
                    "endRowIndex": end_row,
                    "startColumnIndex": start_col,
                    "endColumnIndex": end_col,
                },
                "bottom": {"style": style, "width": 1},
                "right": {"style": style, "width": 1},
                "left": {"style": style, "width": 1},
                "innerHorizontal": {"style": style, "width": 1},
                "innerVertical": {"style": style, "width": 1},
            }
        }
    ]


cond_rule_colors = {
    "green": {"red": 0.72, "green": 0.87, "blue": 0.81},
    "yellow": {"red": 0.95, "green": 0.76, "blue": 0.2},
    "red": {"red": 0.9, "green": 0.49, "blue": 0.45},
}


def boolean_rule(
    sheet_id: int,
    start_row: int,
    end_row: int,
    start_col: int,
    end_col: int,
    formula: str,
    color: str,
) -> list[dict]:
    return [
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": sheet_id,
                            "startRowIndex": start_row,
                            "endRowIndex": end_row,
                            "startColumnIndex": start_col,
                            "endColumnIndex": end_col,
                        }
                    ],
                    "booleanRule": {
                        "condition": {
                            "type": "CUSTOM_FORMULA",
                            "values": [{"userEnteredValue": formula}],
                        },
                        "format": {"backgroundColor": cond_rule_colors[color]},
                    },
                }
            }
        }
    ]


def text_equal_rule(
    sheet_id: int,
    start_row: int,
    end_row: int,
    start_col: int,
    end_col: int,
    text: str,
    color: str,
) -> list[dict]:
    return [
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": sheet_id,
                            "startRowIndex": start_row,
                            "endRowIndex": end_row,
                            "startColumnIndex": start_col,
                            "endColumnIndex": end_col,
                        }
                    ],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": text}],
                        },
                        "format": {"backgroundColor": cond_rule_colors[color]},
                    },
                }
            }
        }
    ]
