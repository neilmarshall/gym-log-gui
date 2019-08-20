import tkinter as tk
from tkinter import ttk

class LoginWindow(tk.Tk):

    def __init__(self):

        super().__init__()

        input_frame = ttk.Frame(self)
        input_frame.pack()

        ttk.Label(input_frame, text="Username").grid(row=0, column=0)
        ttk.Label(input_frame, text="Password").grid(row=1, column=0)

        ttk.Entry(input_frame).grid(row=0, column=1)
        ttk.Entry(input_frame).grid(row=1, column=1)

        ttk.Button(input_frame, text="Login", command=self.login).grid(row=2, columnspan=2)

    def login(self):
        print('logging in...')


if __name__ == '__main__':
    LoginWindow().mainloop()
