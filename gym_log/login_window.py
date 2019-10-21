import os
import re
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.split(basedir)[0]
load_dotenv(os.path.join(basedir, '.env'))

class LoginWindow(ttk.Frame):
    """Subclass of tkinter.Frame  - controls application login"""

    def __init__(self, parent, thread_pool, gym_log_controller):
        """Constructor method"""

        super().__init__(parent)

        self._thread_pool = thread_pool
        self._gym_log_controller = gym_log_controller

        self._username_entry = tk.StringVar()
        self._password_entry = tk.StringVar()
        self._remember_login = tk.IntVar()

    def launch(self, successful_login_callback):
        """Build and launch login window"""
        self.pack()

        ttk.Label(self, text="Username").grid(row=0, column=0)
        ttk.Entry(self, textvariable=self._username_entry).grid(row=0, column=1, columnspan=2)
        self._password_entry.set(os.environ.get('DEFAULT_PASSWORD') or '')

        ttk.Label(self, text="Password").grid(row=1, column=0)
        ttk.Entry(self, textvariable=self._password_entry, show='*').grid(row=1, column=1, columnspan=2)
        self._username_entry.set(os.environ.get('DEFAULT_USERNAME') or '')

        ttk.Button(self, text="Login",
                command=lambda: self._login(successful_login_callback)) \
           .grid(row=2, column=1)

        ttk.Checkbutton(self, text="Remember me", variable=self._remember_login).grid(row=2, column=2)
        self._remember_login.set(True)

    def _login(self, successful_login_callback):
        """Set a user token on the gym log controller"""
        def begin_login():
            username, password = self._username_entry.get(), self._password_entry.get()
            is_login_successful = self._gym_log_controller.check_token(username, password)
            if is_login_successful:
                if self._remember_login.get():
                    self._store_login_details(username, password)
                self._gym_log_controller.set_exercises()
            return is_login_successful
        def end_login(future):
            progress_bar.stop()
            progress_window.destroy()
            if future.result():
                self.destroy()
                successful_login_callback()
            else:
                messagebox.showwarning("404 - Unauthorized Access",
                        "Login attempt failed - please try again")
        progress_window = tk.Toplevel(self)
        progress_frame = ttk.Frame(progress_window)
        progress_frame.pack()
        ttk.Label(progress_frame, text="Requesting login token...").pack()
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        progress_bar.pack()
        progress_bar.start()
        self._thread_pool.submit(begin_login).add_done_callback(end_login)

    def _store_login_details(self, username, password):
        def keep_setting(setting):
            username_match = re.match(r'^\s*DEFAULT_USERNAME=.*$', setting)
            password_match = re.match(r'\s*DEFAULT_PASSWORD=.*$', setting)
            return setting and not username_match and not password_match
        with open('.env') as f:
            current_settings = f.read().split('\n')
        with open('.env', 'w') as f:
            f.write(f'DEFAULT_USERNAME={username}\n')
            f.write(f'DEFAULT_PASSWORD={password}\n')
            f.writelines('\n'.join(filter(keep_setting, current_settings)))
