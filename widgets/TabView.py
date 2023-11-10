import time
import tkinter as tk
from customtkinter import *
from typing import Union, Tuple
from PIL import Image
import numpy as np
from widgets.ImageHandel import *

TEST_URL = "https://media.valorant-api.com/bundles/d958b181-4e7b-dc60-7c3c-e3a3a376a8d2/displayicon.png"
TEST_SKIN = "https://media.valorant-api.com/weaponskins/89be9866-4807-6235-2a95-499cd23828df/displayicon.png"

FILL_X = "fillX"
FILL_Y = "fillY"


class ImageLabel(CTkLabel):
    def __init__(self, master, path=None, url=None, corner_radius=20, fill_type=FILL_Y, *args, **kw) -> None:
        super().__init__(master, *args, **kw)

        self.img_size = None
        self.img = None

        self._fill_type = fill_type
        self._corner_radius = corner_radius
        self.set_img(path, url)

        if fill_type is not None:
            self.bind('<Configure>', self.update_size_img)

    def update_size_img(self, event = None):
        if self.img is not None:
            if event is not None:
                self.configure(image=self.crop(event.height, event.width))
            else:
                self.configure(image=self.crop(self.winfo_height(), self.winfo_width()))

    def crop(self, height, width):
        if self._fill_type == FILL_Y:
            height_ = height
            width_ = int(height / self.img_size[1] * self.img_size[0])
            img = self.img.resize((width_, height_))

            if width < width_:
                denta_width = width_ - width
                img = img.crop((denta_width // 2, 0, denta_width // 2 + width, height))

            return CTkImage(cropping_image_in_a_rounded_rectangle(img, self._corner_radius), size=(width, height))

        elif self._fill_type == FILL_X:
            width_ = width
            height_ = int(width / self.img_size[0] * self.img_size[1])
            img = self.img.resize((width_, height_))

            if width < width_:
                denta_width = width_ - width
                img = img.crop((denta_width // 2, 0, denta_width // 2 + width, height))

            return CTkImage(remove_background(cropping_image_in_a_rounded_rectangle(img, self._corner_radius)), size=(width_, height_))

    def set_img(self, path=None, url=None):
        self.winfo_toplevel().loop.create_task(self.async_set_img(path, url))

    async def async_set_img(self, path=None, url=None):
        if url is not None:
            img = await async_load_img_from_url(url)
        elif path is not None:
            img = Image.open(path)
        else:
            return FileExistsError

        self.img = img
        self.img_size = self.img.size

        self.update_size_img()

class Shop(CTkFrame):
    def __init__(self, master, *args, **kw) -> None:
        super().__init__(master, *args, **kw)

        self.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.grid_columnconfigure(0, weight=3, uniform='a')
        self.grid_columnconfigure(1, weight=1, uniform='a')

        self.bundle_label = ImageLabel(self, text='', url=TEST_URL)
        self.bundle_label.grid(row=0, column=0, rowspan=4, sticky=NSEW, padx=5, pady=5)

        self.item1 = ImageLabel(self, text='', width=50, fill_type=FILL_X)
        self.item1.grid(row=0, column=1, sticky=NSEW, padx=5, pady=5)
        self.item1.set_img(url=TEST_SKIN)

        self.item2 = ImageLabel(self, text='', fill_type=FILL_X)
        self.item2.grid(row=1, column=1, sticky=NSEW, padx=5, pady=5)
        self.item2.set_img(url=TEST_SKIN)

        self.item3 = ImageLabel(self, text='', fill_type=FILL_X)
        self.item3.grid(row=2, column=1, sticky=NSEW, padx=5, pady=5)
        self.item3.set_img(url=TEST_SKIN)

        self.item4 = ImageLabel(self, text='', fill_type=FILL_X)
        self.item4.grid(row=3, column=1, sticky=NSEW, padx=5, pady=5)
        self.item4.set_img(url=TEST_SKIN)

    def show(self):
        self.pack(fill=BOTH, expand=True)

    def hidden(self):
        self.forget()


class TabView(CTkFrame):
    def __init__(self, master, *args, **kw) -> None:
        super().__init__(master, *args, **kw)

        self.button_icon = {
            "shop": CTkImage(Image.open("./img/shop-d.png"), Image.open("./img/shop-l.png")),
            "match": CTkImage(Image.open("./img/feed-d.png"), Image.open("./img/feed-l.png")),
            "setting": CTkImage(Image.open("./img/support-d.png"), Image.open("./img/support-l.png"))
        }
        # tab_title_view
        self.tab_title = TabMaster(self, fg_color="transparent", orientation=HORIZONTAL,
                                   values=tuple(self.button_icon.values()),
                                   command=self.tab_handel, corner_radius=self._corner_radius)
        self.tab_title.pack(side=LEFT, fill=BOTH, pady=7, padx=7)

        # window view
        self.main_view = CTkFrame(self, fg_color="transparent")
        self.main_view.pack(side=LEFT, fill=BOTH, expand=True, pady=7, padx=7)

        shop = Shop(self.main_view)
        shop.show()

    def _match(self):
        pass

    def _setting(self):
        pass

    def tab_handel(self, tab):
        for key in self.button_icon.keys():
            if self.button_icon[key] is tab:
                print(key)


class TabMaster(CTkFrame):
    def __init__(self, master, orientation, values: Union[Tuple[str], tuple[CTkImage]], corner_radius=10,
                 hover_color=None, command=None,
                 height=50, width=50, *args, **kw):
        super().__init__(master, *args, **kw)
        self.hover_color = hover_color if hover_color is not None else ThemeManager.theme["CTkButton"]["hover_color"]
        self.width = width
        self.height = height
        self.orientation = orientation
        self.bg_color = self._detect_color_of_master()
        self.value_selenium = values[0]
        self.values = values
        self.command = command
        self.corner_radius = corner_radius

        self.list_button = [self.craft_button(e) for e in values]

        for e in self.list_button:
            if self.orientation == HORIZONTAL:
                e.pack(side=TOP, pady=2)
            else:
                e.pack(side=LEFT, padx=2)

    def _click_handel(self, ele):

        # xóa toàn bộ bg
        for e in self.list_button:
            e.configure(fg_color=self.bg_color)

        # lấy nút bấm và thay đổi bg
        index = self.values.index(ele)
        self.list_button[index].configure(fg_color=self.hover_color)
        if self.command is not None:
            self.command(ele)

    def craft_button(self, e):
        if isinstance(e, str):
            button = CTkButton(self, text=e, fg_color=self.bg_color, corner_radius=self.corner_radius)
        elif isinstance(e, CTkImage):
            button = CTkButton(self, image=e, text='', fg_color=self.bg_color, corner_radius=self.corner_radius)
        else:
            raise ValueError()

        button.configure(command=lambda: self._click_handel(e))

        if e == self.value_selenium:
            button.configure(fg_color=self.hover_color)

        if self.orientation == HORIZONTAL:
            unit = self.width
            button.configure(height=unit, width=unit)
        elif self.orientation == VERTICAL:
            unit = self.height
            button.configure(height=unit, width=unit)

        return button
