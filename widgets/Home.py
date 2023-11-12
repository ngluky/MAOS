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
    def __init__(self, master, end_points: list[EndPoints] = None, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)

        self.EndPoints: list[EndPoints] = end_points
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
        tasks = [self.render_acc_infor(pvp) for pvp in self.EndPoints]
        await asyncio.gather(*tasks)

    async def render_acc_infor(self, pvp: EndPoints):
        data = await pvp.Pvp.async_Player_Loadout()
        player_card_id = data.identity.player_card_id
        player_title_id = data.identity.player_title_id
        name = await self.get_player_name(pvp)
        avt = await self.get_player_card(player_card_id)
        title = await self.get_player_titles(player_title_id)
        self.acc_infor.add(name, title, avt)

    async def get_player_card(self, player_card_id) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://valorant-api.com/v1/playercards/{player_card_id}")
            data = resp.json()
            return data["data"]["smallArt"]

    async def get_player_name(self, pvp: EndPoints) -> str:
        name_data = await pvp.Pvp.async_Name_Service()
        name_data = dict(name_data[0])
        GameName = name_data.get('GameName', '')
        TagLine = name_data.get('TagLine', '')
        print(GameName, TagLine)
        if GameName != '' and TagLine != '':
            return f"{GameName}#{TagLine}"
        return ''

    async def get_player_titles(self, player_title_id):
        if player_title_id == "00000000-0000-0000-0000-000000000000": return ""
        async with httpx.AsyncClient() as client:
            print(player_title_id)
            resp = await client.get(f"https://valorant-api.com/v1/playertitles/{player_title_id}")
            data = resp.json()
            try:
                titles = data["data"]["titleText"]
                return titles
            except KeyError:
                return ''

    def add(self, endponts):
        self.EndPoints.append(endponts)