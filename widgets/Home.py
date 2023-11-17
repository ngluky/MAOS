import asyncio
import tkinter as tk
from customtkinter import *
from PIL import Image
from asyncio.events import AbstractEventLoop
from tkinter import messagebox

from widgets.AccInfor import *
from widgets.TabView import *
from widgets.Variable import ListVariable, CustomVariable
from widgets.Timer_async import SetInterval, SetTimeout

from ValLib import Auth, EndPoints, get_region, get_shard, async_get_region

CORNER_RADIUS = 20


async def get_player_card(player_card_id) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://valorant-api.com/v1/playercards/{player_card_id}")
        data = resp.json()
        return data["data"]["smallArt"]


async def get_player_name(pvp: EndPoints) -> str:
    name_data = await pvp.Pvp.async_Name_Service()
    name_data = dict(name_data[0])
    GameName = name_data.get('GameName', '')
    TagLine = name_data.get('TagLine', '')
    print(GameName, TagLine)
    if GameName != '' and TagLine != '':
        return f"{GameName}#{TagLine}"
    return ''


async def get_player_titles(player_title_id):
    if player_title_id == "00000000-0000-0000-0000-000000000000":
        return ""
    async with httpx.AsyncClient() as client:
        print(player_title_id)
        resp = await client.get(f"https://valorant-api.com/v1/playertitles/{player_title_id}")
        data = resp.json()
        try:
            titles = data["data"]["titleText"]
            return titles
        except KeyError:
            return ''


class Home(CTkFrame):
    def __init__(self, master, end_points: ListVariable[EndPoints] = None, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)

        # init value
        self.EndPoints: ListVariable[EndPoints] = end_points
        self.Current_Acc: CustomVariable = CustomVariable(None)
        self.Current_Acc.set(self.EndPoints[0])
        self.loop: AbstractEventLoop = self.winfo_toplevel().loop
        self.check_account_status_timer = SetInterval(20, self.check_account_status)

        #
        self.main_home_frame = CTkFrame(self, fg_color="transparent")

        home_frame_top = CTkFrame(self.main_home_frame, height=80, fg_color="transparent")
        home_frame_top.pack(side=TOP, fill=X)

        home_frame_top.grid_columnconfigure(0, weight=7)
        home_frame_top.grid_columnconfigure(1, weight=1)

        # AccInfor
        self.acc_infor = AccInfor(home_frame_top, corner_radius=CORNER_RADIUS)
        self.acc_infor.grid(row=0, column=0, sticky=NSEW, padx=(10, 0), pady=10)
        self.acc_infor.is_account_change(self.handel_event)

        # play button
        button_play_font = CTkFont("Consolas", 20, "bold")
        button_play = CTkButton(home_frame_top, text="PLAY", width=50, font=button_play_font, command=lambda x: print("button play clicked"))
        button_play.grid(row=0, column=1, sticky=NSEW, padx=(20, 10), pady=30)

        # tabView - shop -
        home_frame_button = TabView(self.main_home_frame, corner_radius=CORNER_RADIUS, current_acc=self.Current_Acc)
        home_frame_button.pack(side=TOP, fill=BOTH, expand=True, padx=10, pady=(0, 10))
        self.main_home_frame.pack(fill=BOTH, expand=True)

    def handel_play_button(self):
        pass

    def handel_event(self, index):
        if index < len(self.EndPoints):
            self.Current_Acc.set(self.EndPoints[index])
            SetTimeout(1, self.check_account_status)

    async def api_star(self):
        for pvp in self.EndPoints:
            await self.render_acc_infor(pvp)

    async def render_acc_infor(self, pvp: EndPoints):
        data = await pvp.Pvp.async_Player_Loadout()
        player_card_id = data.identity.player_card_id
        player_title_id = data.identity.player_title_id
        name = await get_player_name(pvp)
        avt = await get_player_card(player_card_id)
        title = await get_player_titles(player_title_id)

        self.acc_infor.add(name, title, avt)

    def show(self):
        self.place(x=0, y=0, relwidth=1, relheight=1)
        task = self.loop.create_task(self.api_star())
        task.add_done_callback(lambda x: self.check_account_status_timer.star())

    def place_forget(self):
        super().place_forget()
        self.check_account_status_timer.cancel()

    async def check_account_status(self):

        account: EndPoints = self.Current_Acc.get()

        party_infor = await account.Party.async_Party_Player()
        if party_infor.get("httpStatus", False):
            self.acc_infor.set_status_current_account("off")
            print("offline")
        else:
            current_game = await account.CurrentGame.async_Current_Game()
            match_id = current_game.get("MatchID", False)
            if match_id:
                self.acc_infor.set_status_current_account("in")
                print("in match")
            else:
                self.acc_infor.set_status_current_account("on")
                print("online")
