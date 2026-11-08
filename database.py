import copy
import json
import os
import uuid
from datetime import datetime

import config

DEFAULT_SERVICES = [
    {"title": "Сделаю логотип для канала или проекта", "category": "Дизайн",
     "price": 50000, "author": "Азиз, 15 лет",
     "desc": "Нарисую логотип в Photoshop. Покажу 2 варианта, одну правку сделаю бесплатно.",
     "contact": "@aziz_design",
     "reviews": [
         {"author": "Дилшод", "rating": 5, "text": "Логотип получился отличный, сделал быстро!", "date": "01.09.2026"},
         {"author": "Севара", "rating": 4, "text": "Хорошая работа, одну правку внёс без проблем.", "date": "12.09.2026"},
     ]},
    {"title": "Помогу с английским: разговор и домашка", "category": "Языки",
     "price": 30000, "author": "Мадина, 16 лет",
     "desc": "Объясню грамматику простыми словами и потренируем разговорную речь.",
     "contact": "@madina_english",
     "reviews": [
         {"author": "Камола", "rating": 5, "text": "Всё объясняет очень понятно, после занятий стало легче.", "date": "20.09.2026"},
     ]},
    {"title": "Напишу Telegram-бота на Python", "category": "Программирование",
     "price": 120000, "author": "Тимур, 17 лет",
     "desc": "Простой бот: приветствие, кнопки, ответы на вопросы. Код объясню.",
     "contact": "@timur_code", "reviews": []},
    {"title": "Смонтирую видео для TikTok и YouTube", "category": "Видео",
     "price": 80000, "author": "Алина, 16 лет",
     "desc": "Нарезка, музыка, субтитры и эффекты. Срок: 1-2 дня.",
     "contact": "@alina_edit",
     "reviews": [
         {"author": "Жасур", "rating": 4, "text": "Монтаж динамичный, сдала в срок.", "date": "05.10.2026"},
     ]},
    {"title": "Объясню математику за 7-9 класс", "category": "Учёба",
     "price": 40000, "author": "Рустам, 17 лет",
     "desc": "Разберём сложные темы и подготовимся к контрольной.",
     "contact": "@rustam_math", "reviews": []},
]


def new_id():
    return uuid.uuid4().hex[:8]


def today():
    return datetime.now().strftime("%d.%m.%Y")


def format_price(price):
    return f"{price:,}".replace(",", " ") + " сум"


def plural(n, one, few, many):
    n = abs(n)
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


def make_default_data():
    data = {"services": copy.deepcopy(DEFAULT_SERVICES), "orders": []}
    ensure_structure(data)
    return data


def ensure_structure(data):
    data.setdefault("user_id", new_id())
    for service in data["services"]:
        service.setdefault("id", new_id())
        service.setdefault("owner_id", None)
        service.setdefault("reviews", [])
        for review in service["reviews"]:
            review.setdefault("owner_id", None)
    titles = {s["title"]: s["id"] for s in data["services"]}
    for order in data["orders"]:
        order.setdefault("id", new_id())
        order.setdefault("service_id", titles.get(order.get("title")))
    return data


def load_data(path=None):
    path = path or config.DATA_FILE
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data.get("services"), list) and isinstance(data.get("orders"), list):
            return ensure_structure(data)
    except FileNotFoundError:
        pass
    except (OSError, ValueError, AttributeError, KeyError):
        try:
            os.replace(path, path + ".broken")
        except OSError:
            pass
    return make_default_data()


def save_data(data, path=None):
    path = path or config.DATA_FILE
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
        return True
    except OSError:
        return False


def is_owner(data, service):
    owner = service.get("owner_id")
    return owner is not None and owner == data["user_id"]


def can_delete_review(data, review):
    owner = review.get("owner_id")
    return owner is not None and owner == data["user_id"]


def find_service(data, service_id):
    for service in data["services"]:
        if service["id"] == service_id:
            return service
    return None


