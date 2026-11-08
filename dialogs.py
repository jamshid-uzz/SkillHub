import tkinter as tk
from tkinter import ttk, messagebox

import config as C
import database as db
from widgets import (Avatar, FlatButton, GradientBar, RoundedCard, ScrollableFrame,
                     StarPicker, make_entry, make_text, stars_text)


class BaseDialog(tk.Toplevel):
    def __init__(self, parent, title, width, height, modal=True):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=C.BG)
        self.minsize(width - 80, height - 120)
        self.transient(parent)
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.geometry(f"{width}x{height}+{max(x, 0)}+{max(y, 30)}")
        if modal:
            self.grab_set()


def field_label(parent, text, bg=C.BG):
    return tk.Label(parent, text=text, bg=bg, fg=C.MUTED, font=(C.FONT, 10, "bold"))


class AddServiceDialog(BaseDialog):
    def __init__(self, app):
        super().__init__(app, "Новая услуга", 500, 740)
        self.app = app

        GradientBar(self, 92, "Новая услуга", "Расскажи, что ты умеешь и сколько это стоит",
                    title_size=18).pack(fill="x")

        form = tk.Frame(self, bg=C.BG)
        form.pack(fill="x", padx=30, pady=(4, 0))

        self.title_entry = self._field(form, "НАЗВАНИЕ УСЛУГИ")

        field_label(form, "КАТЕГОРИЯ").pack(anchor="w", pady=(12, 3))
        self.category_box = ttk.Combobox(form, values=C.CATEGORIES, state="readonly",
                                         font=(C.FONT, 12))
        self.category_box.current(0)
        self.category_box.pack(fill="x")

        self.price_entry = self._field(form, "ЦЕНА В СУМАХ (ТОЛЬКО ЦИФРЫ)")
        self.author_entry = self._field(form, "ТВОЁ ИМЯ И ВОЗРАСТ (НАПРИМЕР: АЗИЗ, 15 ЛЕТ)")
        self.contact_entry = self._field(form, "КОНТАКТ (TELEGRAM, НАПРИМЕР @USERNAME)")

        field_label(form, "КОРОТКОЕ ОПИСАНИЕ").pack(anchor="w", pady=(12, 3))
        self.desc_text = make_text(form, height=4)
        self.desc_text.pack(fill="x")

        FlatButton(self, "Опубликовать", self.save, size=12, padx=36, pady=10
                   ).pack(pady=20)
        self.title_entry.focus_set()

    def _field(self, form, label):
        field_label(form, label).pack(anchor="w", pady=(12, 3))
        entry = make_entry(form)
        entry.pack(fill="x", ipady=6)
        return entry

    def save(self):
        title = self.title_entry.get().strip()
        price = self.price_entry.get().strip()
        author = self.author_entry.get().strip()
        desc = self.desc_text.get("1.0", "end").strip()
        contact = self.contact_entry.get().strip()

        error, price_value = db.validate_service_form(title, price, author, desc, contact)
        if error:
            messagebox.showwarning("Внимание", error, parent=self)
            return

        db.add_service(self.app.data, title, self.category_box.get(), price_value,
                       author, desc, contact)
        self.app.save()
        self.app.show_services()
        self.app.scroll.scroll_top()
        self.destroy()
        messagebox.showinfo("Готово", "Услуга добавлена! Её можно будет удалить в любой момент.",
                            parent=self.app)


