import logging
import os
import requests
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from tkinter import messagebox
from tkinter import ttk

basedir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.split(basedir)[0]
load_dotenv(os.path.join(basedir, '.env'))

class LoginWindow(tk.Tk):

    def __init__(self, logger):

        super().__init__()

        self.logger = logger

        self.thread_pool = ThreadPoolExecutor()

        self.gym_log_controller = GymLogController(self.logger)

        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label='File', menu=file_menu)
        self.config(menu=menu_bar)

        self.load_input_frame()

    def load_input_frame(self):
        self.input_frame = ttk.Frame(self)
        self.input_frame.pack()

        ttk.Label(self.input_frame, text="Username").grid(row=0, column=0)
        ttk.Label(self.input_frame, text="Password").grid(row=1, column=0)

        self.username_entry = ttk.Entry(self.input_frame)
        self.username_entry.grid(row=0, column=1)
        self.password_entry = ttk.Entry(self.input_frame, show='*')
        self.password_entry.grid(row=1, column=1)

        ttk.Button(self.input_frame, text="Login",
                command=self.login).grid(row=2, columnspan=2)

        self.username_entry.insert(0, os.environ.get('DEFAULT_USERNAME'))
        self.password_entry.insert(0, os.environ.get('DEFAULT_PASSWORD'))

    def quit(self):
        self.thread_pool.shutdown(False)
        super().quit()

    def login(self):
        def begin_login():
            username = self.username_entry.get()
            password = self.password_entry.get()
            return self.gym_log_controller.set_token(username, password)
        def end_login(future):
            progress_bar.stop()
            progress_window.destroy()
            if not future.result():
                messagebox.showwarning("404 - Unauthorized Access",
                        "Login attempt failed - please try again")
            else:
                self.input_frame.destroy()
        progress_window = tk.Toplevel(self.input_frame)
        progress_frame = ttk.Frame(progress_window)
        progress_frame.pack()
        ttk.Label(progress_frame, text="Requesting login token...").pack()
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        progress_bar.pack()
        progress_bar.start()
        self.thread_pool.submit(begin_login).add_done_callback(end_login)


class GymLogController():

    base_url = r'http://localhost:5000/api/'

    def __init__(self, logger):
        self.logger = logger
        self.token = None

    def set_token(self, username, password):
        try:
            url = GymLogController.base_url + 'token'
            response = requests.get(url, auth=(username, password))
            if response.status_code == 200:
                try:
                    self.token = response.json()['token']
                    print(self.token)  # TODO : Delete this
                    return True
                except KeyError:
                    self.logger.exception("Unrecognised JSON response")
            elif response.status_code == 401:
                return False
            else:
                raise ValueError("unexpected status code received")
        except Exception:
            self.logger.exception("An unhandled exception has been caught attempting to obtain an access token")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    LoginWindow(logger).mainloop()
