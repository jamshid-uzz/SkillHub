import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skillhub_data.json")
CATEGORIES = ["Дизайн", "Программирование", "Языки", "Видео", "Учёба", "Другое"]

BG = "#F3F4F8"
CARD_BG = "#FFFFFF"
PRIMARY = "#4F46E5"
PRIMARY_DARK = "#3730A3"
TEXT = "#1F2937"
MUTED = "#6B7280"
TAG_BG = "#E0E7FF"

FONT = "Segoe UI"

DEFAULT_DATA = {
    "services": [
        {"title": "Сделаю логотип для канала или проекта", "category": "Дизайн",
         "price": 50000, "author": "Азиз, 15 лет",
         "desc": "Нарисую логотип в Photoshop. Покажу 2 варианта, одну правку сделаю бесплатно.",
         "contact": "@aziz_design"},
        {"title": "Помогу с английским: разговор и домашка", "category": "Языки",
         "price": 30000, "author": "Мадина, 16 лет",
         "desc": "Объясню грамматику простыми словами и потренируем разговорную речь.",
         "contact": "@madina_english"},
        {"title": "Напишу Telegram-бота на Python", "category": "Программирование",
         "price": 120000, "author": "Тимур, 17 лет",
         "desc": "Простой бот: приветствие, кнопки, ответы на вопросы. Код объясню.",
         "contact": "@timur_code"},
        {"title": "Смонтирую видео для TikTok и YouTube", "category": "Видео",
         "price": 80000, "author": "Алина, 16 лет",
         "desc": "Нарезка, музыка, субтитры и эффекты. Срок: 1-2 дня.",
         "contact": "@alina_edit"},
        {"title": "Объясню математику за 7-9 класс", "category": "Учёба",
         "price": 40000, "author": "Рустам, 17 лет",
         "desc": "Разберём сложные темы и подготовимся к контрольной.",
         "contact": "@rustam_math"},
    ],
    "orders": [],
}


def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "services" in data and "orders" in data:
            return data
    except (OSError, ValueError):
        pass
    return json.loads(json.dumps(DEFAULT_DATA))


def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        messagebox.showerror("Ошибка", "Не удалось сохранить данные.")


def format_price(price):
    return f"{price:,}".replace(",", " ") + " сум"


