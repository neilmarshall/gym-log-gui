import requests

class GymLogController():

    base_url = r'http://localhost:5000/api/'

    def __init__(self, logger):
        self.logger = logger
        self.token = None
        self.exercises = None

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
