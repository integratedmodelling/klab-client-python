from enum import Enum
from .exceptions import *


class TicketType(Enum):
    ResourceSubmission = "ResourceSubmission"
    ResourcePublication = "ResourcePublication"
    ComponentSetup = "ComponentSetup"
    ContextObservation = "ContextObservation"
    ObservationInContext = "ObservationInContext"
    ContextEstimate = "ContextEstimate"
    ObservationEstimate = "ObservationEstimate"

    @staticmethod
    def fromValue(value: str):
        for ts in TicketType:
            if ts.value.lower() == value.lower():
                return ts
        raise KlabIllegalArgumentException(
            f"no TicketType available with the value {value}")


class TicketStatus(Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    ERROR = "ERROR"

    @staticmethod
    def fromValue(value: str):
        for ts in TicketStatus:
            if ts.value.lower() == value.lower():
                return ts
        raise KlabIllegalArgumentException(
            f"no TicketStatus available with the value {value}")


class Ticket():

    def __init__(self) -> None:
        self._id = None
        self._postDate = None
        self._resolutionDate = None
        self._status = TicketStatus.OPEN
        self._type = None
        self._data = {}
        self._statusMessage = None
        self._seen = False

    @staticmethod
    def fromDict(dataMap: dict):
        ticket = Ticket()
        ticket.id = dataMap['id']
        ticket.postDate = dataMap['postDate']
        ticket.resolutionDate = dataMap['resolutionDate']
        ticket.status = TicketStatus.fromValue(dataMap['status'])
        ticket.type = TicketType.fromValue(dataMap['type'])
        ticket.data = dataMap['data']
        ticket.statusMessage = dataMap['statusMessage']
        ticket.seen = dataMap['seen']
        return ticket

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, newId):
        self._id = newId

    @property
    def postDate(self):
        return self._postDate

    @postDate.setter
    def postDate(self, postDate):
        self._postDate = postDate

    @property
    def resolutionDate(self):
        return self._resolutionDate

    @resolutionDate.setter
    def resolutionDate(self, resolutionDate):
        self._resolutionDate = resolutionDate

    @property
    def status(self) -> TicketStatus:
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def type(self) -> TicketType:
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def statusMessage(self):
        return self._statusMessage

    @statusMessage.setter
    def statusMessage(self, statusMessage):
        self._statusMessage = statusMessage

    @property
    def seen(self):
        return self._seen

    @seen.setter
    def seen(self, seen):
        self._seen = seen

    def __str__(self) -> str:
        return f"Ticket [id={self.id}, status={self.status}, type={self.type}, data={self.data}]"


class Estimate():
    def __init__(self, id: str, cost: float, currency: str, type: TicketType, feasible: str):
        self._estimateId = id
        self._cost = cost
        self._currency = currency
        self._ticketType = type
        self._feasible = "true" == feasible

    @property
    def cost(self) -> float:
        """The cost of the estimate, converted to the user currency returned by `getCurrency()`"""
        return self._cost

    @property
    def currency(self) -> str:
        """The currency of the estimate (ISO code). If the estimate is in raw k.LAB credits, this will return "KLB"."""
        return self._currency

    @property
    def estimateId(self) -> str:
        return self._estimateId

    @property
    def ticketType(self) -> TicketType:
        return self._ticketType

    # @property
    # def getDataflow(self, format:ExportFormat) -> str:
    #     return self._estimateId

    @property
    def isFeasible(self) -> bool:
        return self._feasible


class TicketResponse():
    def __init__(self) -> None:
        self._tickets = []

    @property
    def tickets(self) -> list:
        return self._tickets

    @tickets.setter
    def tickets(self, tickets):
        self._tickets = tickets
