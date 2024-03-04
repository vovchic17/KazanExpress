KazanExpressHelper
===

[![Python](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/vovchic17/static/main/src/badges/python312.json)](https://www.python.org/)
[![Aiogram](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com%2Fvovchic17%2Fstatic%2Fmain%2Fsrc%2Fbadges%2Faiogram341.json)](https://aiogram.dev/)
[![Aiohttp](https://img.shields.io/badge/aiohttp-v3.9.3-2c5bb4?logo=aiohttp)](https://docs.aiohttp.org/en/stable/)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)
[![Code linter: ruff](https://camo.githubusercontent.com/18c26428c337f9d641fa09b629a3a03b514e8ac84b57974a0ed7d1b38e14e060/68747470733a2f2f696d672e736869656c64732e696f2f656e64706f696e743f75726c3d68747470733a2f2f7261772e67697468756275736572636f6e74656e742e636f6d2f61737472616c2d73682f727566662f6d61696e2f6173736574732f62616467652f76322e6a736f6e)](https://github.com/charliermarsh/ruff)
[![Checked with mypy](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/vovchic17/static/main/src/badges/mypy.json)](https://mypy-lang.org/)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

**KazanExpressHelper** is a telegram-bot tool for [KazanExpress](https://kazanexpress.ru/) marketplace that analyzes the indicators of your products and comparing them with those of a competitor. This tool also provides notifications about stock, price and other indicators change.

![Preview](https://raw.githubusercontent.com/vovchic17/static/main/src/kehelper.gif)

## Installation

* Clone the repository
```
git clone https://github.com/vovchic17/KazanExpressHelper.git
```
* [Make a google service account](https://telegra.ph/Kak-sozdat-servisnyj-akkaunt-dlya-Google-Tablic-12-20) if you don't have one and download the json credentials
* Copy the [Google Spreadsheet](https://docs.google.com/spreadsheets/d/17SJAkJgNOnF84ZNQLk9Soq_2VM_3B0fXbBIj1Vma7kw/) and grant the service account editor access
* Rename and modify .env file
```
mv .env.example .env
```
* Install dependencies via poetry (`pip install poetry`)
```
poetry install
```
* Run the project
```
poetry run python ke_helper_bot
```

## License
Attribution-NonCommercial 4.0 International