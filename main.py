import asyncio

import ctypes
import pickle
import tkinter.font
from ctypes import windll

import _tkinter

from ValLib import async_login_cookie
from widgets.Home import *
from widgets.Loading import *
from widgets.Login import *

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
        self.window = App((800, 450), "MAOS", r".\icons\icon.ico", loop)
        await self.window.show()


# noinspection PyGlobalUndefined
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
        self.index_user_curr.trace("w", self.account_change)

        self.event_value_account_change = tkinter.BooleanVar(self, False)
        self.event_value_account_change.trace('w', self.widget_update)

        # init value
        self.loading_startup: Loaing = None
        self.login_frame_: Login = None
        self.main_home_frame: Home = None
        self.exitFlag = False
        self.Accounts = []
        self.users = []
        self.EndPoints: list[EndPoints] = []

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

            async def login_cookie(self, auth: Auth):
                auth = await async_login_cookie(auth)
                self.count += 1
                self.loading_startup.setprogress(self.count / len_)
                return auth

        loading = HandelCookie(self.loading_startup)

        self.Accounts = []
        tasks = list([
            self.loop.create_task(loading.login_cookie(i)) for i in auths
        ])
        self.Accounts = await asyncio.gather(*tasks)

        self.widget_update()

    def account_change(self, *args):
        print(*args)
        # if self.login_frame_:
        #     self.login_frame_.set_auth(self.Accounts[self.users_curr.get()])

    async def handel_add_cookie(self, user: User):
        auth = await authenticate(user)
        self.Accounts.append(auth)
        self.users.append(user.username)
        self.EndPoints.append(EndPoints(auth))
        self.main_home_frame.add(EndPoints(auth))
        print(auth)

        self.widget_update()
        self.index_user_curr.set(len(self.Accounts) - 1)

    def widget_update(self, *args):
        if self.loading_startup:
            self.loading_startup.destroy()
        elif self.login_frame_:
            self.login_frame_.destroy()
        elif self.main_home_frame:
            self.main_home_frame.destroy()

        if len(self.Accounts) == 0:
            self.render_login()
        else:
            self.render_home()
        # print(tk.font.families())

    def render_(self, win=None):
        if self.loading_startup:
            self.loading_startup.destroy()
        elif self.login_frame_:
            self.login_frame_.destroy()
        elif self.main_home_frame:
            self.main_home_frame.destroy()

        if win is None:
            return

        if win == "login":
            self.render_login()

        elif win == "home":
            self.render_home()

        elif win == "loading":
            self.render_loading_startup()

    def render_home(self):
        if len(self.EndPoints) == 0:
            self.EndPoints = [EndPoints(i) for i in self.Accounts]

        if self.main_home_frame is None:
            self.main_home_frame = Home(self, self.EndPoints)
        self.main_home_frame.place(x=0, y=0, relwidth=1, relheight=1)

    def render_login(self):
        self.login_frame_ = Login(self, fg_color="transparent", corner_radius=CORNER_RADIUS)
        self.login_frame_.pack(fill=BOTH, expand=True)

    def render_loading_startup(self):
        self.loading_startup = Loaing(self, type_=PROGRESS, text="loading cookie")
        self.loading_startup.place(x=0, y=0, relwidth=1, relheight=1)

    def on_quit(self):
        print("quit")
        self.exitFlag = True
        with open("data.d", "wb+") as file:
            pickle.dump(self.Accounts, file)
        self.update()
        self.quit()

    async def show(self):
        while not self.exitFlag:
            try:
                self.winfo_exists()  # Will throw TclError if the main window is destroyed
            except _tkinter.TclError:
                break
            self.update()
            await asyncio.sleep(.01)


if __name__ == "__main__":
    add_font_file(".\\fonts\\Valorant Font.ttf")
    add_font_file("./fonts/FontFont_FF.Mark.Pro.Medium.otf")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MainApp().exec(loop))
