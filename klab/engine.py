import requests
from enum import Enum

P_EXPORT = "{export}";
P_CONTEXT = "{context}";
P_OBSERVATION = "{observation}";
P_TICKET = "{ticket}";
P_ESTIMATE = "{estimate}";


class Endpoints(Enum):
    AUTHENTICATE_USER = API_BASE + "/users/log-in",
    DEAUTHENTICATE_USER = API_BASE + "/users/log-out",
    CREATE_CONTEXT = PUBLIC_BASE + "/submit/context",
    OBSERVE_IN_CONTEXT = PUBLIC_BASE + "/submit/observation/" + P_CONTEXT,
    SUBMIT_ESTIMATE = PUBLIC_BASE + "/submit/estimate/" + P_ESTIMATE,
    EXPORT_DATA = PUBLIC_BASE + "/export/" + P_EXPORT + "/" + P_OBSERVATION,
    TICKET_INFO = PUBLIC_BASE + "/ticket/info/" + P_TICKET


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
