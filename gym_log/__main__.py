import requests
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import ttk

class LoginWindow(tk.Tk):

    def __init__(self):

        super().__init__()

        input_frame = ttk.Frame(self)
        input_frame.pack()

        ttk.Label(input_frame, text="Username").grid(row=0, column=0)
        ttk.Label(input_frame, text="Password").grid(row=1, column=0)

        self.username_entry = ttk.Entry(input_frame)
        self.username_entry.grid(row=0, column=1)
        self.password_entry = ttk.Entry(input_frame, show='*')
        self.password_entry.grid(row=1, column=1)

        ttk.Button(input_frame, text="Login",
                command=self.login).grid(row=2, columnspan=2)

        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label='File', menu=file_menu)
        self.config(menu=menu_bar)

        self.gym_log_controller = GymLogController()

    def login(self):
        def begin_login():
            self.gym_log_controller.set_token(self.username_entry.get(), self.password_entry.get())
        def end_login(future):
            progress_bar.stop()
            progress_window.destroy()
        progress_window = tk.Toplevel(self)
        progress_frame = ttk.Frame(progress_window)
        progress_frame.pack()
        ttk.Label(progress_frame, text="Logging in...").pack()
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        progress_bar.pack()
        progress_bar.start()
        pool = ThreadPoolExecutor()
        pool.submit(begin_login).add_done_callback(end_login)
        pool.shutdown(False)


class GymLogController():

    base_url = r'http://localhost:5000/api/'

    def __init__(self):
        self.token = None

    def set_token(self, username, password):
        url = GymLogController.base_url + 'token'
        response = requests.get(url, auth=(username, password))
        try:
            if response.status_code == 200:
                try:
                    self.token = response.json()['token']
                    print(self.token)  # TODO : Delete this
                except KeyError as e:
                    pass  # TODO : Send error message to logging output
            elif response.status_code == 401:
                pass  # TODO : Deal with unauthorised access (show an error message?)
            else:
                pass  # TODO : Send error message to logging output
        except Exception as e:
            print('error caught', e)  # TODO : Send error message to logging output


if __name__ == '__main__':
    LoginWindow().mainloop()  # TODO : Inject a logger here
