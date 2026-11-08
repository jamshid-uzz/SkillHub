import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import config as C
import database as db
from dialogs import AddServiceDialog, OrdersDialog, ReviewsDialog
from widgets import (Avatar, FlatButton, GradientBar, Pill, RoundedCard, ScrollableFrame,
                     load_image, make_entry, stars_text)


class SkillHub(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SkillHub - биржа услуг для школьников")
        self.geometry("1020x740")
        self.minsize(860, 560)
        self.configure(bg=C.BG)

        self.data = db.load_data()
        db.save_data(self.data)
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Все")
        self.sort_var = tk.StringVar(value=C.SORT_OPTIONS[0])
        self.chips = {}

        self.logo = load_image("logo_icon.png")
        self.app_icon = load_image("app_icon.png")
        if self.app_icon is not None:
            self.iconphoto(True, self.app_icon)

        self.setup_styles()
        self.build_header()
        self.build_filters()
        self.build_list()

        self.search_var.trace_add("write", lambda *args: self.show_services())
        self.sort_var.trace_add("write", lambda *args: self.show_services())
        self.category_var.trace_add("write", lambda *args: self.on_category_change())
        self.sync_chips()
        self.show_services()

    def setup_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        self.option_add("*TCombobox*Listbox.font", f"{{{C.FONT}}} 11")
        style.configure("Treeview", font=(C.FONT, 11), rowheight=34, background="white",
                        fieldbackground="white", borderwidth=0)
        style.configure("Treeview.Heading", font=(C.FONT, 11, "bold"), relief="flat",
                        background=C.PRIMARY_LIGHT, foreground=C.PRIMARY_DARK, padding=8)
        style.map("Treeview", background=[("selected", C.PRIMARY)],
                  foreground=[("selected", "white")])
        style.configure("TCombobox", fieldbackground="white", background="white",
                        bordercolor=C.BORDER, lightcolor=C.BORDER, darkcolor=C.BORDER,
                        arrowcolor=C.PRIMARY, padding=6)
        style.map("TCombobox", fieldbackground=[("readonly", "white")],
                  selectbackground=[("readonly", "white")],
                  selectforeground=[("readonly", C.TEXT)],
                  bordercolor=[("focus", C.PRIMARY)])
        style.configure("Vertical.TScrollbar", background="#C4B5FD", troughcolor=C.BG,
                        bordercolor=C.BG, lightcolor="#C4B5FD", darkcolor="#C4B5FD",
                        arrowcolor=C.PRIMARY, relief="flat", gripcount=0)
        style.map("Vertical.TScrollbar", background=[("active", "#A78BFA")])

    def save(self):
        if not db.save_data(self.data):
            messagebox.showerror("Ошибка", "Не удалось сохранить данные.", parent=self)

    def build_header(self):
        bar = GradientBar(self, 112, C.APP_NAME, C.APP_SUBTITLE, title_size=26,
                          logo=self.logo, title_split=5)
        bar.pack(fill="x")
        bar.add_button("+ Добавить услугу", lambda: AddServiceDialog(self), "white")
        bar.add_button("Мои заказы", lambda: OrdersDialog(self), "dark")

    def build_filters(self):
        top = tk.Frame(self, bg=C.BG)
        top.pack(fill="x", padx=26, pady=(20, 10))

        tk.Label(top, text="Поиск", bg=C.BG, fg=C.MUTED,
                 font=(C.FONT, 11, "bold")).pack(side="left", padx=(0, 10))
        make_entry(top, textvariable=self.search_var, size=12).pack(
            side="left", fill="x", expand=True, ipady=7)

        ttk.Combobox(top, textvariable=self.sort_var, state="readonly",
                     values=C.SORT_OPTIONS, font=(C.FONT, 11), width=16
                     ).pack(side="right")
        tk.Label(top, text="Сортировка", bg=C.BG, fg=C.MUTED,
                 font=(C.FONT, 11, "bold")).pack(side="right", padx=(18, 10))

        row = tk.Frame(self, bg=C.BG)
        row.pack(fill="x", padx=26, pady=(0, 6))
        for name in ["Все"] + C.CATEGORIES + [C.MY_FILTER]:
            chip = FlatButton(row, name, lambda n=name: self.category_var.set(n),
                              style="chip", size=10, padx=15, pady=5)
            chip.pack(side="left", padx=(0, 8))
            self.chips[name] = chip

        self.count_label = tk.Label(self, text="", bg=C.BG, fg=C.MUTED, font=(C.FONT, 10))
        self.count_label.pack(anchor="w", padx=28)

    def build_list(self):
        self.scroll = ScrollableFrame(self, bg=C.BG)
        self.scroll.pack(fill="both", expand=True, padx=26, pady=(6, 14))

    def sync_chips(self):
        current = self.category_var.get()
        for name, chip in self.chips.items():
            chip.set_style("chip_active" if name == current else "chip")

    def on_category_change(self):
        self.sync_chips()
        self.show_services()

    def show_services(self):
        self.scroll.clear()
        category = self.category_var.get()
        found = db.filter_services(self.data, self.search_var.get(), category,
                                   self.sort_var.get())
        word = db.plural(len(found), "услуга", "услуги", "услуг")
        self.count_label.config(text=f"Найдено: {len(found)} {word}")

        if not found:
            if category == C.MY_FILTER and not self.search_var.get().strip():
                message = "Ты ещё не добавил ни одной услуги.\nНажми «+ Добавить услугу» сверху."
            else:
                message = "Ничего не найдено. Попробуй другой запрос."
            tk.Label(self.scroll.inner, text=message, bg=C.BG, fg=C.MUTED,
                     font=(C.FONT, 13), justify="center").pack(pady=50)
            return
        for service in found:
            self.create_card(service)

    def create_card(self, service):
        tag_bg, tag_fg = C.CATEGORY_COLORS.get(service["category"], C.CATEGORY_COLORS["Другое"])
        own = db.is_owner(self.data, service)

        card = RoundedCard(self.scroll.inner, bg=C.BG)
        card.pack(fill="x", pady=(0, 8))
        body = card.inner

        Avatar(body, service["author"][:1].upper() or "?", tag_bg, tag_fg,
               size=52).pack(side="left", anchor="n")

        right = tk.Frame(body, bg=C.CARD_BG)
        right.pack(side="right", anchor="n", padx=(16, 0))
        tk.Label(right, text=db.format_price(service["price"]), bg=C.CARD_BG, fg=C.PRIMARY,
                 font=(C.FONT, 17, "bold")).pack(pady=(0, 10))
        if not own:
            FlatButton(right, "Заказать", lambda s=service: self.order_service(s),
                       min_width=132).pack()
        FlatButton(right, "Отзывы", lambda s=service: self.open_reviews(s), style="light",
                   min_width=132).pack(pady=6)
        if own:
            FlatButton(right, "Удалить", lambda s=service: self.delete_service(s),
                       style="danger", min_width=132).pack()

        text = tk.Frame(body, bg=C.CARD_BG)
        text.pack(side="left", fill="both", expand=True, padx=(16, 0))

        tags = tk.Frame(text, bg=C.CARD_BG)
        tags.pack(anchor="w")
        Pill(tags, service["category"], tag_bg, tag_fg).pack(side="left")
        if own:
            Pill(tags, "Моя услуга", C.SUCCESS_BG, C.SUCCESS).pack(side="left", padx=8)

        title = tk.Label(text, text=service["title"], bg=C.CARD_BG, fg=C.TEXT,
                         font=(C.FONT, 15, "bold"), wraplength=420, justify="left")
        title.pack(anchor="w", pady=(10, 3))
        desc = tk.Label(text, text=service["desc"], bg=C.CARD_BG, fg=C.MUTED,
                        font=(C.FONT, 11), wraplength=420, justify="left")
        desc.pack(anchor="w")
        tk.Label(text, text="Исполнитель: " + service["author"], bg=C.CARD_BG, fg=C.TEXT,
                 font=(C.FONT, 11)).pack(anchor="w", pady=(10, 0))

        avg, count = db.average_rating(service)
        rating_row = tk.Frame(text, bg=C.CARD_BG, cursor="hand2")
        rating_row.pack(anchor="w", pady=(4, 0))
        if count:
            word = db.plural(count, "отзыв", "отзыва", "отзывов")
            tk.Label(rating_row, text=stars_text(avg), bg=C.CARD_BG, fg=C.STAR,
                     font=(C.FONT, 14), cursor="hand2").pack(side="left")
            info = f"  {avg:.1f}  ·  {count} {word}"
        else:
            tk.Label(rating_row, text="☆☆☆☆☆", bg=C.CARD_BG, fg=C.STAR_EMPTY,
                     font=(C.FONT, 14), cursor="hand2").pack(side="left")
            info = "  Пока нет отзывов"
        tk.Label(rating_row, text=info, bg=C.CARD_BG, fg=C.MUTED, font=(C.FONT, 11),
                 cursor="hand2").pack(side="left")
        for widget in [rating_row] + rating_row.winfo_children():
            widget.bind("<Button-1>", lambda e, s=service: self.open_reviews(s))

        def on_width(width):
            wrap = max(220, width - 360)
            title.config(wraplength=wrap)
            desc.config(wraplength=wrap)

        card.set_on_width(on_width)

    def open_reviews(self, service):
        ReviewsDialog(self, service)

    def order_service(self, service):
        if db.is_owner(self.data, service):
            messagebox.showinfo("Нельзя", "Нельзя заказать собственную услугу.", parent=self)
            return
        name = simpledialog.askstring("Заказ", "Как тебя зовут?", parent=self)
        if name is None:
            return
        name = name.strip()
        if not name:
            messagebox.showwarning("Внимание", "Введи своё имя.", parent=self)
            return

        db.add_order(self.data, name, service)
        self.save()
        messagebox.showinfo(
            "Заказ оформлен",
            f"Спасибо, {name}!\n\nЗаказ отправлен.\n"
            f"Свяжись с исполнителем: {service['contact']}\n\n"
            "После выполнения заказа не забудь оставить отзыв.",
            parent=self)

    def delete_service(self, service):
        reviews = len(service["reviews"])
        message = f"Удалить услугу «{service['title']}»?"
        if reviews:
            message += f"\n\nВместе с ней удалятся отзывы ({reviews})."
        message += "\nЭто действие нельзя отменить."
        if not messagebox.askyesno("Удаление услуги", message, icon="warning", parent=self):
            return
        try:
            db.delete_service(self.data, service["id"])
        except PermissionError as error:
            messagebox.showwarning("Нельзя удалить", str(error), parent=self)
            return
        self.save()
        self.show_services()
