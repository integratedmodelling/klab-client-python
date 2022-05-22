from enum import Enum
from engine import Engine

API_BASE = "/api/v2",
PUBLIC_BASE = API_BASE + "/public",


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

