import datetime
import requests

class GymLogController():

    base_url = r'http://localhost:5000/api/'

    def __init__(self, logger):
        self.logger = logger
        self.token = None
        self.exercises = None
        self._observers = []

    def subscribe(self, func):
        self._observers.append(func)

    def _update_observers(self):
        for func in self._observers:
            func()

    def check_token(self, username, password):
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

    def add_exercise(self, exercise):
        if self.token:
            try:
                url = GymLogController.base_url + 'exercises'
                headers = {'Authorization': f'Bearer {self.token}'}
                response = requests.post(url=url, headers=headers, json={'exercises': [exercise]})
                if response.status_code == 201:
                    self.exercises += response.json()
                    self.exercises.sort()
                    self._update_observers()
                    return True
                elif response.status_code == 401:
                    raise PermissionError("invalid token")
                elif response.status_code == 409:
                    return False
                else:
                    raise ValueError("unexpected status code received")
            except requests.exceptions.RequestException:
                self.logger.exception("An unhandled exception has been caught attempting to create exercise")
        else:
            raise PermissionError("invalid token")

    def add_logs(self, exercises):
        date = datetime.date.today().strftime("%Y-%m-%d")
        json = {'date': date, 'exercises': exercises}
        if self.token:
            try:
                url = GymLogController.base_url + 'sessions'
                headers = {'Authorization': f'Bearer {self.token}'}
                response = requests.post(url=url, headers=headers, json=json)
                if response.status_code == 201:
                    return True
                elif response.status_code == 400:
                    raise ValueError("invalid json in request body")
                elif response.status_code == 401:
                    raise PermissionError("invalid token")
                elif response.status_code == 409:
                    return False
                else:
                    raise ValueError("unexpected status code received")
            except requests.exceptions.RequestException:
                self.logger.exception("An unhandled exception has been caught attempting to create record")
        else:
            raise PermissionError("invalid token")

    def get_logs(self, date):
        """
        Example URL:
            https://gym-log-staging.herokuapp.com/api/sessions/2019-07-17

        Example response:
            [{
                "session": {
                    "date": "Wed, 17 Jul 2019 00:00:00 -0000",
                    "username": "Hadlee Poure",
                    "exercises": ["dumbbell bench press", "tricep pushdown"],
                    "reps": [
                        [9, 13],
                        [10]
                    ],
                    "weights": [
                        [19, 36],
                        [108]
                    ]
                }
            }]
        """
        print(date)
        return """
            [{
                "session": {
                    "date": "Wed, 17 Jul 2019 00:00:00 -0000",
                    "username": "Hadlee Poure",
                    "exercises": ["dumbbell bench press", "tricep pushdown"],
                    "reps": [
                        [9, 13],
                        [10]
                    ],
                    "weights": [
                        [19, 36],
                        [108]
                    ]
                }
            }]
            """
