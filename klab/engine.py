import requests
from klab.klab import Endpoints


class Engine:
    """

    """
    token: str
    url: str

    DEFAULT_LOCAL_ENGINE_URL = "http://127.0.0.1:8283/modeler"

    def __init__(self):
        self.url = self.DEFAULT_LOCAL_ENGINE_URL
        self.authenticate_local()

    def __init__(self, url):
        self.url = url
        self.authenticate_local()

    def __init__(self, url, username, password):
        self.url = url
        self.authenticate_remote(username, password)

    def authenticate_local(self):
        pass

    def authenticate_remote(self, username, password):
        pass

    def get(self, endpoint, parameters=None):
        pass
