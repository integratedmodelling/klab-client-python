import requests
from .exceptions import *
from .utils import EndPoint, KLAB_VERSION, USER_AGENT_PLATFORM, POLLING_INTERVAL_SEC,P_EXPORT,P_OBSERVATION
from .observation import ObservationReference, Export, ExportFormat, ObservationRequest, ContextImpl, ObservationImpl, ContextRequest
from .ticket import Ticket, TicketResponse, TicketStatus, TicketType, Estimate
import asyncio

class Engine:
    """

    """

    def __init__(self, url):
        self.token = None
        self.url = url
        self.acceptHeader = None

        while self.url.endswith("/"):
            self.url = self.url[0:-1]

    # def authenticate(self, username = None, password = None):
    #     if username and password:
    #         pass
    #     else:
    #         response = requests.get(api_url)

    def authenticate(self):
        """Local engine login, no auth necessary."""

        requestUrl = self.makeUrl(EndPoint.PING.value)
        userAgent = self.getUserAgent()
        headers = {
            "User-Agent": userAgent,
            "Accept": "application/json"
        }
        try:
            response = requests.get(requestUrl, headers=headers)
            response.raise_for_status()
        except Exception as err:
            raise err
        else:
            jsonResponse = response.json()
            self.token = jsonResponse.get("localSessionId")

        return self.token

    def deauthenticate(self):
        # TODO this doesn't have a backend implementation yet, for now return true
        # headers = {
        #     "Authorization":self.token
        # }
        # requestUrl = self.makeUrl(EndPoint.DEAUTHENTICATE_USER.value)
        # try:
        #     response = requests.post(requestUrl, headers=headers)
        #     response.raise_for_status()
        # except Exception:
        #     return False
        # else:
        return True

    def isOnline(self):
        return self.token != None
    
    def accept(self, mediaType:str):
        self.acceptHeader = mediaType
        return self
	

    def get(self, endpoint:str, responseType:any, parameters:list=None):
        mediaType = "application/json"
        if self.acceptHeader:
            mediaType = self.acceptHeader
            self.acceptHeader = None
        
        requestUrl = self.makeUrl(endpoint, parameters)
        userAgent = self.getUserAgent()
        headers = {
            "User-Agent": userAgent,
            "Accept": mediaType,
            "Authorization": self.token
        }
        try:
            response = requests.get(requestUrl, headers=headers)
            response.raise_for_status()
        except Exception as err:
            raise err
        else:
            jsonResponse = response.json()
            return jsonResponse


    def post(self, endpoint:str, request:any, responseType, pathVariables:list = None):
        mediaType = "application/json"
        if self.acceptHeader:
            mediaType = self.acceptHeader
            self.acceptHeader = None
        
        # TODO
        # if (pathVariables != null) {
        # 	for (int i = 0; i < pathVariables.length; i++) {
        # 		endpoint = endpoint.replace(pathVariables[i].toString(), pathVariables[++i].toString());
        # 	}
        # }

        requestUrl = self.makeUrl(endpoint)
        userAgent = self.getUserAgent()
        headers = {
            "User-Agent": userAgent,
            "Content-Type": "application/json",
            "Accept": mediaType,
            "Authorization": self.token
        }

        try:
            response = requests.post(requestUrl, headers=headers, data=request.toJson() )
            response.raise_for_status()
        except Exception as err:
            raise err
        else:
            jsonResponse = response.json()
            return jsonResponse
    


    def makeUrl(self, endpoint, parameters=[]):
        parms = ""
        if parameters:
            for i in range(0, len(parameters)):
                if parms == "":
                    parms += "?"
                else:
                    parms += "&"
                parms += str(parameters[i])
                i += 1
                parms += "=" + str(parameters[i])

        return f"{self.url}{endpoint}{parms}"

    def getUserAgent(self):
        return "k.LAB/" + KLAB_VERSION + " (" + USER_AGENT_PLATFORM + ")"

    def getObservation(self, artifactId: str) -> ObservationReference:
        endpoint = EndPoint.EXPORT_DATA.value.replace(P_EXPORT, Export.STRUCTURE.name.lower()).replace(P_OBSERVATION, artifactId)
        ret = self.get(endpoint, ObservationReference)
        if not ret or not ret.id:
            return None
        return ret

    def streamExport(self, observationId: str, target: Export,  format: ExportFormat, output, parameters: list) -> bool:
        pass
        # String url = makeUrl(
        #         EXPORT_DATA.replace(P_EXPORT, target.name().toLowerCase()).replace(P_OBSERVATION, observationId),
        #         parameters);
        # try {

        #     Unirest.get(url).accept(format.getMediaType()).header("Authorization", token)
        #             .header("User-Agent", getUserAgent()).thenConsume(response -> {
        #                 try {
        #                     response.getContent().transferTo(output);
        #                 } catch (IOException e) {
        #                     // uncheck
        #                     throw new KlabIOException(e);
        #                 }
        #             });

        #     return true;

        # } catch (Throwable t) {
        #     // just return false
        # }

        # return false;

    def submitObservation(self, request: ObservationRequest) -> str:
        """Submit context request, return ticket number or null in case of error"""
        pass
        # 	TicketResponse.Ticket response = post(OBSERVE_IN_CONTEXT.replace(P_CONTEXT, request.getContextId()), request,
        # 			TicketResponse.Ticket.class);
        # 	if (response != null && response.getId() != null) {
        # 		return response.getId();
        # 	}
        # 	return null;
        # }


    def submitContext(self, request:ContextRequest):
        """Submit context request, return ticket number or null in case of error"""
        response = self.post(EndPoint.CREATE_CONTEXT.value, request, Ticket)
        if response:
            return response.id
        
        return None
	

    def getTicket(self, ticketId: str) -> Ticket:
        pass
        # ret = self.get(TICKET_INFO.replace(P_TICKET, ticketId), TicketResponse.Ticket.class);
        # return (ret == null || ret.getId() == null) ? null : ret;