class SkillHub(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SkillHub - биржа услуг для школьников")
        self.geometry("900x650")
        self.minsize(700, 500)
        self.configure(bg=BG)

        self.data = load_data()
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Все")

        self.build_header()
        self.build_filters()
        self.build_list()


        self.search_var.trace_add("write", lambda *args: self.show_services())
        self.category_var.trace_add("write", lambda *args: self.show_services())

        self.show_services()


    def build_header(self):
        header = tk.Frame(self, bg=PRIMARY)
        header.pack(fill="x")

        title_box = tk.Frame(header, bg=PRIMARY)
        title_box.pack(side="left", padx=20, pady=12)
        tk.Label(title_box, text="SkillHub", bg=PRIMARY, fg="white",
                 font=(FONT, 22, "bold")).pack(anchor="w")
        tk.Label(title_box, text="Услуги от школьников и студентов", bg=PRIMARY,
                 fg="#C7D2FE", font=(FONT, 11)).pack(anchor="w")

        buttons = tk.Frame(header, bg=PRIMARY)
        buttons.pack(side="right", padx=20)
        self.make_button(buttons, "+ Добавить услугу", self.open_add_window,
                         bg="white", fg=PRIMARY).pack(side="left", padx=5)
        self.make_button(buttons, "Мои заказы", self.open_orders_window,
                         bg=PRIMARY_DARK, fg="white").pack(side="left", padx=5)


    def build_filters(self):
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=20, pady=(15, 5))

        tk.Label(bar, text="Поиск:", bg=BG, fg=TEXT, font=(FONT, 12)).pack(side="left")
        tk.Entry(bar, textvariable=self.search_var, font=(FONT, 12), width=28,
                 relief="solid", bd=1).pack(side="left", padx=(8, 20), ipady=3)

        tk.Label(bar, text="Категория:", bg=BG, fg=TEXT, font=(FONT, 12)).pack(side="left")
        box = ttk.Combobox(bar, textvariable=self.category_var, state="readonly",
                           values=["Все"] + CATEGORIES, font=(FONT, 12), width=18)
        box.pack(side="left", padx=8)

        self.count_label = tk.Label(bar, text="", bg=BG, fg=MUTED, font=(FONT, 11))
        self.count_label.pack(side="right")


    def build_list(self):
        wrapper = tk.Frame(self, bg=BG)
        wrapper.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(wrapper, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(wrapper, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.list_frame = tk.Frame(self.canvas, bg=BG)
        self.window_id = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")


        self.list_frame.bind("<Configure>",
                             lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfig(self.window_id, width=e.width))


        self.bind_all("<MouseWheel>", self.on_mousewheel)
        self.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-event.delta / 120), "units")


    def make_button(self, parent, text, command, bg=PRIMARY, fg="white"):
        return tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                         font=(FONT, 11, "bold"), relief="flat", cursor="hand2",
                         activebackground=PRIMARY_DARK, activeforeground="white",
                         padx=14, pady=6)


    def show_services(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        query = self.search_var.get().strip().lower()
        category = self.category_var.get()

        found = []
        for service in self.data["services"]:
            if category != "Все" and service["category"] != category:
                continue
            text = (service["title"] + " " + service["desc"] + " " + service["author"]).lower()
            if query and query not in text:
                continue
            found.append(service)

        self.count_label.config(text=f"Найдено услуг: {len(found)}")

        if not found:
            tk.Label(self.list_frame, text="Ничего не найдено. Попробуй другой запрос.",
                     bg=BG, fg=MUTED, font=(FONT, 13)).pack(pady=40)
            return

        for service in found:
            self.create_card(service)

    def create_card(self, service):
        card = tk.Frame(self.list_frame, bg=CARD_BG, highlightbackground="#E5E7EB",
                        highlightthickness=1)
        card.pack(fill="x", pady=6)

        left = tk.Frame(card, bg=CARD_BG)
        left.pack(side="left", fill="both", expand=True, padx=16, pady=12)

        tk.Label(left, text=service["category"], bg=TAG_BG, fg=PRIMARY,
                 font=(FONT, 10, "bold"), padx=8, pady=2).pack(anchor="w")
        tk.Label(left, text=service["title"], bg=CARD_BG, fg=TEXT,
                 font=(FONT, 14, "bold"), wraplength=560, justify="left").pack(anchor="w", pady=(6, 2))
        tk.Label(left, text=service["desc"], bg=CARD_BG, fg=MUTED,
                 font=(FONT, 11), wraplength=560, justify="left").pack(anchor="w")
        tk.Label(left, text="Исполнитель: " + service["author"], bg=CARD_BG, fg=TEXT,
                 font=(FONT, 11)).pack(anchor="w", pady=(6, 0))

        right = tk.Frame(card, bg=CARD_BG)
        right.pack(side="right", padx=16, pady=12)
        tk.Label(right, text=format_price(service["price"]), bg=CARD_BG, fg=PRIMARY,
                 font=(FONT, 15, "bold")).pack(pady=(0, 8))
        self.make_button(right, "Заказать", lambda s=service: self.order_service(s)).pack()


    def order_service(self, service):
        name = simpledialog.askstring("Заказ", "Как тебя зовут?", parent=self)
        if name is None:
            return
        name = name.strip()
        if not name:
            messagebox.showwarning("Внимание", "Введи своё имя.")
            return

        self.data["orders"].append({
            "customer": name,
            "title": service["title"],
            "price": service["price"],
            "author": service["author"],
            "contact": service["contact"],
        })
        save_data(self.data)
        messagebox.showinfo(
            "Заказ оформлен",
            f"Спасибо, {name}!\n\nЗаказ отправлен.\n"
            f"Свяжись с исполнителем: {service['contact']}")


    def open_orders_window(self):
        win = tk.Toplevel(self)
        win.title("Мои заказы")
        win.geometry("560x420")
        win.configure(bg=BG)

        tk.Label(win, text="Мои заказы", bg=BG, fg=TEXT,
                 font=(FONT, 18, "bold")).pack(pady=(15, 5))

        orders = self.data["orders"]
        if not orders:
            tk.Label(win, text="Пока заказов нет.", bg=BG, fg=MUTED,
                     font=(FONT, 12)).pack(pady=30)
            return

        total = sum(o["price"] for o in orders)
        tk.Label(win, text=f"Всего заказов: {len(orders)}   |   Сумма: {format_price(total)}",
                 bg=BG, fg=MUTED, font=(FONT, 11)).pack(pady=(0, 10))

        listbox = tk.Listbox(win, font=(FONT, 11), bd=0, highlightthickness=1,
                             highlightbackground="#E5E7EB", activestyle="none")
        listbox.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        for i, o in enumerate(orders, start=1):
            listbox.insert("end", f"{i}. {o['title']} - {format_price(o['price'])} ({o['author']})")


    def open_add_window(self):
        win = tk.Toplevel(self)
        win.title("Новая услуга")
        win.geometry("460x560")
        win.configure(bg=BG)
        win.grab_set()

        tk.Label(win, text="Добавить свою услугу", bg=BG, fg=TEXT,
                 font=(FONT, 16, "bold")).pack(pady=(15, 10))

        form = tk.Frame(win, bg=BG)
        form.pack(fill="x", padx=25)

        def add_field(label):
            tk.Label(form, text=label, bg=BG, fg=TEXT, font=(FONT, 11)).pack(anchor="w", pady=(8, 2))
            entry = tk.Entry(form, font=(FONT, 12), relief="solid", bd=1)
            entry.pack(fill="x", ipady=3)
            return entry

        title_entry = add_field("Название услуги")

        tk.Label(form, text="Категория", bg=BG, fg=TEXT, font=(FONT, 11)).pack(anchor="w", pady=(8, 2))
        cat_box = ttk.Combobox(form, values=CATEGORIES, state="readonly", font=(FONT, 12))
        cat_box.current(0)
        cat_box.pack(fill="x")

        price_entry = add_field("Цена в сумах (только цифры)")
        author_entry = add_field("Твоё имя и возраст (например: Азиз, 15 лет)")
        desc_entry = add_field("Короткое описание")
        contact_entry = add_field("Контакт (Telegram, например @username)")

        def save():
            title = title_entry.get().strip()
            price = price_entry.get().strip()
            author = author_entry.get().strip()
            desc = desc_entry.get().strip()
            contact = contact_entry.get().strip()

            if not (title and price and author and desc and contact):
                messagebox.showwarning("Внимание", "Заполни все поля.", parent=win)
                return
            if not price.isdigit() or int(price) <= 0:
                messagebox.showwarning("Внимание", "Цена должна быть числом больше нуля.", parent=win)
                return

            self.data["services"].insert(0, {
                "title": title, "category": cat_box.get(), "price": int(price),
                "author": author, "desc": desc, "contact": contact,
            })
            save_data(self.data)
            self.show_services()
            win.destroy()
            messagebox.showinfo("Готово", "Услуга добавлена!")

        self.make_button(win, "Опубликовать", save).pack(pady=20)


if __name__ == "__main__":
    app = SkillHub()
    app.mainloop()
