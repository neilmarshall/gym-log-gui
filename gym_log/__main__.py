import time
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

    def login(self):
        def begin_login():
            # TODO : This function needs to extract username and password from the GUI and use these to obtain a token
            print(self.username_entry.get())  # TODO : Remove
            time.sleep(3)  # TODO : Remove
            print(self.password_entry.get())  # TODO : Remove
        def end_login(future):
            print('logged in...')  # TODO : Remove
            progress_bar.stop()
            progress_window.destroy()
        print('logging in...')  # TODO : Remove
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


if __name__ == '__main__':
    LoginWindow().mainloop()
