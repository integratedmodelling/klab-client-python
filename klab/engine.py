import requests
from requests.exceptions import HTTPError
from .utils import DEFAULT_LOCAL_ENGINE_URL, API, KLAB_VERSION, USER_AGENT_PLATFORM

class Engine:
    """

    """
    token: str
    url: str

    def __init__(self, url):
        self.url = url
        while self.url.endswith("/"):
            self.url = self.url[0:-1]

    # def authenticate(self, username = None, password = None):
    #     if username and password:
    #         pass
    #     else:
    #         response = requests.get(api_url)

    def authenticate(self):
        """Local engine login, no auth necessary."""
		
        requestUrl = self.makeUrl(API.PING)
        userAgent = self.getUserAgent()
        headers = {
            "User-Agent": userAgent,
            "Accept":"application/json"
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
        # requestUrl = self.makeUrl(API.DEAUTHENTICATE_USER)
        # try: 
        #     response = requests.post(requestUrl, headers=headers)
        #     response.raise_for_status()
        # except Exception:
        #     return False
        # else:
        return True

    def isOnline(self):
        return self.token != None


    def get(self, endpoint, parameters=None):
        pass


    def makeUrl(self, endpoint, parameters=[]):
        parms = ""
        if parameters:
            for i in range(0, len(parameters)):
                if parms == "":
                    parms += "?"
                else:
                    parms += "&"
                parms += str(parameters[i])
                i+=1
                parms += "=" + str(parameters[i])

        return f"{self.url}{endpoint}{parms}"
    
    def getUserAgent(self):
        return "k.LAB/" + KLAB_VERSION + " (" + USER_AGENT_PLATFORM + ")"
	
	