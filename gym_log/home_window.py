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

        self._logs = []

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
        def clear_inputs():
            self._exercise_name.set('')
            self._exercise_weight.set(0)
            self._exercise_reps.set(0)
            self._exercise_sets.set(0)

        def set_add_log_button_state(e=None):
            if self._exercise_name.get() and self._exercise_reps.get() and self._exercise_sets.get():
                add_log_button.state(['!disabled'])
            else:
                add_log_button.state(['disabled'])

        def set_submit_logs_button_state():
            if self._logs:
                submit_logs_button.state(['!disabled'])
            else:
                submit_logs_button.state(['disabled'])

        def add_log():
            name = self._exercise_name.get().lower()
            weight = self._exercise_weight.get()
            reps = self._exercise_reps.get()
            sets = self._exercise_sets.get()
            log = [{'exercise name': name, 'weights': [weight] * sets, 'reps': [reps] * sets}]
            self._logs += log
            clear_inputs()
            set_add_log_button_state()
            set_submit_logs_button_state()
            update_current_log_display()

        def update_current_log_display():
            current_log_display.delete('1.0', tk.END)
            current_log_display.insert('1.0', self._logs)

        def submit_logs():
            def check_for_409_response(future):
                if not future.result():
                    messagebox.showwarning("409 - Duplicate Content",
                    "A session for that date already exists")
            self._thread_pool \
                .submit(self._gym_log_controller.add_logs, self._logs) \
                .add_done_callback(check_for_409_response)
            self._logs = []
            set_submit_logs_button_state()

        add_log_frame = ttk.Frame(parent)

        ttk.Label(add_log_frame, text="Exercise:").grid(row=0, column=0, sticky=tk.W)
        exercise_name = ttk.Combobox(add_log_frame,
                                     textvariable=self._exercise_name,
                                     state='readonly',
                                     values=self._gym_log_controller.exercises)
        exercise_name.grid(row=0, column=1, sticky=tk.E)
        exercise_name.bind('<<ComboboxSelected>>', set_add_log_button_state)

        def update_exercise_name_options():
            exercise_name['values'] = self._gym_log_controller.exercises
        self._gym_log_controller.subscribe(update_exercise_name_options)

        ttk.Label(add_log_frame, text="Weight:").grid(row=1, column=0, sticky=tk.W)
        ttk.Spinbox(add_log_frame, from_=0, to=10, textvariable=self._exercise_weight) \
           .grid(row=1, column=1, sticky=tk.E)

        ttk.Label(add_log_frame, text="Reps:").grid(row=2, column=0, sticky=tk.W)
        exercise_reps = ttk.Spinbox(add_log_frame, from_=0, to=10,
                                    textvariable=self._exercise_reps)
        exercise_reps.grid(row=2, column=1, sticky=tk.E)
        exercise_reps.bind('<ButtonRelease-1>', set_add_log_button_state)

        ttk.Label(add_log_frame, text="Sets:").grid(row=3, column=0, sticky=tk.W)
        exercise_sets = ttk.Spinbox(add_log_frame, from_=0, to=10,
                                    textvariable=self._exercise_sets)
        exercise_sets.grid(row=3, column=1, sticky=tk.E)
        exercise_sets.bind('<ButtonRelease-1>', set_add_log_button_state)

        button_frame = ttk.Frame(add_log_frame)
        button_frame.grid(row=4, columnspan=2)

        add_log_button = ttk.Button(button_frame,
                text="Add log to session", command=add_log)
        add_log_button.pack(side=tk.LEFT)
        add_log_button.state(['disabled'])

        submit_logs_button = ttk.Button(button_frame,
                text="Submit session", command=submit_logs)
        submit_logs_button.pack(side=tk.LEFT)
        submit_logs_button.state(['disabled'])

        reset_session_button = ttk.Button(button_frame,
                text="Reset Session", command=lambda: print('resetting session...'))
        reset_session_button.pack(side=tk.LEFT)

        session_frame = ttk.LabelFrame(add_log_frame, text="Session")
        session_frame.grid(row=5, columnspan=2)
        current_log_display = tk.Text(session_frame)
        current_log_display.pack()

        return add_log_frame

    def _build_add_exercise_frame(self, parent):
        """Home window frame responsible for adding new exercises"""

        def set_button_state(*args):
            state = "!disabled" if exercise_name.get() != "" else "disabled"
            add_exercise_button.state([state])

        def add_exercise(*args):
            def check_for_409_response(future):
                if not future.result():
                    messagebox.showwarning("409 - Duplicate Content",
                    "That exercise already exists - please try again")
            exercise = exercise_name.get()
            exercise_name.set("")  # clear entry widget once exercise parsed
            self._thread_pool \
                .submit(self._gym_log_controller.add_exercise, exercise) \
                .add_done_callback(check_for_409_response)

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