def validate_service_form(title, price, author, desc, contact):
    if not (title and price and author and desc and contact):
        return "Заполни все поля.", None
    if not price.isdigit() or int(price) <= 0:
        return "Цена должна быть целым числом больше нуля.", None
    if len(title) > config.MAX_TITLE:
        return f"Название слишком длинное (максимум {config.MAX_TITLE} символов).", None
    if len(desc) > config.MAX_DESC:
        return f"Описание слишком длинное (максимум {config.MAX_DESC} символов).", None
    if len(author) > config.MAX_AUTHOR:
        return f"Имя слишком длинное (максимум {config.MAX_AUTHOR} символов).", None
    if len(contact) > config.MAX_CONTACT:
        return f"Контакт слишком длинный (максимум {config.MAX_CONTACT} символов).", None
    return None, int(price)


def add_service(data, title, category, price, author, desc, contact):
    service = {"id": new_id(), "title": title, "category": category, "price": price,
               "author": author, "desc": desc, "contact": contact,
               "owner_id": data["user_id"], "reviews": []}
    data["services"].insert(0, service)
    return service


def delete_service(data, service_id):
    service = find_service(data, service_id)
    if service is None:
        return False
    if not is_owner(data, service):
        raise PermissionError("Удалять можно только свои услуги.")
    data["services"].remove(service)
    return True


def filter_services(data, query="", category="Все", sort_by="Сначала новые"):
    query = query.strip().lower()
    found = []
    for service in data["services"]:
        if category == config.MY_FILTER:
            if not is_owner(data, service):
                continue
        elif category != "Все" and service["category"] != category:
            continue
        text = (service["title"] + " " + service["desc"] + " " + service["author"]).lower()
        if query and query not in text:
            continue
        found.append(service)

    if sort_by == "Сначала дешёвые":
        found.sort(key=lambda s: s["price"])
    elif sort_by == "Сначала дорогие":
        found.sort(key=lambda s: -s["price"])
    elif sort_by == "По рейтингу":
        found.sort(key=lambda s: average_rating(s), reverse=True)
    return found


def average_rating(service):
    reviews = service.get("reviews", [])
    if not reviews:
        return 0.0, 0
    return sum(r["rating"] for r in reviews) / len(reviews), len(reviews)


def add_review(data, service_id, author, rating, text):
    service = find_service(data, service_id)
    if service is None:
        raise ValueError("Эта услуга уже удалена.")
    if is_owner(data, service):
        raise ValueError("Нельзя оставить отзыв на собственную услугу.")
    author = author.strip()
    text = text.strip()
    if not author:
        raise ValueError("Введи своё имя.")
    if len(author) > config.MAX_AUTHOR:
        raise ValueError("Имя слишком длинное.")
    if rating not in (1, 2, 3, 4, 5):
        raise ValueError("Поставь оценку от 1 до 5 звёзд.")
    if len(text) < 3:
        raise ValueError("Напиши хотя бы пару слов в отзыве.")
    if len(text) > config.MAX_REVIEW:
        raise ValueError(f"Отзыв слишком длинный (максимум {config.MAX_REVIEW} символов).")
    for review in service["reviews"]:
        if review["author"].lower() == author.lower():
            raise ValueError("Ты уже оставлял отзыв на эту услугу.")
    review = {"author": author, "rating": rating, "text": text, "date": today(),
              "owner_id": data["user_id"]}
    service["reviews"].insert(0, review)
    return review


def delete_review(data, service, review):
    if not can_delete_review(data, review):
        raise PermissionError("Удалять можно только свои отзывы.")
    if review in service["reviews"]:
        service["reviews"].remove(review)
        return True
    return False


def add_order(data, customer, service):
    if is_owner(data, service):
        raise ValueError("Нельзя заказать собственную услугу.")
    order = {"id": new_id(), "customer": customer, "service_id": service["id"],
             "title": service["title"], "price": service["price"],
             "author": service["author"], "contact": service["contact"],
             "date": today()}
    data["orders"].append(order)
    return order


def delete_order(data, order_id):
    for order in data["orders"]:
        if order["id"] == order_id:
            data["orders"].remove(order)
            return True
    return False
