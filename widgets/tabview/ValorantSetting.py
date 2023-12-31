import asyncio
import json

from asyncio.events import AbstractEventLoop
from CTkToolTip import CTkToolTip
from PIL import Image
from customtkinter import *
from CTkMessagebox import CTkMessagebox

from Constant import Constant
from ValLib import EndPoints, ExtraAuth
from widgets.Structs import TabViewFrame
from widgets.ImageHandel import load_img


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

        load_img_ = CTkImage(load_img('./img/downloading-updates-d.png'),
                            load_img('./img/downloading-updates-l.png'))
        save_img = CTkImage(load_img('./img/save-d.png'),
                            load_img('./img/save-l.png'))

        self.load_button = CTkButton(self, text='', height=40, width=40, image=load_img_, fg_color="#2B2B2B",
                                     bg_color="#1D1E1E", command=self.load_button_click_handel)
        CTkToolTip(self.load_button, "load setting from account")
        self.save_button = CTkButton(self, text='', height=40, width=40, image=save_img, fg_color="#2B2B2B",
                                     bg_color="#1D1E1E", command=self.save_button_click_handel)
        CTkToolTip(self.save_button, "save setting to default")
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
        self.load_button.place(x=configure.width - 35, y=30, anchor=CENTER)
        self.save_button.place(x=configure.width - 35, y=80, anchor=CENTER)

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
