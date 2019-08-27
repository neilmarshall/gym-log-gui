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

        # create login window and variables used in that widow
        self.login_window = ttk.Frame(self)
        self.username_entry = tk.StringVar()
        self.password_entry = tk.StringVar()

        # create home window and variables used in that widow
        self.home_window = ttk.Frame(self)
        self.exercise_name = tk.StringVar()
        self.exercise_weight = tk.IntVar()
        self.exercise_reps = tk.IntVar()
        self.exercise_sets = tk.IntVar()

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
            is_login_successful = self.gym_log_controller.set_token(username, password)
            if is_login_successful:
                self.gym_log_controller.set_exercises()
            return is_login_successful
        def end_login(future):
            progress_bar.stop()
            progress_window.destroy()
            if future.result():
                self.login_window.destroy()
                self.launch_home_window()
            else:
                messagebox.showwarning("404 - Unauthorized Access",
                                       "Login attempt failed - please try again")
        progress_window = tk.Toplevel(self.login_window)
        progress_frame = ttk.Frame(progress_window)
        progress_frame.pack()
        ttk.Label(progress_frame, text="Requesting login token...").pack()
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        progress_bar.pack()
        progress_bar.start()
        self.thread_pool.submit(begin_login).add_done_callback(end_login)

    def launch_home_window(self):
        """Build and launch home window"""
        self.home_window.pack()
        notebook = ttk.Notebook(self.home_window)
        notebook.pack()
        add_log_frame = self.build_add_log_frame(notebook)
        search_log_frame = ttk.Frame(notebook)
        notebook.add(add_log_frame, text="Add Logs")
        notebook.add(search_log_frame, text="Search Logs")

    def build_add_log_frame(self, parent):
        """Home window frame responsible for adding new logs"""
        def set_button_state(e):
            if self.exercise_name.get() and self.exercise_reps.get() and self.exercise_sets.get():
                submit_button.state(['!disabled'])
            else:
                submit_button.state(['disabled'])

        add_log_frame = ttk.Frame(parent)

        ttk.Label(add_log_frame, text="Exercise:").grid(row=0, column=0, sticky=tk.W)
        exercise_name_selector = ttk.Combobox(add_log_frame,
                                              textvariable=self.exercise_name,
                                              state='readonly',
                                              values=self.gym_log_controller.exercises)
        exercise_name_selector.grid(row=0, column=1, sticky=tk.E)

        ttk.Label(add_log_frame, text="Weight:").grid(row=1, column=0, sticky=tk.W)
        ttk.Spinbox(add_log_frame, from_=0, to=10,
                    textvariable=self.exercise_weight).grid(row=1, column=1, sticky=tk.E)

        ttk.Label(add_log_frame, text="Reps:").grid(row=2, column=0, sticky=tk.W)
        exercise_reps_selector = ttk.Spinbox(add_log_frame,
                                             from_=0,
                                             to=10,
                                             textvariable=self.exercise_reps)
        exercise_reps_selector.grid(row=2, column=1, sticky=tk.E)

        ttk.Label(add_log_frame, text="Sets:").grid(row=3, column=0, sticky=tk.W)
        exercise_sets_selector = ttk.Spinbox(add_log_frame,
                                             from_=0,
                                             to=10,
                                             textvariable=self.exercise_sets)
        exercise_sets_selector.grid(row=3, column=1, sticky=tk.E)

        submit_button = ttk.Button(add_log_frame, text="Submit", command=self.add_log)
        submit_button.grid(row=4, columnspan=2)
        submit_button.state(['disabled'])

        exercise_name_selector.bind('<<ComboboxSelected>>', set_button_state)
        exercise_reps_selector.bind('<ButtonRelease-1>', set_button_state)
        exercise_sets_selector.bind('<ButtonRelease-1>', set_button_state)

        return add_log_frame

    def add_log(self):
        print(self.exercise_name.get(), self.exercise_weight.get(),
              self.exercise_reps.get(), self.exercise_sets.get())


class GymLogController():

    base_url = r'http://localhost:5000/api/'

    def __init__(self, logger):
        self.logger = logger
        self.token = None
        self.exercises = None

    def set_token(self, username, password):
        try:
            url = GymLogController.base_url + 'token'
            response = requests.get(url, auth=(username, password))
            if response.status_code == 200:
                try:
                    self.token = response.json()['token']
                    return True
                except KeyError:
                    self.logger.exception("Unrecognised JSON response")
            elif response.status_code == 401:
                return False
            else:
                raise ValueError("unexpected status code received")
        except requests.exceptions.RequestException:
            self.logger.exception("An unhandled exception has been caught attempting to obtain an access token")

    def set_exercises(self):
        if self.token:
            try:
                url = GymLogController.base_url + 'exercises'
                headers = {'Authorization': f'Bearer {self.token}'}
                response = requests.get(url=url, headers=headers)
                if response.status_code == 200:
                    self.exercises = [e.title() for e in response.json()]
                elif response.status_code == 401:
                    raise PermissionError("invalid token")
                else:
                    raise ValueError("unexpected status code received")
            except requests.exceptions.RequestException:
                self.logger.exception("An unhandled exception has been caught attempting to obtain exercise details")
        else:
            raise PermissionError("invalid token")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    LoginWindow(logging.getLogger()).mainloop()
