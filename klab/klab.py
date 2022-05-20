from klab.engine import Engine
from enum import Enum

API_BASE = "/api/v2",
PUBLIC_BASE = API_BASE + "/public",

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


class Export(Enum):
    STRUCTURE = "structure",
    DATA = "data",
    VIEW = "view",
    LEGEND = "legend",
    REPORT = "report",
    DATAFLOW = "dataflow",
    PROVENANCE_FULL = "provenance_full",
    PROVENANCE_SIMPLIFIED = "provenance_simplified"


class Klab:
    """
    """

    def __init__(self):
        self.engine = Engine()

    def __init__(self, url):
        self.engine = Engine(url)

    def __init__(self, url, username, password):
        self.engine = Engine(url, username, password)
