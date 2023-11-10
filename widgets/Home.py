import asyncio
import tkinter as tk
from customtkinter import *
from PIL import Image
from asyncio.events import AbstractEventLoop

from widgets.AccInfor import *
from widgets.TabView import *

from ValLib import Auth, EndPoints, get_region, get_shard, async_get_region

CORNER_RADIUS = 20


class Home(CTkFrame):
    def __init__(self, master, end_points: EndPoints = None, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)

        self.EndPoints: EndPoints = end_points
        self.loop: AbstractEventLoop = self.winfo_toplevel().loop

        self.main_home_frame = CTkFrame(self, fg_color="transparent")

        home_frame_top = CTkFrame(self.main_home_frame, height=80, fg_color="transparent")
        home_frame_top.pack(side=TOP, fill=X)

        home_frame_top.grid_columnconfigure(0, weight=7)
        home_frame_top.grid_columnconfigure(1, weight=1)

        # AccInfor
        self.acc_infor = AccInfor(home_frame_top, corner_radius=CORNER_RADIUS)
        self.acc_infor.grid(row=0, column=0, sticky=NSEW, padx=(10, 0), pady=10)

        button_play_font = CTkFont("Consolas", 20, "bold")
        button_play = CTkButton(home_frame_top, text="PLAY", width=50, font=button_play_font)
        button_play.grid(row=0, column=1, sticky=NSEW, padx=(20, 10), pady=30)

        home_frame_button = TabView(self.main_home_frame, corner_radius=CORNER_RADIUS)
        home_frame_button.pack(side=TOP, fill=BOTH, expand=True, padx=10, pady=(0, 10))
        self.main_home_frame.pack(fill=BOTH, expand=True)

        self.after(10, lambda: self.loop.create_task(self.api_star()))

    async def api_star(self):
        task = [
            self.loop.create_task(self.get_player_card()),
            self.loop.create_task(self.get_player_name())
        ]

        await asyncio.gather(*task)

    async def get_player_card(self):
        async with httpx.AsyncClient() as client:
            data = await self.EndPoints.Pvp.async_Player_Loadout()
            resp = await client.get(f"https://valorant-api.com/v1/playercards/{data.identity.player_card_id}")
            data = resp.json()
            self.acc_infor.set_avt(data["data"]["smallArt"])

    async def get_player_name(self):
        name_data = await self.EndPoints.Pvp.async_Name_Service()
        name_data = dict(name_data[0])
        GameName = name_data.get('GameName', '')
        TagLine = name_data.get('TagLine', '')
        print(GameName, TagLine)
        if GameName != '' and TagLine != '':
            self.acc_infor.set_name(f"{GameName}#{TagLine}")

    async def get_player_titles(self):
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://valorant-api.com/v1/playertitles/{self.EndPoints.auth.user_id}")

            data = resp.json()

            titles = data["data"]["displayName"]

            self.acc_infor.set_title(titles)

    def set_end_points(self, end_point: EndPoints):
        self.EndPoints = end_point
