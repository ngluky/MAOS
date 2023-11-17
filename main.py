import asyncio

import ctypes
import json
import pickle
import tkinter.font

from ctypes import windll
from CTkMessagebox import CTkMessagebox

import _tkinter

from ValLib import async_login_cookie
from Constant import Constant
from widgets.Home import *
from widgets.Loading import *
from widgets.Login import *
from widgets.Variable import ListVariable, CustomVariable


CORNER_RADIUS = 20

FR_PRIVATE = 0x10
FR_NOT_ENUM = 0x20


def add_font_file(file):
    fr_private = 0x10

    file = ctypes.byref(ctypes.create_unicode_buffer(file))
    font_count = windll.gdi32.AddFontResourceExW(file, fr_private, 0)

    if font_count == 0:
        raise RuntimeError("Error durante la carga de la fuente.")


class MainApp:
    def __init__(self):
        self.window = None

    async def exec(self, loop):
        self.window = App((810, 450), "MAOS", r".\icons\icon.ico", loop)
        await self.window.show()


class App(CTk):
    def __init__(self, start_size, title, icon, loop: AbstractEventLoop) -> None:
        super().__init__()
        # init window
        self.title(title)
        self.geometry(f"{start_size[0]}x{start_size[1]}")
        self.iconbitmap(icon)
        set_appearance_mode("Dark")
        set_default_color_theme("blue")

        # tkinter.Variable
        self.index_user_curr = tkinter.IntVar(self, -1)
        # self.index_user_curr.trace("w", self.account_change)

        self.event_value_account_change = tkinter.BooleanVar(self, False)
        self.event_value_account_change.trace('w', self.widget_update)

        # init value
        self.loading_startup: Loaing = None
        self.login_frame_: Login = None
        self.main_home_frame: Home = None
        self.exitFlag = False
        self.loop = loop

        # loading cookie
        self.render_loading_startup()
        try:
            with open("data.d", "rb") as file:
                self.loading_startup.set_text("loading cookie file")
                data = pickle.load(file)
                for i in data:
                    print(i.expire)
                self.loop.create_task(self.load_cookie(data))

        except FileNotFoundError:
            self.widget_update()


        # loading global setting
        try:
            with open('setting_global.json', 'r+', encoding='UTF-8') as file:
                Constant.Setting_Valorant = json.loads(file.read())

        except (FileNotFoundError, json.JSONDecodeError):
            Constant.Setting_Valorant = {}

        # add event
        self.protocol("WM_DELETE_WINDOW", self.on_quit)

    async def load_cookie(self, auths: Auth):
        len_ = len(auths)
        if len_ == 0:
            self.widget_update()
            return

        class HandelCookie:
            def __init__(self, progress):
                self.count = 0
                self.loading_startup = progress

            async def login_cookie(self, auth: ExtraAuth):
                auth = await async_login_cookie(auth)
                print(auth)
                self.count += 1
                self.loading_startup.setprogress(self.count / len_)
                return auth

        loading = HandelCookie(self.loading_startup)

        tasks = [self.loop.create_task(loading.login_cookie(i)) for i in auths]
        Constant.Accounts = await asyncio.gather(*tasks)
        for i in Constant.Accounts:
            Constant.EndPoints.append(EndPoints(i))
        self.widget_update()

    async def handel_add_cookie(self, user: User):
        try:
            auth = await authenticate(user)
            Constant.Accounts.append(auth)
            Constant.EndPoints.append(EndPoints(auth))
            print(auth)
            self.render_("home")
            return True

        except exceptions.AuthException as err:
            CTkMessagebox(type="Error", message=err)
            return False

    def widget_update(self, *args):
        self.clear_()
        if len(Constant.Accounts) == 0:
            self.render_("login")
        else:
            self.render_("home")
        # print(tk.font.families())

    def clear_(self):
        for widgets in self.winfo_children():
            widgets.place_forget()
            widgets.pack_forget()

    def render_(self, win=None):
        self.clear_()
        if win is None:
            return

        if win == "login":
            self.render_login()

        elif win == "home":
            self.render_home()

        elif win == "loading":
            self.render_loading_startup()

    def render_home(self):
        if self.main_home_frame is None:
            self.main_home_frame = Home(self)
        self.main_home_frame.show()

    def render_login(self):
        self.login_frame_ = Login(self, fg_color="transparent", corner_radius=CORNER_RADIUS)
        self.login_frame_.place(x=0, y=0, relwidth=1, relheight=1)

    def render_loading_startup(self):
        self.loading_startup = Loaing(self, type_=PROGRESS, text="loading cookie")

        self.loading_startup.place(x=0, y=0, relwidth=1, relheight=1)

    def on_quit(self):
        print("quit")
        self.exitFlag = True
        accounts = []
        for i in Constant.Accounts:
            if i.remember:
                accounts.append(i)
        with open("data.d", "wb+") as file:
            pickle.dump(accounts, file)
        with open('setting_global.json', 'w+', encoding='UTF-8') as file:
            setting = json.dumps(Constant.Setting_Valorant)
            file.write(setting)
        self.update()
        # self.withdraw()


    async def show(self):
        while not self.exitFlag:
            self.update()
            await asyncio.sleep(.01)

        self.quit()



if __name__ == "__main__":
    add_font_file(".\\fonts\\Valorant Font.ttf")
    add_font_file("./fonts/FontFont_FF.Mark.Pro.Medium.otf")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MainApp().exec(loop))
