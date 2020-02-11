import logging
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from ttkthemes.themed_tk import ThemedTk

from gym_log.gym_log_controller import  GymLogController
from gym_log.home_window import HomeWindow
from gym_log.login_window import LoginWindow

class MainWindow(ThemedTk):
    """Subclass of tkinter.Tk  - controls GUI application"""

    def __init__(self, ulr, logger):
        """Constructor method"""

        super().__init__(theme='arc')

        self.thread_pool = ThreadPoolExecutor()

        self.logger = logger
        self.gym_log_controller = GymLogController(url, self.logger)

        self.login_window = None
        self.home_window = None

        # create menu bar
        self.create_menu_bar()

        # create and launch windows
        self.launch_login_window()

    def launch_login_window(self):
        """Instantiate and launch login window"""
        def login_callback():
            self.title('Gym Log - Home')
            self.launch_home_window()
        self.title('Gym Log - Login')
        self.login_window = LoginWindow(self,
                self.thread_pool, self.gym_log_controller)
        self.login_window.launch(login_callback)

    def launch_home_window(self):
        """Instantiate and launch home window"""
        self.home_window = HomeWindow(self,
                self.thread_pool, self.gym_log_controller)
        self.home_window.launch()

    def create_menu_bar(self):
        """Create menu bar for GUI application"""
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label='File', menu=file_menu)
        self.config(menu=menu_bar)

    def logout(self):
        """Log out current user from the home window"""
        if self.home_window is not None:
            self.home_window.destroy()
            self.home_window = None
            self.launch_login_window()

    def quit(self):
        """Exit the application"""
        self.thread_pool.shutdown(False)
        super().quit()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    MainWindow(url, logging.getLogger()).mainloop()
