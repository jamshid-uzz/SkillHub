import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

import config as C

BUTTON_STYLES = {
    "primary": (C.PRIMARY, "white", C.PRIMARY_DARK, C.PRIMARY),
    "light": (C.PRIMARY_LIGHT, C.PRIMARY_DARK, "#DDD6FE", C.PRIMARY_LIGHT),
    "danger": (C.DANGER_BG, C.DANGER, "#FECACA", C.DANGER_BG),
    "white": ("white", C.PRIMARY_DARK, "#F5F3FF", "white"),
    "dark": ("#3730A3", "white", "#312E81", "#3730A3"),
    "chip": ("white", C.MUTED, C.PRIMARY_LIGHT, C.BORDER),
    "chip_active": (C.PRIMARY, "white", C.PRIMARY_DARK, C.PRIMARY),
}


def hex_to_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def gradient_color(stops, t):
    t = max(0.0, min(1.0, t))
    segments = len(stops) - 1
    pos = t * segments
    i = min(int(pos), segments - 1)
    local = pos - i
    a, b = hex_to_rgb(stops[i]), hex_to_rgb(stops[i + 1])
    return "#%02x%02x%02x" % tuple(int(a[k] + (b[k] - a[k]) * local) for k in range(3))


def round_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    points = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
              x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
              x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def load_image(name):
    try:
        return tk.PhotoImage(file=os.path.join(C.ASSETS_DIR, name))
    except tk.TclError:
        return None


def stars_text(rating):
    full = max(0, min(5, int(round(rating))))
    return "★" * full + "☆" * (5 - full)


def make_entry(parent, textvariable=None, size=12, width=None):
    entry = tk.Entry(parent, font=(C.FONT, size), relief="flat", bd=0, bg="white",
                     fg=C.TEXT, insertbackground=C.TEXT, highlightthickness=1,
                     highlightbackground=C.BORDER, highlightcolor=C.PRIMARY,
                     textvariable=textvariable)
    if width:
        entry.configure(width=width)
    return entry


def make_text(parent, height=3, size=12):
    return tk.Text(parent, height=height, font=(C.FONT, size), relief="flat", bd=0,
                   bg="white", fg=C.TEXT, insertbackground=C.TEXT, wrap="word",
                   highlightthickness=1, highlightbackground=C.BORDER,
                   highlightcolor=C.PRIMARY, padx=6, pady=4)


class Pill(tk.Canvas):
    def __init__(self, parent, text, fill, fg, size=10, padx=11, pady=3, outline=None,
                 bg=None, bold=True, min_width=0):
        font = tkfont.Font(root=parent.winfo_toplevel(), family=C.FONT, size=size,
                           weight="bold" if bold else "normal")
        width = max(font.measure(text) + 2 * padx, min_width)
        height = font.metrics("linespace") + 2 * pady
        super().__init__(parent, width=width, height=height,
                         bg=bg or parent.cget("bg"), highlightthickness=0)
        self._pill_font = font
        self._shape = round_rect(self, 1, 1, width - 1, height - 1, (height - 2) / 2,
                                 fill=fill, outline=outline or fill)
        self._caption = self.create_text(width / 2, height / 2, text=text, fill=fg, font=font)

    def recolor(self, fill, fg, outline=None):
        self.itemconfigure(self._shape, fill=fill, outline=outline or fill)
        self.itemconfigure(self._caption, fill=fg)


class FlatButton(Pill):
    def __init__(self, parent, text, command, style="primary", size=11, padx=18, pady=7,
                 bg=None, min_width=0):
        fill, fg, hover, outline = BUTTON_STYLES[style]
        super().__init__(parent, text, fill, fg, size=size, padx=padx, pady=pady,
                         outline=outline, bg=bg, min_width=min_width)
        self._command = command
        self._style = style
        self.configure(cursor="hand2")
        self.bind("<Enter>", lambda e: self._paint(True))
        self.bind("<Leave>", lambda e: self._paint(False))
        self.bind("<Button-1>", lambda e: self._command())

    def _paint(self, hovered):
        fill, fg, hover, outline = BUTTON_STYLES[self._style]
        self.recolor(hover if hovered else fill, fg, outline)

    def set_style(self, style):
        self._style = style
        self._paint(False)