class ReviewsDialog(BaseDialog):
    def __init__(self, app, service, default_author=""):
        super().__init__(app, "Отзывы", 620, 740)
        self.app = app
        self.service_id = service["id"]

        self.bar = GradientBar(self, 100, service["title"], "", title_size=14,
                               subtitle_fg="#FDE68A", title_width=540)
        self.bar.pack(fill="x")

        form_card = RoundedCard(self, bg=C.BG, radius=16, pad=14)
        form_card.pack(side="bottom", fill="x", padx=16, pady=(0, 16))
        form = form_card.inner

        if db.is_owner(app.data, service):
            tk.Label(form, text="Это твоя услуга, поэтому оставить на неё отзыв нельзя.",
                     bg=C.CARD_BG, fg=C.MUTED, font=(C.FONT, 11), wraplength=480,
                     justify="left").pack(anchor="w", pady=6)
        else:
            tk.Label(form, text="Оставить отзыв", bg=C.CARD_BG, fg=C.TEXT,
                     font=(C.FONT, 13, "bold")).pack(anchor="w")

            row = tk.Frame(form, bg=C.CARD_BG)
            row.pack(fill="x", pady=(8, 0))
            field_label(row, "ИМЯ", bg=C.CARD_BG).pack(side="left")
            self.name_entry = make_entry(row, width=16)
            self.name_entry.pack(side="left", padx=(8, 18), ipady=4)
            self.name_entry.insert(0, default_author)
            field_label(row, "ОЦЕНКА", bg=C.CARD_BG).pack(side="left")
            self.stars = StarPicker(row, bg=C.CARD_BG, size=22)
            self.stars.pack(side="left", padx=6)

            self.text = make_text(form, height=3, size=11)
            self.text.pack(fill="x", pady=10)
            FlatButton(form, "Отправить отзыв", self.submit).pack(anchor="e")

        self.scroll = ScrollableFrame(self, bg=C.BG)
        self.scroll.pack(fill="both", expand=True, padx=16, pady=12)

        self.refresh()

    def service(self):
        return db.find_service(self.app.data, self.service_id)

    def refresh(self):
        service = self.service()
        if service is None:
            self.destroy()
            return
        avg, count = db.average_rating(service)
        if count:
            word = db.plural(count, "отзыв", "отзыва", "отзывов")
            self.bar.set_subtitle(f"{stars_text(avg)}  {avg:.1f} из 5  ·  {count} {word}")
        else:
            self.bar.set_subtitle("Пока нет отзывов. Будь первым!")

        self.scroll.clear()
        if not count:
            tk.Label(self.scroll.inner, text="Здесь пока пусто.", bg=C.BG, fg=C.MUTED,
                     font=(C.FONT, 12)).pack(pady=30)
        for review in service["reviews"]:
            self._review_card(review)

    def _review_card(self, review):
        card = RoundedCard(self.scroll.inner, bg=C.BG, radius=14, pad=12)
        card.pack(fill="x", pady=(0, 6))
        body = card.inner

        top = tk.Frame(body, bg=C.CARD_BG)
        top.pack(fill="x")
        Avatar(top, review["author"][:1].upper() or "?", C.PRIMARY_LIGHT, C.PRIMARY,
               size=38).pack(side="left")
        names = tk.Frame(top, bg=C.CARD_BG)
        names.pack(side="left", padx=10)
        tk.Label(names, text=review["author"], bg=C.CARD_BG, fg=C.TEXT,
                 font=(C.FONT, 12, "bold")).pack(anchor="w")
        tk.Label(names, text=review.get("date", ""), bg=C.CARD_BG, fg=C.MUTED,
                 font=(C.FONT, 10)).pack(anchor="w")
        tk.Label(top, text=stars_text(review["rating"]), bg=C.CARD_BG, fg=C.STAR,
                 font=(C.FONT, 14)).pack(side="right")

        text = tk.Label(body, text=review["text"], bg=C.CARD_BG, fg=C.TEXT,
                        font=(C.FONT, 11), wraplength=440, justify="left")
        text.pack(anchor="w", pady=(8, 0))
        card.set_on_width(lambda w, label=text: label.config(wraplength=max(200, w - 60)))

        if db.can_delete_review(self.app.data, review):
            FlatButton(body, "Удалить мой отзыв", lambda r=review: self.delete_review(r),
                       style="danger", size=9, padx=12, pady=3).pack(anchor="e", pady=(8, 0))

    def submit(self):
        try:
            db.add_review(self.app.data, self.service_id, self.name_entry.get(),
                          self.stars.get(), self.text.get("1.0", "end"))
        except ValueError as error:
            messagebox.showwarning("Внимание", str(error), parent=self)
            return
        self.app.save()
        self.text.delete("1.0", "end")
        self.stars.set(0)
        self.refresh()
        self.scroll.scroll_top()
        self.app.show_services()

    def delete_review(self, review):
        if not messagebox.askyesno("Удаление отзыва", "Удалить этот отзыв?", parent=self):
            return
        try:
            db.delete_review(self.app.data, self.service(), review)
        except PermissionError as error:
            messagebox.showwarning("Нельзя удалить", str(error), parent=self)
            return
        self.app.save()
        self.refresh()
        self.app.show_services()


