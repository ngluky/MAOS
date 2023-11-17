import asyncio
import json
import time
import tkinter as tk
import httpx

from asyncio.events import AbstractEventLoop
from typing import Union, Tuple
from customtkinter import *
from CTkMessagebox import CTkMessagebox
from PIL import Image
import numpy as np

from ValLib import EndPoints, ExtraAuth
from Constant import Constant

from widgets.ImageHandel import *
from widgets.Variable import CustomVariable

TEST_URL = "https://media.valorant-api.com/bundles/d958b181-4e7b-dc60-7c3c-e3a3a376a8d2/displayicon.png"
TEST_SKIN = "https://media.valorant-api.com/weaponskinlevels/578e9077-4f88-260c-e54c-b988425c60e4/displayicon.png"

FILL_X = "fillX"
FILL_Y = "fillY"
FILL_AUTO = "fillAuto"


class TabView(CTkFrame):
    def __init__(self, master, *args, **kw) -> None:
        super().__init__(master, *args, **kw)
        self.button_icon = {
            "shop": CTkImage(Image.open("./img/shop-d.png"), Image.open("./img/shop-l.png")),
            "account": CTkImage(Image.open("./img/curly-brackets-d.png"), Image.open("./img/curly-brackets-l.png")),
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
            "shop": Shop(self.main_view),
            "account": ValorantSetting(self.main_view),
            "match": TabViewFrame(self.main_view),
            "setting": TabViewFrame(self.main_view)
        }

        self.hidden_all_frame_()
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


class ValorantSetting(TabViewFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # init value
        self.loop: AbstractEventLoop = asyncio.get_event_loop()
        self.setting_valorant: dict = {}
        self.popup_is_show = False
        self.height = 0
        self.width = 0

        # init layout
        self.setting_view = CTkTextbox(self, corner_radius=15)
        self.setting_view.place(x=0, y=0, relwidth=1, relheight=1)
        self.setting_view.insert('0.0', json.dumps(Constant.Setting_Valorant, indent=4))

        load_img = CTkImage(Image.open('./img/downloading-updates-d.png'),
                            Image.open('./img/downloading-updates-l.png'))
        save_img = CTkImage(Image.open('./img/save-d.png'), Image.open('./img/save-l.png'))

        self.load_button = CTkButton(self, text='', height=40, width=40, image=load_img, fg_color="#2B2B2B",
                                     bg_color="#1D1E1E", command=self.load_button_click_handel)
        self.save_button = CTkButton(self, text='', height=40, width=40, image=save_img, fg_color="#2B2B2B",
                                     bg_color="#1D1E1E", command=self.save_button_click_handel)
        self.frame_acc = CTkFrame(self, bg_color="#1D1E1E")

        # init event
        self.popup_acc_render()

        self.bind('<Configure>', self.update_pos)

    def load_button_click_handel(self):
        if self.popup_is_show:
            self.hidden_popup()
            return

        self.show_popup()

    def update_pos(self, configure):
        self.height = configure.height
        self.width = configure.width
        self.load_button.place(x=configure.width - 30, y=30, anchor=CENTER)
        self.save_button.place(x=configure.width - 30, y=80, anchor=CENTER)

    def show_popup(self):
        self.frame_acc.place(x=self.width - 55, y=10, anchor=NE)
        self.popup_is_show = True

    def hidden_popup(self):
        self.frame_acc.place_forget()
        self.popup_is_show = False

    async def click_handel(self, acc):
        for endpoint in Constant.EndPoints:
            endpoint: EndPoints
            if acc == endpoint.auth:
                self.setting_view.delete('0.0', 'end')
                print(endpoint)

                setting = await endpoint.Setting.async_Fetch_Preference()
                self.setting_valorant = setting
                self.setting_view.insert('0.0', json.dumps(setting, indent=4))

        self.hidden_popup()

    def popup_acc_render(self):

        for i in Constant.Accounts:
            i: ExtraAuth
            text = CTkButton(self.frame_acc, text=i.username, fg_color="transparent",
                             command=lambda: self.loop.create_task(self.click_handel(i)))
            text.pack(fill=X, padx=10, pady=5)

    def save_button_click_handel(self):
        Constant.Setting_Valorant = self.setting_valorant
        CTkMessagebox(title="Success", message="Save Complicit")

    def show(self):
        super().show()


class Shop(TabViewFrame):
    def __init__(self, master, *args, **kw) -> None:
        super().__init__(master, *args, **kw)

        # init value
        self.loop = asyncio.get_event_loop()

        # setup layout
        self.grid_rowconfigure((0, 1, 2, 3), weight=1, uniform='a')
        self.grid_columnconfigure(0, weight=3, uniform='a')
        self.grid_columnconfigure(1, weight=1, uniform='a')

        self.bundle_label = ImageLabel(self)
        self.bundle_label.grid(row=0, column=0, rowspan=4, sticky=NSEW, padx=5, pady=5)

        self.skins = [
            ImageLabel(self, fill_type=FILL_AUTO, corner_radius=0),
            ImageLabel(self, fill_type=FILL_AUTO, corner_radius=0),
            ImageLabel(self, fill_type=FILL_AUTO, corner_radius=0),
            ImageLabel(self, fill_type=FILL_AUTO, corner_radius=0)
        ]
        for index, ele in enumerate(self.skins):
            ele.grid(row=index, column=1, sticky=NSEW, padx=5, pady=5)

        Constant.Current_Acc.add_callback(self.handel_event)

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
        endpont = Constant.Current_Acc.get()
        print(endpont)
        if isinstance(endpont, EndPoints):
            self.loop.create_task(self.get_shop(Constant.Current_Acc.get()))

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


class ImageLabel(CTkFrame):
    def __init__(self, master, path=None, url=None, size=None, corner_radius=20, fill_type=FILL_Y,
                 *args, **kw) -> None:
        super().__init__(master, fg_color="transparent", *args, **kw)

        self.label = CTkLabel(self, text='')
        self.label.place(x=0, y=0, relheight=1, relwidth=1)
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
            self.label.configure(image=self.crop(event.height, event.width))
        else:
            self.label.configure(image=self.crop(self.winfo_height(), self.winfo_width()))

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
            new_height = height - 1
            new_width = int(height / self.img_size[1] * self.img_size[0])
            if new_width > width:
                new_width = width
                new_height = int(width / self.img_size[0] * self.img_size[1])

            img = self.img.resize((new_width, new_height))

            return CTkImage(cropping_image_in_a_rounded_rectangle(img, self._corner_radius),
                            size=(new_width, new_height))

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
