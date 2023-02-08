from .engine import Engine
from .utils import DEFAULT_LOCAL_ENGINE_URL

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
    def createLocalDefault():
        """
        Connect to local server. Equivalent to `create(localEngineUrl)` using 
        the default local server URL on port 8283.
        
        Returns
        -------
        Klab:
            The created local default Klab instance.
        """
        return Klab(DEFAULT_LOCAL_ENGINE_URL)

    @staticmethod
    def createRemote(remoteEngineUrl, username, password):
        """
        Authenticate with a remote engine and open a new user session. Call `close()` to free
        remote resources.

        Parameters
        ----------
        remoteEngineUrl: str
            the url to the remote engine, something like: http://127.0.0.1:8283/modeler
        username:str
        password:str
            
        Returns
        -------
        Klab:
            The created remote Klab instance.
        """
        return Klab(remoteEngineUrl, username, password)
    
    @staticmethod
    def createLocal(localEngineUrl):
        """
        Authenticate with a local engine and open the default session. This does not require
        authentication but only works if the engine is running on the local network and is properly
        authenticated through a certificate. Calling `close()` is good practice but won't
        change the state of the session, which can be reconnected to if wished.

        Parameters
        ----------
        localEngineUrl: str
            the url to the local engine, something like: http://127.0.0.1:8283/modeler
            
        Returns
        -------
        Klab:
            The created local Klab instance.
        """
        return Klab(localEngineUrl)
    

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
        
    

