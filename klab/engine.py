import requests
from .exceptions import *
from .utils import Export, ExportFormat, EndPoint, KLAB_VERSION, USER_AGENT_PLATFORM, POLLING_INTERVAL_SEC,P_EXPORT,P_OBSERVATION,P_TICKET, P_CONTEXT,P_ESTIMATE
from .observation import ObservationReference,  ObservationRequest, Context, Observation, ContextRequest
from .ticket import Ticket, TicketResponse, TicketStatus, TicketType, Estimate
import asyncio
import io
import json
import logging

LOGGER = logging.getLogger(__name__)


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
	

    def get(self, endpoint:str, parameters:list=None):
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
            if mediaType == 'application/json':
                jsonResponse = response.json()
                return jsonResponse
            elif mediaType == 'text/plain':
                return response.text
            else:
                return response.content


    def post(self, endpoint:str, request:any, pathVariables:list = None):
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

    def addParams(self, endpoint, parameters=[]):
        parms = ""
        if parameters:
            i = 0
            while i < len(parameters):
                if parms == "":
                    parms += "?"
                else:
                    parms += "&"
                parms += str(parameters[i])
                i += 1
                parms += "=" + str(parameters[i])
                i += 1

        return f"{endpoint}{parms}"

    def getUserAgent(self):
        return "k.LAB/" + KLAB_VERSION + " (" + USER_AGENT_PLATFORM + ")"

    def getObservation(self, artifactId: str) -> ObservationReference:
        endpoint = EndPoint.EXPORT_DATA.value.replace(P_EXPORT, Export.STRUCTURE.name.lower()).replace(P_OBSERVATION, artifactId)
        ret = self.get(endpoint)
        if not ret or 'id' not in ret:
            return None
        return ObservationReference.fromDict(ret)

    def streamExport(self, observationId: str, target: Export,  format: ExportFormat, output: io.BytesIO, parameters: list = []) -> bool:
        endpoint = EndPoint.EXPORT_DATA.value.replace(P_EXPORT, target.name.lower()).replace(P_OBSERVATION, observationId)
        endpoint = self.addParams(endpoint, parameters)

        self.accept(format.getMediaType())

        ret = self.get(endpoint)
        if ret:
            if format == ExportFormat.GEOJSON_FEATURES or format == ExportFormat.JSON_CODE or format == ExportFormat.ELK_GRAPH_JSON:
                retType = ret.get('type')
                if retType == "FeatureCollection":
                    features = ret.get('features')
                    featuresJson = json.dumps(features)
                    res = bytes(featuresJson, 'utf-8')
                    output.write(res)
                else:
                    js = json.dumps(ret)
                    res = bytes(js, 'utf-8')
                    output.write(res)
            elif format == ExportFormat.GEOTIFF_RASTER:
                output.write(ret) # TODO check this
            elif format == ExportFormat.KDL_CODE:
                res = bytes(ret, 'utf-8')
                output.write(res) # TODO check this
            elif format == ExportFormat.PNG_IMAGE:
                output.write(ret)
                    
            return True
        else:
            return False


    def submitObservation(self, request: ObservationRequest) -> Ticket:
        """Submit context request, return ticket number or null in case of error"""
        endpoint = EndPoint.OBSERVE_IN_CONTEXT.value.replace(P_CONTEXT, request.contextId)

        response = self.post(endpoint, request)
        if response:
            return Ticket.fromDict(response)
        
        return None



    def submitContext(self, request:ContextRequest) -> Ticket:
        """Submit context request, return ticket number or null in case of error"""
        LOGGER.debug(f"submit context...")
        response = self.post(EndPoint.CREATE_CONTEXT.value, request)
        if response:
            return Ticket.fromDict(response)
        
        return None
	

    def submitEstimate(self, estimateId: str) -> Ticket:
        endpoint = EndPoint.SUBMIT_ESTIMATE.value.replace(P_ESTIMATE, estimateId)
        response = self.get(endpoint)
        if response:
            return Ticket.fromDict(response)
	

    def getTicket(self, ticketId: str) -> Ticket:
        LOGGER.debug(f"get ticket info...")
        ret = self.get(EndPoint.TICKET_INFO.value.replace(P_TICKET, ticketId))
        if ret and 'id' in ret:
            return Ticket.fromDict(ret)
        return None  
        


class TicketHandler():
    def __init__(self,  engine: Engine, ticketId: str, context: Context) -> None:
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
                ret = Observation(bean, self.engine)
                if self.context and ret and ret.reference:
                    self.context.updateWith(ret)
                return ret
        return None

    def makeContext(self, ticket: Ticket):
        bean = self.engine.getObservation(ticket.data.get("context"))
        context = Context(bean, self.engine)
        if "artifacts" in ticket.data:
            artSplit = ticket.data["artifacts"].split(",")
            for oid in artSplit:
                context.notifyObservation(oid)
        return context

    def makeEstimate(self,  ticket:Ticket):
        return Estimate(ticket.data.get("estimate"), float(ticket.data.get("cost")),
                ticket.data.get("currency"), ticket.type, ticket.data.get("feasible"))