class OrdersDialog(BaseDialog):
    def __init__(self, app):
        super().__init__(app, "Мои заказы", 740, 520, modal=False)
        self.app = app

        self.bar = GradientBar(self, 88, "Мои заказы", "", title_size=18)
        self.bar.pack(fill="x")

        buttons = tk.Frame(self, bg=C.BG)
        buttons.pack(side="bottom", fill="x", padx=20, pady=(0, 18))
        FlatButton(buttons, "Оставить отзыв", self.review_selected).pack(side="left")
        FlatButton(buttons, "Удалить заказ", self.delete_selected, style="danger"
                   ).pack(side="left", padx=10)
        FlatButton(buttons, "Закрыть", self.destroy, style="light").pack(side="right")

        holder = tk.Frame(self, bg=C.BORDER)
        holder.pack(fill="both", expand=True, padx=20, pady=16)
        table = tk.Frame(holder, bg="white")
        table.pack(fill="both", expand=True, padx=1, pady=1)

        columns = ("num", "title", "author", "price")
        self.tree = ttk.Treeview(table, columns=columns, show="headings", selectmode="browse")
        for name, text, width, anchor in (("num", "№", 44, "center"),
                                          ("title", "Услуга", 320, "w"),
                                          ("author", "Исполнитель", 160, "w"),
                                          ("price", "Цена", 120, "e")):
            self.tree.heading(name, text=text)
            self.tree.column(name, width=width, anchor=anchor)
        scrollbar = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        self.refresh()

    def refresh(self):
        orders = self.app.data["orders"]
        self.tree.delete(*self.tree.get_children())
        for i, order in enumerate(orders, start=1):
            self.tree.insert("", "end", iid=order["id"],
                             values=(i, order["title"], order["author"],
                                     db.format_price(order["price"])))
        total = sum(o["price"] for o in orders)
        if orders:
            self.bar.set_subtitle(
                f"Всего заказов: {len(orders)}   ·   Сумма: {db.format_price(total)}")
        else:
            self.bar.set_subtitle("Пока заказов нет. Выбери услугу на главном экране.")

    def selected_order(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Подсказка", "Сначала выбери заказ в списке.", parent=self)
            return None
        for order in self.app.data["orders"]:
            if order["id"] == selection[0]:
                return order
        return None

    def review_selected(self):
        order = self.selected_order()
        if order is None:
            return
        service = db.find_service(self.app.data, order.get("service_id"))
        if service is None:
            messagebox.showinfo("Услуга удалена",
                                "Эта услуга больше не доступна, отзыв оставить нельзя.",
                                parent=self)
            return
        ReviewsDialog(self.app, service, default_author=order["customer"])

    def delete_selected(self):
        order = self.selected_order()
        if order is None:
            return
        if not messagebox.askyesno("Удаление заказа",
                                   f"Удалить заказ «{order['title']}» из списка?", parent=self):
            return
        db.delete_order(self.app.data, order["id"])
        self.app.save()
        self.refresh()
