from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Config class"""

    BOT_TOKEN: str
    ADMINS: list[int]
    GOOGLE_SHEETS_API_CREDS: str
    SPREADSHEET_KEY: str
    DAILY_TASK_TABLE_ID: int
    DAILY_REPORT_TABLE_ID: int
    MY_SHOP_TASK_TABLE_ID: int
    MY_SHOP_REPORT_TABLE_ID: int
    COM_SHOP_TASK_TABLE_ID: int
    COM_SHOP_REPORT_TABLE_ID: int
    MY_NOTIF_TABLE_ID: int
    MY_STOCK_NOTIF_TABLE_ID: int
    COM_NOTIF_TABLE_ID: int
    COM_STOCK_NOTIF_TABLE_ID: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


config = Settings()
