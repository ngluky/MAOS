import asyncio
import json
import time
import tkinter as tk

import httpx
from customtkinter import *
from typing import Union, Tuple
from PIL import Image
import numpy as np
from widgets.ImageHandel import *
from ValLib import EndPoints
from widgets.Variable import CustomVariable

TEST_URL = "https://media.valorant-api.com/bundles/d958b181-4e7b-dc60-7c3c-e3a3a376a8d2/displayicon.png"
TEST_SKIN = "https://media.valorant-api.com/weaponskinlevels/578e9077-4f88-260c-e54c-b988425c60e4/displayicon.png"

FILL_X = "fillX"
FILL_Y = "fillY"
FILL_AUTO = "fillAuto"


class TabView(CTkFrame):
    def __init__(self, master, current_acc: CustomVariable = None, *args, **kw) -> None:
        super().__init__(master, *args, **kw)

        self.current_acc: CustomVariable = current_acc
        self.button_icon = {
            "shop": CTkImage(Image.open("./img/shop-d.png"), Image.open("./img/shop-l.png")),
            "account": CTkImage(Image.open("./img/account-d.png"), Image.open("./img/account-l.png")),
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

        self.frame_ = {
            "shop": Shop(self.main_view, current_acc=self.current_acc),
            "account": TabViewFrame(self.main_view),
            "match": TabViewFrame(self.main_view),
            "setting": TabViewFrame(self.main_view)
        }

        var = self.frame_["shop"]
        var.show()

    def tab_handel(self, tab):
        for key in self.button_icon.keys():
            if self.button_icon[key] is tab:
                print(key)
                self.hidden_all_frame_()
                frame = self.frame_.get(key, None)
                frame.show()
    def hidden_all_frame_(self):
        for i in self.frame_.values():
            i.hidden()



async def get_weapon_skin_level_by_uuid(uuid):
    #  return url image skin
    url = f'https://valorant-api.com/v1/weapons/skinlevels/{uuid}'
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)

        data = resp.json()

        return data['data']['displayIcon']


async def get_bundle_by_uuid(uuid):
    url = f"https://valorant-api.com/v1/bundles/{uuid}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()
        return data["data"]["displayIcon"]


class TabViewFrame(CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.is_show = False

    def show(self):
        self.pack(fill=BOTH, expand=True)
        self.is_show = True

    def hidden(self):
        self.pack_forget()
        self.is_show = False

class Shop(TabViewFrame):
    def __init__(self, master, current_acc: CustomVariable = None, *args, **kw) -> None:
        super().__init__(master, *args, **kw)

        # init value
        self.current_acc = current_acc
        self.loop = asyncio.get_event_loop()

        # setup layout
        self.grid_rowconfigure((0, 1, 2, 3), weight=1, uniform='a')
        self.grid_columnconfigure(0, weight=3, uniform='a')
        self.grid_columnconfigure(1, weight=1, uniform='a')

        self.bundle_label = ImageLabel(self, text='')
        self.bundle_label.grid(row=0, column=0, rowspan=4, sticky=NSEW, padx=5, pady=5)

        self.skins = [
            ImageLabel(self, text='', width=50, fill_type=FILL_AUTO, corner_radius=0),
            ImageLabel(self, text='', width=50, fill_type=FILL_AUTO, corner_radius=0),
            ImageLabel(self, text='', width=50, fill_type=FILL_AUTO, corner_radius=0),
            ImageLabel(self, text='', width=50, fill_type=FILL_AUTO, corner_radius=0)
        ]
        for index, ele in enumerate(self.skins):
            ele.grid(row=index, column=1, sticky=NSEW, padx=5, pady=5)

        self.current_acc.add_callback(self.handel_event)

    async def get_shop(self, endpoint: EndPoints):
        data = await endpoint.Store.Storefront()
        bundle = data["FeaturedBundle"]["Bundle"]["DataAssetID"]
        skins = data["SkinsPanelLayout"]["SingleItemOffers"]

        bundle_url = await get_bundle_by_uuid(bundle)
        if self.is_show:
            self.bundle_label.set_img(url=bundle_url)

        async def get_skin(uuid, index):
            ele = self.skins[index]
            skin_url = await get_weapon_skin_level_by_uuid(uuid)
            if self.is_show:
                ele.set_img(url=skin_url)

        tasks = [self.loop.create_task(get_skin(id, index)) for index, id in enumerate(skins)]

    def set_(self, data):
        pass

    def show(self):
        super().show()
        endpont = self.current_acc.get()
        print(endpont)
        if isinstance(endpont, EndPoints):
            self.loop.create_task(self.get_shop(self.current_acc.get()))

    async def handel_event(self, mode, value):
        await self.get_shop(value)


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


class ImageLabel(CTkLabel):
    def __init__(self, master, path=None, url=None, size=None, corner_radius=20, fill_type=FILL_Y,
                 *args, **kw) -> None:
        super().__init__(master, *args, **kw)

        self.img_size = None
        self.img = None

        self._fill_type = fill_type
        self._corner_radius = corner_radius
        self.set_img(path, url)

        if fill_type is not None:
            self.bind('<Configure>', self.update_size_img)

    def update_size_img(self, event=None):
        if self.img is None:
            return

        if event is not None:
            self.configure(image=self.crop(event.height, event.width))
        else:
            self.configure(image=self.crop(self.winfo_height(), self.winfo_width()))

    def _crop_fill_y(self, height, width):
        new_height = height
        new_width = int(height / self.img_size[1] * self.img_size[0])
        img = self.img.resize((new_width, new_height))

        if width < new_width:
            denta_width = new_width - width
            img = img.crop((denta_width // 2, 0, denta_width // 2 + width, height))

        return CTkImage(cropping_image_in_a_rounded_rectangle(img, self._corner_radius), size=(width, height))

    def _crop_fill_x(self, height, width):
        new_width = width
        new_height = int(width / self.img_size[0] * self.img_size[1])
        img = self.img.resize((new_width, new_height))

        if width < new_width:
            denta_width = new_width - width
            img = img.crop((denta_width // 2, 0, denta_width // 2 + width, height))

        return CTkImage(cropping_image_in_a_rounded_rectangle(img, self._corner_radius),
                        size=(new_width, new_height))

    def crop(self, height, width):
        if self._fill_type == FILL_Y:
            return self._crop_fill_y(height, width)

        elif self._fill_type == FILL_X:
            return self._crop_fill_x(height, width)

        elif self._fill_type == FILL_AUTO:
            new_width = width
            new_height = int(width / self.img_size[0] * self.img_size[1])

            if new_height > height:
                new_height = height - 1
                new_width = int(height / self.img_size[1] * self.img_size[0])

            img = self.img.resize((new_width, new_height))

            return CTkImage(cropping_image_in_a_rounded_rectangle(img, self._corner_radius), size=(new_width, new_height))

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