class Avatar(tk.Canvas):
    def __init__(self, parent, letter, fill, fg, size=48, bg=None):
        super().__init__(parent, width=size, height=size, bg=bg or parent.cget("bg"),
                         highlightthickness=0)
        self.create_oval(1, 1, size - 1, size - 1, fill=fill, outline=fill)
        self.create_text(size / 2, size / 2, text=letter, fill=fg,
                         font=(C.FONT, int(size * 0.38), "bold"))


class StarPicker(tk.Frame):
    def __init__(self, parent, bg=C.BG, size=24):
        super().__init__(parent, bg=bg)
        self.value = 0
        self.labels = []
        for i in range(1, 6):
            label = tk.Label(self, text="☆", font=(C.FONT, size), fg=C.STAR_EMPTY,
                             bg=bg, cursor="hand2")
            label.pack(side="left")
            label.bind("<Button-1>", lambda e, v=i: self.set(v))
            label.bind("<Enter>", lambda e, v=i: self._paint(v))
            label.bind("<Leave>", lambda e: self._paint(self.value))
            self.labels.append(label)

    def set(self, value):
        self.value = value
        self._paint(value)

    def get(self):
        return self.value

    def _paint(self, upto):
        for i, label in enumerate(self.labels, start=1):
            if i <= upto:
                label.config(text="★", fg=C.STAR)
            else:
                label.config(text="☆", fg=C.STAR_EMPTY)


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, bg=C.BG):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg=bg)
        self._win_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfig(self._win_id, width=e.width))

        top = self.winfo_toplevel()
        top.bind("<MouseWheel>", self._on_wheel, add="+")
        top.bind("<Button-4>", self._on_wheel, add="+")
        top.bind("<Button-5>", self._on_wheel, add="+")

    def _on_wheel(self, event):
        try:
            under = self.winfo_containing(event.x_root, event.y_root)
        except (tk.TclError, KeyError):
            return
        if under is None or not str(under).startswith(str(self)):
            return
        if event.num == 4:
            step = -1
        elif event.num == 5:
            step = 1
        elif sys.platform == "darwin":
            step = -event.delta
        else:
            step = int(-event.delta / 120)
        self.canvas.yview_scroll(step, "units")

    def clear(self):
        for widget in self.inner.winfo_children():
            widget.destroy()

    def scroll_top(self):
        self.canvas.yview_moveto(0)


class RoundedCard(tk.Canvas):
    def __init__(self, parent, bg=C.BG, fill=C.CARD_BG, radius=18, pad=18):
        super().__init__(parent, bg=bg, highlightthickness=0, height=40)
        self._fill = fill
        self._radius = radius
        self._pad = pad
        self._on_width = None
        self._last_width = 0
        self.inner = tk.Frame(self, bg=fill)
        self._win_id = self.create_window(2 + pad, 2 + pad, window=self.inner, anchor="nw")
        self.bind("<Configure>", self._redraw)
        self.inner.bind("<Configure>", self._redraw)

    def set_on_width(self, callback):
        self._on_width = callback

    def _redraw(self, event=None):
        width = self.winfo_width()
        if width < 40:
            return
        if self._on_width and width != self._last_width:
            self._last_width = width
            self._on_width(width)
        card_height = self.inner.winfo_reqheight() + 2 * self._pad
        total = card_height + 6
        if int(float(self.cget("height"))) != total:
            self.configure(height=total)
        self.delete("shape")
        round_rect(self, 4, 5, width - 1, card_height + 4, self._radius,
                   fill=C.SHADOW, outline=C.SHADOW, tags="shape")
        round_rect(self, 2, 2, width - 3, card_height + 2, self._radius,
                   fill=self._fill, outline=C.BORDER, tags="shape")
        self.coords(self._win_id, 2 + self._pad, 2 + self._pad)
        self.itemconfigure(self._win_id, width=max(10, width - 2 * self._pad - 6))
        self.tag_lower("shape")


