from .engine import Engine, TicketHandler
from .utils import DEFAULT_LOCAL_ENGINE_URL
from .observable import Observable
from .observation import Context, ContextRequest
from .geometry import KlabGeometry
from .exceptions import *
from .ticket import Estimate, TicketType
import asyncio

import logging

LOGGER = logging.getLogger(__name__)


class Klab:
    """
    The main k.LAB client class. A client object represents a user session in a local or remote
    engine.

    Instantiate a k.LAB client using the create* methods to connect to a local or remote engine. 
    After creation, isOnline() should always be called to ensure the connection was successful. 
    Then call `submit(Observable, Geometry, Object))` or `estimate(Observable, Geometry, Object))` 
    to create a context for further observations, which are done by invoking similar methods directly
    on the resulting context. Using estimate provides a pattern to obtain a cost estimate for each
    operation, which depends on the size of the job and the user agreement.
    """

    def __init__(self, url, username=None, password=None):
        if username and password:
            self.engine = Engine(url)
            self.session = self.engine.authenticate(username, password);
        else:
            self.engine = Engine(url)
            self.session = self.engine.authenticate();

    @staticmethod
    def create(remoteOrLocalEngineUrl = DEFAULT_LOCAL_ENGINE_URL, username=None, password=None):
        """
        Authenticate with a local or remote engine and open a new user session. Call `close()` to free
        remote resources.

        Parameters
        ----------
        remoteOrLocalEngineUrl: str
            the url to the remote or local engine, something like: http://127.0.0.1:8283/modeler.
            This defaults to DEFAULT_LOCAL_ENGINE_URL
        username:str
            necessary only for remote engines.
        password:str
            necessary only for remote engines.
            
        Returns
        -------
        Klab:
            The created remote Klab instance.
        """
        return Klab(remoteOrLocalEngineUrl, username, password)

    def isOnline(self):
        """
        Checks if the engine is online. Should always be called after creation to check on the engine status.
        
        Returns
        -------
        bool:
            true is the engine is online..
        """
        return self.engine.isOnline()
    
    def close(self):
        if self.engine.isOnline():
            return self.engine.deauthenticate()
        return True
        
    def submit(self, contextType: Observable,  geometry: KlabGeometry, *arguments: list) -> TicketHandler:
        """
        Call with a concept and geometry to create the context observation (accepting all costs) and
        optionally further observations as semantic types or options.
        
        @param contextType the type of the context. The Explorer sets that as earth:Region by
            default.
        @param geometry the geometry for the context. Use {@link GeometryBuilder} to create fluently.
        @param arguments pass semantic types for further observations to be made in the context (if
            passed, the task will finish after all have been computed). Strings will be
            interpreted as scenario URNs.
        """

        request = ContextRequest()
        request.contextType = str(contextType)
        request.geometry = geometry.encode()
        request.estimate = False

        LOGGER.debug(f"klab submit with: {request}")

        for o in arguments:
            if isinstance(o, Observable):
                request.observables.append(o)
            elif isinstance(o, str):
                request.scenarios.append(o)
            
        if request.geometry != None and request.contextType != None:
            ticket = self.engine.submitContext(request)
            if ticket:
                LOGGER.debug(f"got ticket: {ticket}")
                return TicketHandler(self.engine, ticket.id, None)

        raise KlabIllegalArgumentException(f"Cannot build observation request from arguments: {arguments}")
    
    def submitEstimate(self, estimate:Estimate) -> TicketHandler:
        if estimate.ticketType != TicketType.ContextEstimate:
            raise KlabIllegalArgumentException("the estimate passed is not a context estimate")

        LOGGER.debug(f"klab submit estimate with: {estimate}")
        ticket = self.engine.submitEstimate(estimate.estimateId)
        if ticket:
            LOGGER.debug(f"got ticket: {ticket}")
            return TicketHandler(self.engine, ticket.id, None)
        
        raise KlabIllegalStateException("estimate cannot be used")

    def estimate(self, contextType: Observable,  geometry: KlabGeometry, *arguments: list) -> TicketHandler:
        """
        Call with a concept and geometry to retrieve an estimate of the cost of making the context
        observation described. Add any observations to be made in the context as semantic types or
        options.
        
        @param contextType the type of the context. The Explorer sets that as earth:Region by
               default.
        @param geometry the geometry for the context. Use {@link GeometryBuilder} to create fluently.
        @param arguments pass observables for further observations to be made in the context (if
               passed, the task will finish after all have been computed). Strings will be
               interpreted as scenario URNs.
        
        @return a TicketHandler; call get() to wait until the estimate is ready and retrieve it.
        """
        request = ContextRequest()
        request.contextType = str(contextType)
        request.geometry = geometry.encode()
        request.estimate = True

        LOGGER.debug(f"klab submit with: {request}")

        for o in arguments:
            if isinstance(o, Observable):
                request.observables.append(o)
            elif isinstance(o, str):
                request.scenarios.append(o)

        if request.geometry != None and request.contextType != None:
            ticket = self.engine.submitContext(request)
            if ticket:
                LOGGER.debug(f"got estimate ticket: {ticket}")
                return TicketHandler(self.engine, ticket.id, None)

        raise KlabIllegalArgumentException(f"Cannot build estimate request from arguments: {arguments}")
