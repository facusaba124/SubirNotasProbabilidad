import json
import os

SETTINGS_FILE = "settings.json"


def cargar_settings():

    if not os.path.exists(SETTINGS_FILE):

        return {
            "spreadsheet_url": "",
            "spreadsheet_name": ""
        }

    with open(
        SETTINGS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        settings = json.load(f)

    settings.setdefault("spreadsheet_url", "")
    settings.setdefault("spreadsheet_name", "")

    return settings


def guardar_settings(settings):

    with open(
        SETTINGS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            settings,
            f,
            indent=4,
            ensure_ascii=False
        )