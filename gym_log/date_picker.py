import datetime
import tkinter as tk
from calendar import month_name, monthrange
from tkinter import ttk

class DatePicker():
    """Data picker widget that presents year, month, day selectors in a 3 x 2 grid"""

    def __init__(self, parent):

        # instantiate variables
        today = datetime.date.today()
        self.year, self.month, self.day = tk.IntVar(), tk.StringVar(), tk.IntVar()
        self.days = list(range(1, monthrange(today.year, today.month)[1] + 1))

        # set current year / month / day to current date
        self.year.set(today.year)
        self.month.set(month_name[today.month])
        self.day.set(today.day)

        # year label
        ttk.Label(parent, text="Year:").grid(row=0, column=0, sticky=tk.W)
        ttk.Spinbox(parent, textvariable=self.year,
                    values=(today.year - 1, today.year, today.year + 1)) \
           .grid(row=0, column=1)

        # month label
        ttk.Label(parent, text="Month:").grid(row=1, column=0, sticky=tk.W)
        ttk.Combobox(parent, textvariable=self.month, state='readonly',
                     values=[month_name[i] for i in range(1, 13)]) \
           .grid(row=1, column=1)

        # day label
        ttk.Label(parent, text="Day:").grid(row=2, column=0, sticky=tk.W)
        self.day_picker = ttk.Spinbox(parent, values=self.days, textvariable=self.day)
        self.day_picker.grid(row=2, column=1)

        # add function bindings to year / month selectors
        self.year.trace('w', self._update_days)
        self.month.trace('w', self._update_days)

    def _update_days(self, *args):
        index = list(month_name).index(self.month.get())
        self.days = list(range(1, monthrange(self.year.get(), index)[1] + 1))
        self.day_picker.config(values=self.days)
        if self.day.get() > self.days[-1]:
            self.day.set(self.days[-1])

    def get_date(self):
        return self.year.get(), self.month.get(), self.day.get()

