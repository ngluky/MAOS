import asyncio
from asyncio.events import AbstractEventLoop
import tkinter as tk
from customtkinter import *
from PIL import Image

from widgets.AccStatus import *
from widgets.ImageHandel import *

URL_PLYER_CARD_DEF = "https://media.valorant-api.com/playercards/c89194bd-4710-b54e-8d6c-60be6274fbb2/displayicon.png"


class Acc(CTkFrame):
    def __init__(self, master, corner_radius, *arg, **kw) -> None:
        super().__init__(master, corner_radius=corner_radius, *arg, **kw)

        # init frame
        self.configure(fg_color=self._detect_color_of_master())
        self.configure(bg_color=self.winfo_toplevel()["background"])

        # setup value
        self.name = tk.StringVar(self, '')
        self.title = tk.StringVar(self, '')

        # avt img
        self.avt_img: CTkImage = None
        self.label_avt: CTkLabel = CTkLabel(self, text="")
        self.label_avt.pack(side=LEFT, padx=int(self['height'] * 0.3 / 2), pady=int(self['height'] * 0.3 / 2))
        self.set_avt()

        # player name and title widget
        frame_name = CTkFrame(self, fg_color="transparent")
        frame_name.pack(side=LEFT)

        font_name = CTkFont('Consolas', 20, "bold")
        font_title = CTkFont('Consolas', 14, "normal")

        name_text = CTkLabel(frame_name, textvariable=self.name, anchor="sw", font=font_name)
        name_text.pack(expand=True, fill='both')

        title_text = CTkLabel(frame_name, textvariable=self.title, anchor="nw", font=font_title)
        title_text.pack(fill='both', expand=True)

        # acc status widget
        acc_status = AccStatus(self, OFFLINE)
        acc_status.pack(side=LEFT, expand=True, fill='both', padx=(0, 20))
        acc_status.set_status((10, 0))

    def _size_update(self, height):
        if self.avt_img is not None:
            self.avt_img.configure(size=(int(height * 0.7), int(height * 0.7)))

    async def _set_avt(self, url=URL_PLYER_CARD_DEF, path=None):
        print("set avt: ", url)
        if url is not None:
            img = await async_load_img_from_url(url)
            img_pil = cropping_image_in_a_circular(img)
        elif path is not None:
            img_pil = Image.open(path)
        else:
            raise KeyError("undefined url or path")
        size = (30, 30)
        self.avt_img = CTkImage(img_pil, size=size if (size[0] != 0 or size[1] != 0) else img_pil.size)
        self._size_update(self['height'])
        self.label_avt.configure(image=self.avt_img)

    def set_avt(self, url=URL_PLYER_CARD_DEF, path=None):
        self.winfo_toplevel().loop.create_task(self._set_avt(url, path))

    def set_name(self, name: str):
        print("set name: ", name)
        self.name.set(name)

    def set_title(self, text: str):
        self.title.set(text)


class AddAcc(CTkFrame):
    def __init__(self, master, corner_radius, command=None, *arg, **kw) -> None:
        super().__init__(master, corner_radius=corner_radius, *arg, **kw)
        # init frame
        self.configure(fg_color=self._detect_color_of_master())
        self.configure(bg_color=self.winfo_toplevel()["background"])

        img = CTkImage(Image.open("img/add-d.png"), Image.open("img/add-l.png"))
        button = CTkButton(self, text='', image=img, fg_color="transparent")
        button.place(relx=.5, rely=.5, anchor=CENTER)


class AccInfor(CTkFrame):
    def __init__(self, master, corner_radius, *arg, **kw) -> None:
        super().__init__(master, corner_radius=corner_radius, *arg, **kw)

        # init frame
        self.height = self.master["height"]
        self.corner_radius = corner_radius
        self.loop: AbstractEventLoops = self.winfo_toplevel().loop
        self.configure(height=self.height)

        # setup value
        self.values = []
        self.frames = []
        self.shift_index = 0
        self.target_index = 0

        # init image
        img_up = CTkImage(Image.open("img/arrow-up-d.png"), Image.open("img/arrow-up-l.png"))
        img_down = CTkImage(Image.open("img/arrow-down-d.png"), Image.open("img/arrow-down-l.png"))

        # button change Acc
        self.button_frame = CTkFrame(self, fg_color="transparent", height=self.height, width=40)

        buttons_up = CTkButton(self.button_frame, text='', width=40, command=self.up,
                               fg_color="transparent", hover=False, image=img_up)

        buttons_down = CTkButton(self.button_frame, text='', width=40, command=self.down,
                                 fg_color="transparent", hover=False, image=img_down)

        buttons_up.pack(side=TOP, fill=BOTH, expand=True)
        buttons_down.pack(side=TOP, fill=BOTH, expand=True)
        self.button_frame.pack(side=RIGHT, fill=Y, padx=10, pady=10)

        # button add Acc
        self.button_Acc = AddAcc(self, command=lambda: print('click'), corner_radius=20)

    async def update_pos_widget(self):

        if self.target_index > self.shift_index:
            for i in range(self.shift_index, self.target_index, 1):
                self.shift_index = i
                self.render_acc()
                await asyncio.sleep(0.01)

        else:
            for i in range(self.shift_index, self.target_index, -1):
                self.shift_index = i
                self.render_acc()
                await asyncio.sleep(0.01)




    def render_acc(self):
        for index, ele in enumerate(self.frames):
            ele.place(x=0, y=index * self.height - self.shift_index, relheight=1, relwidth=1)

        self.button_Acc.place(x=0, y=len(self.frames) * self.height - self.shift_index, relwidth=1, relheight=1)

        self.button_frame.lift()

    def _render_frame(self, data: dict):
        frame = Acc(self, 20, height=self.height)
        frame.set_avt(data.get('avt', ''))
        frame.set_name(data.get('name', ''))
        frame.set_title(data.get('title', ''))
        self.frames.append(frame)

    def add(self, name: str, title: str, avt: str):
        data = {
            "name": name,
            "avt": avt,
            "title": title
        }
        self.values.append(data)
        self._render_frame(data)

        self.render_acc()

    def get(self, index):
        pass

    def remove(self, index):
        pass

    def up(self):
        if self.target_index - self.height < 0:
            return

        self.target_index -= self.height

        self.loop.create_task(self.update_pos_widget())

    def down(self):
        if self.target_index + self.height > len(self.frames) * self.height:
            return

        self.target_index += self.height

        self.loop.create_task(self.update_pos_widget())