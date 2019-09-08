import os
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

        self.thread_pool = thread_pool
        self.gym_log_controller = gym_log_controller

        self.username_entry = tk.StringVar()
        self.password_entry = tk.StringVar()

    def launch(self, successful_login_callback):
        """Build and launch login window"""
        self.pack()

        ttk.Label(self, text="Username").grid(row=0, column=0)
        ttk.Entry(self, textvariable=self.username_entry).grid(row=0, column=1)
        self.password_entry.set(os.environ.get('DEFAULT_PASSWORD') or '')

        ttk.Label(self, text="Password").grid(row=1, column=0)
        ttk.Entry(self, textvariable=self.password_entry, show='*').grid(row=1, column=1)
        self.username_entry.set(os.environ.get('DEFAULT_USERNAME') or '')

        ttk.Button(self, text="Login",
                command=lambda: self._login(successful_login_callback)) \
           .grid(row=2, columnspan=2)

    def _login(self, successful_login_callback):
        """Set a user token on the gym log controller"""
        def begin_login():
            username, password = self.username_entry.get(), self.password_entry.get()
            is_login_successful = self.gym_log_controller.check_token(username, password)
            if is_login_successful:
                self.gym_log_controller.set_exercises()
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
        self.thread_pool.submit(begin_login).add_done_callback(end_login)
