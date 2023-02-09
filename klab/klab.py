from .engine import Engine
from .utils import DEFAULT_LOCAL_ENGINE_URL
import asyncio

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
    def create(remoteOrLocalEngineUrl = DEFAULT_LOCAL_ENGINE_URL, username = None, password = None):
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
        return self.engine.isOnline();
    
    def close(self):
        if self.engine.isOnline():
            return self.engine.deauthenticate();
        return True
        
    

