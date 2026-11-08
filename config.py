import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "skillhub_data.json")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

APP_NAME = "SkillHub"
APP_SUBTITLE = "Услуги от школьников и студентов"

CATEGORIES = ["Дизайн", "Программирование", "Языки", "Видео", "Учёба", "Другое"]
SORT_OPTIONS = ["Сначала новые", "Сначала дешёвые", "Сначала дорогие", "По рейтингу"]

MAX_TITLE = 80
MAX_DESC = 300
MAX_AUTHOR = 40
MAX_CONTACT = 40
MAX_REVIEW = 400

FONT = "Segoe UI" if sys.platform.startswith("win") else "Helvetica"

MY_FILTER = "Мои услуги"

BG = "#F6F5FB"
CARD_BG = "#FFFFFF"
PRIMARY = "#6D28D9"
PRIMARY_DARK = "#5B21B6"
PRIMARY_LIGHT = "#EDE9FE"
TEXT = "#1E1B3A"
MUTED = "#6B6A85"
BORDER = "#E4E1F2"
SHADOW = "#E3DFF3"
STAR = "#F59E0B"
STAR_EMPTY = "#D9D6E8"
DANGER = "#B91C1C"
DANGER_BG = "#FEE2E2"
SUCCESS = "#15803D"
SUCCESS_BG = "#DCFCE7"

GRADIENT = ("#4F46E5", "#7C3AED", "#C026D3")

CATEGORY_COLORS = {
    "Дизайн": ("#FCE7F3", "#BE185D"),
    "Программирование": ("#DBEAFE", "#1D4ED8"),
    "Языки": ("#DCFCE7", "#15803D"),
    "Видео": ("#FEF3C7", "#B45309"),
    "Учёба": ("#EDE9FE", "#6D28D9"),
    "Другое": ("#E5E7EB", "#374151"),
}
