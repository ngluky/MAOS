import tkinter
from tkinter import messagebox

import httpx
from customtkinter import *
from typing import Union, Tuple

from widgets.Loading import *
from ValLib import authenticate, User, exceptions, HCaptchaTimeoutException


class Login(CTkFrame):
    def __init__(self, master, *arg, **kw):
        super().__init__(master, *arg, **kw)
        self.main_window = self.winfo_toplevel()
        self.logging = Loaing(self, text="Loading", height=80, width=90)

        self.frame = CTkFrame(self)
        self.frame.place(anchor="c", relx=.5, rely=.5, relwidth=0.6, relheight=0.7)

        login_text_font = CTkFont("VALORANT", 40)
        login_text = CTkLabel(self.frame, text="login", font=login_text_font)
        login_text.pack(pady=(20, 0))

        check_var = tkinter.BooleanVar(self, False)

        frame_user_name_pass_fill = CTkFrame(self.frame, fg_color="transparent")
        fill_font = CTkFont("MarkPro-Medium", 14)
        user_name_fill = CTkEntry(frame_user_name_pass_fill, placeholder_text="USERNAME", height=35, width=250,
                                  font=fill_font)
        user_name_fill.place(relx=.5, rely=.20, anchor='c')

        user_pass_fill = CTkEntry(frame_user_name_pass_fill, placeholder_text="PASSWORD", height=35, width=250,
                                  font=fill_font)
        user_pass_fill.place(relx=.5, rely=.60, anchor='c')

        checkbox = CTkCheckBox(frame_user_name_pass_fill, text="remember", variable=check_var, onvalue=True,
                               offvalue=False)
        checkbox.place(relx=.5, rely=.85, anchor='c')

        frame_user_name_pass_fill.pack(fill=X, side=TOP, expand=True)

        def button_command():
            print('clic')
            try:
                self.main_window.users.index(user_name_fill.get())
            except ValueError:
                self.frame.place_forget()
                self.logging.place(anchor="c", relx=.5, rely=.5, relwidth=0.6, relheight=0.7)
                self.login(user_name_fill.get(), user_pass_fill.get(), check_var.get())

        button = CTkButton(self.frame, text="LOGIN", height=35, command=button_command)
        button.pack(side=BOTTOM, pady=(0, 20))

    async def _login(self, user_name, passw, remember):
        print(user_name, passw, remember)
        user = User(user_name, passw, remember)
        try:
            auth = await authenticate(user)
            self.main_window.Accounts.append(auth)
            self.main_window.users.append(user_name)

            print(auth)

            self.main_window.change.set(True)
            self.main_window.users_curr.set(len(self.main_window.Accounts) - 1)


        except (exceptions.AuthException, HCaptchaTimeoutException) as er:
            messagebox.showerror('Auth Error', er)
            self.logging.place_forget()
            self.frame.place(anchor="c", relx=.5, rely=.5, relwidth=0.6, relheight=0.7)


    def login(self, user_name, passw, remember):
        self.main_window.loop.create_task(self._login(user_name, passw, remember))
