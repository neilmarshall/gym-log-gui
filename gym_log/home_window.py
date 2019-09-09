import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

class HomeWindow(ttk.Frame):
    """Subclass of tkinter.Frame  - controls post-login behaviour"""

    def __init__(self, parent, thread_pool, gym_log_controller):
        """Constructor method"""

        super().__init__(parent)

        self._thread_pool = thread_pool
        self._gym_log_controller = gym_log_controller

        self._exercise_name = tk.StringVar()
        self._exercise_weight = tk.IntVar()
        self._exercise_reps = tk.IntVar()
        self._exercise_sets = tk.IntVar()

        self._update_exercise_name_options = None

    def launch(self):
        """Build and launch home window"""
        self.pack()
        notebook = ttk.Notebook(self)
        notebook.pack()

        add_log_frame = self._build_add_log_frame(notebook)
        notebook.add(add_log_frame, text="Add Logs")

        add_exercise_frame = self._build_add_exercise_frame(notebook)
        notebook.add(add_exercise_frame, text="Add Exercises")

        search_log_frame = ttk.Frame(notebook)
        notebook.add(search_log_frame, text="Search Logs")

    def _build_add_log_frame(self, parent):
        """Home window frame responsible for adding new logs"""

        def add_log():
            print(self._exercise_name.get(), self._exercise_weight.get(),
                  self._exercise_reps.get(), self._exercise_sets.get())

        def set_button_state(e):
            if self._exercise_name.get() and self._exercise_reps.get() and self._exercise_sets.get():
                submit_button.state(['!disabled'])
            else:
                submit_button.state(['disabled'])

        add_log_frame = ttk.Frame(parent)

        ttk.Label(add_log_frame, text="Exercise:").grid(row=0, column=0, sticky=tk.W)
        exercise_name = ttk.Combobox(add_log_frame,
                                     textvariable=self._exercise_name,
                                     state='readonly',
                                     values=self._gym_log_controller.exercises)
        exercise_name.grid(row=0, column=1, sticky=tk.E)
        exercise_name.bind('<<ComboboxSelected>>', set_button_state)

        def update_exercise_name_options():
            exercise_name['values'] = self._gym_log_controller.exercises
        self._update_exercise_name_options = update_exercise_name_options

        ttk.Label(add_log_frame, text="Weight:").grid(row=1, column=0, sticky=tk.W)
        ttk.Spinbox(add_log_frame, from_=0, to=10, textvariable=self._exercise_weight) \
           .grid(row=1, column=1, sticky=tk.E)

        ttk.Label(add_log_frame, text="Reps:").grid(row=2, column=0, sticky=tk.W)
        exercise_reps = ttk.Spinbox(add_log_frame, from_=0, to=10,
                                    textvariable=self._exercise_reps)
        exercise_reps.grid(row=2, column=1, sticky=tk.E)
        exercise_reps.bind('<ButtonRelease-1>', set_button_state)

        ttk.Label(add_log_frame, text="Sets:").grid(row=3, column=0, sticky=tk.W)
        exercise_sets = ttk.Spinbox(add_log_frame, from_=0, to=10,
                                    textvariable=self._exercise_sets)
        exercise_sets.grid(row=3, column=1, sticky=tk.E)
        exercise_sets.bind('<ButtonRelease-1>', set_button_state)

        submit_button = ttk.Button(add_log_frame, text="Submit", command=add_log)
        submit_button.grid(row=4, columnspan=2)
        submit_button.state(['disabled'])

        return add_log_frame

    def _build_add_exercise_frame(self, parent):
        """Home window frame responsible for adding new exercises"""

        def set_button_state(*args):
            state = "!disabled" if exercise_name.get() != "" else "disabled"
            add_exercise_button.state([state])

        def add_exercise(*args):
            def update_exercise_list(future):
                if future.result():
                    self._update_exercise_name_options()
                else:
                    messagebox.showwarning("409 - Duplicate Content",
                    "That exercise already exists - please try again")
            exercise = exercise_name.get()
            exercise_name.set("")  # clear entry widget once exercise parsed
            self._thread_pool \
                .submit(self._gym_log_controller.add_exercise, exercise) \
                .add_done_callback(update_exercise_list)

        add_exercise_frame = ttk.Frame(parent)

        ttk.Label(add_exercise_frame, text="Exercise:") \
           .grid(row=0, column=0, sticky=tk.W)
        exercise_name = tk.StringVar()
        exercise_name.trace_add('write', set_button_state)
        ttk.Entry(add_exercise_frame, textvariable=exercise_name) \
           .grid(row=0, column=1, sticky=tk.E)

        add_exercise_button = ttk.Button(add_exercise_frame,
                                         text="Add Exercise",
                                         command=add_exercise)
        add_exercise_button.grid(row=1, columnspan=2)
        add_exercise_button.state(['disabled'])

        return add_exercise_frame