class GradientBar(tk.Canvas):
    def __init__(self, parent, height, title, subtitle="", title_size=22,
                 subtitle_fg="#E0E7FF", title_width=0, logo=None, title_split=0):
        super().__init__(parent, height=height, highlightthickness=0, bg=C.GRADIENT[0])
        root = parent.winfo_toplevel()
        self._title = title
        self._subtitle = subtitle
        self._subtitle_fg = subtitle_fg
        self._title_width = title_width
        self._logo = logo
        self._title_split = title_split
        self._buttons = []
        self._title_font = tkfont.Font(root=root, family=C.FONT, size=title_size, weight="bold")
        self._light_font = tkfont.Font(root=root, family=C.FONT, size=title_size, weight="normal")
        self._sub_font = tkfont.Font(root=root, family=C.FONT,
                                     size=11 if title_size > 16 else 12,
                                     weight="normal" if title_size > 16 else "bold")
        self._btn_font = tkfont.Font(root=root, family=C.FONT, size=11, weight="bold")
        self.bind("<Configure>", lambda e: self._draw())

    def add_button(self, text, command, style="white"):
        self._buttons.append((text, command, style))
        self._draw()

    def set_subtitle(self, text):
        self._subtitle = text
        self._draw()

    def _draw(self):
        width = self.winfo_width()
        height = self.winfo_height()
        if width < 10 or height < 10:
            return
        self.delete("all")
        step = 4
        for x in range(0, width, step):
            self.create_rectangle(x, 0, x + step, height, outline="",
                                  fill=gradient_color(C.GRADIENT, x / width))

        left = 26
        if self._logo is not None:
            self.create_image(left, height / 2, image=self._logo, anchor="w")
            left += self._logo.width() + 16

        has_subtitle = bool(self._subtitle)
        title_y = height * 0.38 if has_subtitle else height / 2
        if self._title_split:
            first, second = self._title[:self._title_split], self._title[self._title_split:]
            self.create_text(left, title_y, text=first, anchor="w", fill="white",
                             font=self._light_font)
            self.create_text(left + self._light_font.measure(first), title_y, text=second,
                             anchor="w", fill="white", font=self._title_font)
        else:
            options = {"width": self._title_width} if self._title_width else {}
            self.create_text(left, title_y, text=self._title, anchor="w", fill="white",
                             font=self._title_font, **options)
        if has_subtitle:
            self.create_text(left, height * 0.76, text=self._subtitle, anchor="w",
                             fill=self._subtitle_fg, font=self._sub_font)

        right = width - 26
        for index, (text, command, style) in enumerate(reversed(self._buttons)):
            fill, fg, hover, outline = BUTTON_STYLES[style]
            button_width = self._btn_font.measure(text) + 44
            button_height = self._btn_font.metrics("linespace") + 20
            x1 = right - button_width
            y1 = (height - button_height) / 2
            tag = f"button{index}"
            shape = round_rect(self, x1, y1, right, y1 + button_height, button_height / 2,
                               fill=fill, outline=fill, tags=(tag,))
            self.create_text(x1 + button_width / 2, y1 + button_height / 2, text=text,
                             fill=fg, font=self._btn_font, tags=(tag,))
            self.tag_bind(tag, "<Enter>", lambda e, s=shape, h=hover: (
                self.itemconfigure(s, fill=h, outline=h), self.configure(cursor="hand2")))
            self.tag_bind(tag, "<Leave>", lambda e, s=shape, f=fill: (
                self.itemconfigure(s, fill=f, outline=f), self.configure(cursor="")))
            self.tag_bind(tag, "<Button-1>", lambda e, c=command: c())
            right = x1 - 12
