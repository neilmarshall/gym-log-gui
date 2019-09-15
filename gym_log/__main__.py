import logging
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import ttk
from ttkthemes.themed_tk import ThemedTk

from gym_log.gym_log_controller import  GymLogController
from gym_log.home_window import HomeWindow
from gym_log.login_window import LoginWindow

class MainWindow(ThemedTk):
    """Subclass of tkinter.Tk  - controls GUI application"""

    def __init__(self, logger):
        """Constructor method"""

        super().__init__(theme='arc')
        self.title('Gym Log - Login')

        self.logger = logger
        self.thread_pool = ThreadPoolExecutor()
        self.gym_log_controller = GymLogController(self.logger)

        # create menu bar
        self.create_menu_bar()

        # create login window
        login_window = LoginWindow(self,
                self.thread_pool, self.gym_log_controller)

        # create home window
        self.home_window = HomeWindow(self,
                self.thread_pool, self.gym_log_controller)

        # launch login window
        login_window.launch(self.login_callback)

    def create_menu_bar(self):
        """Create menu bar for GUI application"""
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label='File', menu=file_menu)
        self.config(menu=menu_bar)

    def quit(self):
        """Exit the application"""
        self.thread_pool.shutdown(False)
        super().quit()

    def login_callback(self):
        self.title('Gym Log - Home')
        self.home_window.launch()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    MainWindow(logging.getLogger()).mainloop()
