import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from gym_log.date_picker import DatePicker

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
        self._show_all_logs_value = tk.IntVar()

        self._logs = {}

    def launch(self):
        """Build and launch home window"""
        self.pack()
        notebook = ttk.Notebook(self)
        notebook.pack()

        add_log_frame = self._build_add_log_frame(notebook)
        notebook.add(add_log_frame, text="Add Logs")

        add_exercise_frame = self._build_add_exercise_frame(notebook)
        notebook.add(add_exercise_frame, text="Add Exercises")

        search_log_frame = self._build_show_logs_frame(notebook)
        notebook.add(search_log_frame, text="Search Logs")

    def _build_add_log_frame(self, parent):
        """Home window frame responsible for adding new logs"""
        def set_button_states(*args):
            if self._exercise_name.get() and self._exercise_reps.get() and self._exercise_sets.get():
                add_log_button.state(['!disabled'])
            else:
                add_log_button.state(['disabled'])

            if self._logs:
                submit_logs_button.state(['!disabled'])
                reset_session_button.state(['!disabled'])
            else:
                submit_logs_button.state(['disabled'])
                reset_session_button.state(['disabled'])

        def add_log():
            name = self._exercise_name.get().title()
            sets = self._exercise_sets.get()
            weight = [self._exercise_weight.get()] * sets
            reps = [self._exercise_reps.get()] * sets
            if name in self._logs:
                self._logs[name]['weights'] += weight
                self._logs[name]['reps'] += reps
            else:
                self._logs[name] = {'weights': weight, 'reps': reps}
            update_display(False)

        def submit_logs():
            def check_for_409_response(future):
                if not future.result():
                    messagebox.showwarning("409 - Duplicate Content",
                    "A session for that date already exists")
            date = str(date_picker.get_date())
            self._thread_pool \
                .submit(self._gym_log_controller.add_logs, date, self._logs) \
                .add_done_callback(check_for_409_response)
            update_display()

        def update_display(reset_session=True):
            def update_current_log_display():
                current_log_display.config(state='normal')
                current_log_display.delete('1.0', tk.END)
                data = ''
                for name, log in self._logs.items():
                    data += name + ':\n'
                    data += '\tweights: ' + str(log['weights']) + '\n'
                    data += '\treps: ' + str(log['reps']) + '\n'
                current_log_display.insert('1.0', data)
                current_log_display.config(state='disabled')
            def clear_inputs():
                self._exercise_name.set('')
                self._exercise_weight.set(0)
                self._exercise_reps.set(0)
                self._exercise_sets.set(0)
            if reset_session:
                self._logs = {}
            update_current_log_display()
            set_button_states()
            clear_inputs()

        # define parent frame to hold widgets
        add_log_frame = ttk.Frame(parent)

        # encapsulate widgets to specify parameters for gym logs
        ttk.Label(add_log_frame, text="Exercise:").grid(row=0, column=0, sticky=tk.W)
        exercise_name = ttk.Combobox(add_log_frame,
                                     textvariable=self._exercise_name,
                                     state='readonly',
                                     values=self._gym_log_controller.exercises)
        exercise_name.grid(row=0, column=1, sticky=tk.E)
        exercise_name.bind('<<ComboboxSelected>>', set_button_states)

        def update_exercise_name_options():
            exercise_name['values'] = self._gym_log_controller.exercises
        self._gym_log_controller.subscribe(update_exercise_name_options)

        ttk.Label(add_log_frame, text="Weight:").grid(row=1, column=0, sticky=tk.W)
        exercise_weights = ttk.Spinbox(add_log_frame, from_=0, to=100,
                                       textvariable=self._exercise_weight,
                                       justify=tk.RIGHT)
        exercise_weights.grid(row=1, column=1, sticky=tk.E)

        ttk.Label(add_log_frame, text="Reps:").grid(row=2, column=0, sticky=tk.W)
        exercise_reps = ttk.Spinbox(add_log_frame, from_=0, to=100,
                                    textvariable=self._exercise_reps,
                                    justify=tk.RIGHT)
        exercise_reps.grid(row=2, column=1, sticky=tk.E)

        ttk.Label(add_log_frame, text="Sets:").grid(row=3, column=0, sticky=tk.W)
        exercise_sets = ttk.Spinbox(add_log_frame, from_=0, to=100,
                                    textvariable=self._exercise_sets,
                                    justify=tk.RIGHT)
        exercise_sets.grid(row=3, column=1, sticky=tk.E)

        for widget in (exercise_weights, exercise_reps, exercise_sets):
            widget.bind('<ButtonRelease-1>', set_button_states)
            widget.bind('<FocusOut>', set_button_states)
            widget.bind('<Return>', set_button_states)

        # add date picker
        date_picker_frame = ttk.Frame(add_log_frame)
        date_picker = DatePicker(date_picker_frame)
        date_picker_frame.grid(row=0, rowspan=3, column=2)

        # encapsulate window control buttons in their own frame
        button_frame = ttk.Frame(add_log_frame)
        button_frame.grid(row=4, columnspan=3, pady=(10, 5))
        add_log_button = ttk.Button(button_frame, text="Add log to session", command=add_log)
        submit_logs_button = ttk.Button(button_frame, text="Submit session", command=submit_logs)
        reset_session_button = ttk.Button(button_frame, text="Reset Session", command=update_display)
        for widget in (add_log_button, submit_logs_button, reset_session_button):
            widget.pack(side=tk.LEFT)
            widget.state(['disabled'])

        # encapsulate display to show logs in current session
        session_frame = ttk.LabelFrame(add_log_frame, text="Session")
        session_frame.grid(row=5, columnspan=3, padx=10, pady=(0, 10))
        current_log_display = tk.Text(session_frame, state='disabled')
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

    def _build_show_logs_frame(self, parent):
        """Home window frame responsible for showing existing logs"""
        def get_logs():
            if self._show_all_logs_value.get():
                date = None
            else:
                date = date_picker.get_date()
            self._thread_pool.submit(self._gym_log_controller.get_logs, date) \
                .add_done_callback(update_display)

        def update_display(future):
            data = future.result()
            current_log_display.config(state='normal')
            current_log_display.delete('1.0', tk.END)
            if data:
                for row in data:
                    session = row['session']
                    date = datetime.datetime.strptime(session['date'], "%a, %d %b %Y %H:%M:%S %z").date()
                    exercises = session['exercises']
                    reps = session['reps']
                    weights = session['weights']
                    current_log_display.insert(tk.END, str(date) + '\n')
                    for e, r, w in zip(exercises, reps, weights):
                        current_log_display.insert(tk.END, '\t' + str(e) + ':\n')
                        current_log_display.insert(tk.END, '\t\tweights: ' + str(w) + '\n')
                        current_log_display.insert(tk.END, '\t\treps: ' + str(r) + '\n')
            else:
                current_log_display.insert(tk.END, "There are no logs available for this date.")
            current_log_display.config(state='disabled')

        def show_logs(*args):
            get_logs()

        # define parent frame to hold widgets
        show_logs_frame = ttk.Frame(parent)

        # add date picker
        date_picker_frame = ttk.Frame(show_logs_frame)
        date_picker = DatePicker(date_picker_frame)
        date_picker_frame.grid(row=0, rowspan=3, column=2)

        # encapsulate window control buttons in their own frame
        button_frame = ttk.Frame(show_logs_frame)
        button_frame.grid(row=4, columnspan=3, pady=(10, 5))
        show_logs_button = ttk.Button(button_frame, text="Show logs", command=show_logs)
        show_logs_button.pack(side=tk.LEFT)
        show_all_logs_checkbox = ttk.Checkbutton(button_frame,
                text="Show all logs", variable=self._show_all_logs_value)
        show_all_logs_checkbox.pack(side=tk.LEFT)

        # encapsulate display to show logs
        display_frame = ttk.LabelFrame(show_logs_frame, text="Logs")
        display_frame.grid(row=5, columnspan=3, padx=10)
        current_log_display = tk.Text(display_frame, state='disabled', height=26)
        current_log_display.pack()

        return show_logs_frame

