import tkinter as tk
from customtkinter import *
from PIL import Image

from widgets.AccStatus import *
from widgets.ImageHandel import *

URL_PLYER_CARD_DEF = "https://media.valorant-api.com/playercards/c89194bd-4710-b54e-8d6c-60be6274fbb2/displayicon.png"


class Acc(CTkFrame):
    def __init__(self, master, corner_radius, *arg, **kw) -> None:
        super().__init__(master, fg_color="transparent", *arg, **kw)

        self.name = tk.StringVar(self, '')
        self.title = tk.StringVar(self, '')

        # avt
        self.avt_img: CTkImage = None
        self.label_avt: CTkLabel = CTkLabel(self, text="")
        self.label_avt.pack(side=LEFT, padx=int(self['height'] * 0.3 / 2), pady=int(self['height'] * 0.3 / 2))
        self.set_avt()

        # name player
        frame_name = CTkFrame(self, fg_color="transparent")
        frame_name.pack(side=LEFT)

        font_name = CTkFont('Consolas', 20, "bold")
        name_text = CTkLabel(frame_name, textvariable=self.name, anchor="sw", font=font_name)
        name_text.pack(expand=True, fill='both')

        font_title = CTkFont('Consolas', 14, "normal")
        title_text = CTkLabel(frame_name, textvariable=self.title, anchor="nw", font=font_title)
        title_text.pack(fill='both', expand=True)

        # acc status
        acc_status = AccStatus(self, OFFLINE)
        acc_status.pack(side=LEFT, expand=True, fill='both', )
        acc_status.set_status((10, 0))

        # change acc button
        buttons_frame = CTkFrame(self, fg_color="transparent", height=self['height'], width=40,
                                 corner_radius=20)
        buttons_frame.pack(side=RIGHT, padx=(0, 14))

        img_up = CTkImage(Image.open("img/arrow-up-d.png"), Image.open("img/arrow-up-l.png"))
        img_down = CTkImage(Image.open("img/arrow-down-d.png"), Image.open("img/arrow-down-l.png"))

        buttons_up = CTkButton(buttons_frame, text='', height=40, width=40, fg_color="transparent", corner_radius=10,
                               hover=False, image=img_up, command=self.up)
        buttons_up.place(x=0, y=0, anchor=NW)

        buttons_down = CTkButton(buttons_frame, text='', height=40, width=40, fg_color="transparent", corner_radius=10,
                                 hover=False, image=img_down, command=self.down)
        buttons_down.place(x=0, rely=1, anchor=SW)

    def _size_update(self, height):
        if self.avt_img:
            self.avt_img.configure(size=(int(height * 0.7), int(height * 0.7)))

    async def _set_avt(self, url=URL_PLYER_CARD_DEF, path=None):
        print("start")
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
        self.name.set(name)

    def set_title(self, text: str):
        self.title.set(text)

class AccInfor(CTkFrame):
    def __init__(self, master, corner_radius,*arg, **kw) -> None:
        super().__init__(master, fg_color="transparent", *arg, **kw)
        self.configure(height=self.master["height"])
        self.corner_radius = corner_radius
        self.values = []
        self.frames = []
        # self.bind("<Configure>", self.size_update)

    def render_acc(self):
        pass

    def add(self, data):
        # data = {
        #     "name": str,
        #     "avt": str url,
        #     "title"
        # }
        pass

    def get(self, index):
        pass

    def remove(self, index):
        pass