class TicketHandler():
    def __init__(self,  engine: Engine, ticketId: str, context: ContextImpl) -> None:
        self.engine = engine
        self.ticketId = ticketId
        self.context = context
        self.cancelled = False
        self.result = None

    def cancel(self):
        self.cancelled = True
        # return False ???

    def isCancelled(self) -> bool:
        return self.cancelled

    def isDone(self) -> bool:
        return self.result != None

    async def get(self, timeoutSeconds:int = 900):
        if self.isCancelled():
            return None
        time = 0
        while not self.result:
            if time > timeoutSeconds:
                break
            bean = self.poll(self.engine)
            if bean:
                self.result = bean
                break
            elif self.isCancelled():
                break
            await asyncio.sleep(POLLING_INTERVAL_SEC)
            time += POLLING_INTERVAL_SEC

        return self.result

    def poll(self, engine: Engine) -> any:
        ticket = engine.getTicket(self.ticketId)
        if ticket == None or ticket.status == TicketStatus.ERROR or ticket.id == None:
            self.cancel()
            return None

        if ticket.status == TicketStatus.RESOLVED:
            return self.processTicket(ticket)
        return None

    def processTicket(self, ticket: Ticket):
        match ticket.type:
            case TicketType.ContextEstimate:
                return self.makeEstimate(ticket)
            case TicketType.ObservationEstimate:
                return self.makeEstimate(ticket)
            case TicketType.ContextObservation:
                return self.makeContext(ticket)
            case TicketType.ObservationInContext:
                return self.makeObservation(ticket)

        raise KlabInternalErrorException(
            f"unexpected ticket type: {ticket.type}")

    def makeObservation(self,  ticket: Ticket) -> any:
        if "artifacts" in ticket.data:
            artSplit = ticket.data["artifacts"].split(",")
            for oid in artSplit:
                bean = self.engine.getObservation(oid)
                ret = ObservationImpl(bean, self.engine)
                if self.context and ret and ret.reference:
                    self.context.updateWith(ret)
                return ret
        return None

    def makeContext(self, ticket: Ticket):
        bean = self.engine.getObservation(ticket.data.get("context"))
        context = ContextImpl(bean, self.engine)
        if "artifacts" in ticket.data:
            artSplit = ticket.data["artifacts"].split(",")
            for oid in artSplit:
                context.notifyObservation(oid)
        return context

    def makeEstimate(self,  ticket:Ticket):
        return Estimate(ticket.data.get("estimate"), float(ticket.data.get("cost")),
                ticket.data.get("currency"), ticket.type, ticket.data.get("feasible"))
