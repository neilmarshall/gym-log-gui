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
    """Subclass of tkinter.Tk  - controls GUI application"""

    def __init__(self, logger):
        """Constructor method"""

        super().__init__()

        self.logger = logger

        self.thread_pool = ThreadPoolExecutor()

        self.gym_log_controller = GymLogController(self.logger)

        # create menu bar
        self.create_menu_bar()

        # create login window
        self.login_window = ttk.Frame(self)
        self.username_entry = tk.StringVar()
        self.password_entry = tk.StringVar()

        # launch login window
        self.launch_login_window()

    def create_menu_bar(self):
        """Create menu bar for GUI application"""
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label='File', menu=file_menu)
        self.config(menu=menu_bar)

    def launch_login_window(self):
        """Build and launch login window"""
        self.login_window.pack()

        ttk.Label(self.login_window, text="Username").grid(row=0, column=0)
        ttk.Entry(self.login_window, textvariable=self.username_entry).grid(row=0, column=1)
        self.password_entry.set(os.environ.get('DEFAULT_PASSWORD') or '')

        ttk.Label(self.login_window, text="Password").grid(row=1, column=0)
        ttk.Entry(self.login_window, textvariable=self.password_entry, show='*').grid(row=1, column=1)
        self.username_entry.set(os.environ.get('DEFAULT_USERNAME') or '')

        ttk.Button(self.login_window, text="Login", command=self.login).grid(row=2, columnspan=2)

    def quit(self):
        """Exit the application"""
        self.thread_pool.shutdown(False)
        super().quit()

    def login(self):
        """Set a user token on the gym log controller"""
        def begin_login():
            username, password = self.username_entry.get(), self.password_entry.get()
            return self.gym_log_controller.set_token(username, password)
        def end_login(future):
            progress_bar.stop()
            progress_window.destroy()
            if not future.result():
                messagebox.showwarning("404 - Unauthorized Access",
                        "Login attempt failed - please try again")
            else:
                self.login_window.destroy()
        progress_window = tk.Toplevel(self.login_window)
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
        except requests.exceptions.RequestException:
            self.logger.exception("An unhandled exception has been caught attempting to obtain an access token")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    LoginWindow(logging.getLogger()).mainloop()
