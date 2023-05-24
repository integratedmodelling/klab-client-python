from enum import Enum
from .exceptions import KlabIllegalArgumentException
import re

API_BASE = "/api/v2"
PUBLIC_BASE = API_BASE + "/public"

KLAB_VERSION = "0.11.0"
"""
Main version number for the whole k.LAB software stack, which is expected to
have synchronized release numbers. Change this whenever a new version is
released.
"""

USER_AGENT_PLATFORM = "client:klab-api"
"""Platform segment for User-Agent header in API requests."""

DEFAULT_LOCAL_ENGINE_URL = "http://127.0.0.1:8283/modeler"

POLLING_INTERVAL_SEC = 2

P_EXPORT = "{export}"
P_CONTEXT = "{context}"
P_OBSERVATION = "{observation}"
P_TICKET = "{ticket}"
P_ESTIMATE = "{estimate}"


class Export(Enum):
    STRUCTURE = "structure"
    DATA = "data"
    VIEW = "view"
    LEGEND = "legend"
    REPORT = "report"
    DATAFLOW = "dataflow"
    PROVENANCE_FULL = "provenance_full"
    PROVENANCE_SIMPLIFIED = "provenance_simplified"


class ExportFormat(Enum):
    PNG_IMAGE = ("image/png", [Export.DATA, Export.LEGEND, Export.VIEW])
    GEOTIFF_RASTER = ("image/tiff", [Export.DATA])
    GEOJSON_FEATURES = ("application/json", [Export.DATA])
    JSON_CODE = ("application/json", [Export.LEGEND, Export.STRUCTURE])
    KDL_CODE = ("text/plain", [Export.DATAFLOW])
    KIM_CODE = ("text/plain", [Export.PROVENANCE_FULL, Export.PROVENANCE_SIMPLIFIED])
    ELK_GRAPH_JSON = ("application/json", [Export.DATAFLOW, Export.PROVENANCE_FULL, Export.PROVENANCE_SIMPLIFIED])
    CSV_TABLE = ("text/csv", [Export.VIEW])
    PDF_DOCUMENT = ("application/pdf", [Export.REPORT])
    EXCEL_TABLE = ("application/vnd.ms-excel", [Export.VIEW])
    WORD_DOCUMENT = ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", [Export.REPORT])
    BYTESTREAM = ("application/octet-stream", [Export.DATA])

    def getMediaType(self) -> str:
        return self.value[0]
    
    def isText(self) -> bool:
        mt = self.value[0]
        return "text/plain" == mt or "application/json" == mt or "text/csv" == mt
    
    def isExportAllowed(self, export: Export) -> bool:
        allowedList = self.value[1]
        return export in allowedList
    
    def __str__(self) -> str:
        return f"{self.value[0]}"

    @staticmethod
    def fromMediaType(value: str):
        if not value:
            return None
        for ef in ExportFormat:
            if ef.value.lower() == value.lower():
                return ef
        raise KlabIllegalArgumentException(f"No ExportFormat available by the value: {value}")

    @staticmethod
    def fromMediaTypeList(value: list):
        efl = []
        for v in value:
            ef = ExportFormat.fromValue(v)
            if ef:
                efl.append(ef)
            
        return efl
        
    
class EndPoint(Enum):
    AUTHENTICATE_USER = API_BASE + "/users/log-in"
    """Called by users to log in and receive an authentication token for a remote engine. Duplicate from HUB. 
    POST with username and password in data."""

    DEAUTHENTICATE_USER = API_BASE + "/users/log-out"
    """Called by users to log off from a remote engine. Duplicate from HUB."""

    CREATE_CONTEXT = PUBLIC_BASE + "/submit/context"
    """Post a `ContextRequest` to create a context or get an estimate for it. Returns a ticket to poll and retrieve 
    the outcome when done."""

    OBSERVE_IN_CONTEXT = PUBLIC_BASE + "/submit/observation/" + P_CONTEXT
    """Post a `ObservationRequest` to make an observation in an existing context or get an estimate for it. Returns 
    a ticket to poll and retrieve the outcome when done."""

    SUBMIT_ESTIMATE = PUBLIC_BASE + "/submit/estimate/" + P_ESTIMATE
    """Call as GET with an estimate ID to accept the estimate and start an observation (context
    or observation) for which an estimation was previously made. Returns the ticket
    corresponding to the running task."""

    EXPORT_DATA = PUBLIC_BASE + "/export/" + P_EXPORT + "/" + P_OBSERVATION
    """Retrieve any of the exportable items in the {@link Export} enum. The Observation path
    variable should contain the context ID for those request that apply to the entire
    context, like report, dataflows etc. The Accept header selects the format, which must be
    appropriate for the content requested."""

    TICKET_INFO = PUBLIC_BASE + "/ticket/info/" + P_TICKET
    """Check the status of the passed ticket. Same as the one in API.TICKET but only accessing
    tickets created by calls in the public API and requesting the session as a parameter. GET
    request returns the entire ticket for inspection; asking for a ticket not created in the
    same session is an error."""

    PING = "/ping"
    """
        Ping service. Accepts HEAD requests to simply check for heartbeat, or GET to return
        meaningful info on the engine's status. If the engine is local (i.e. the request comes from a
        local IP) and accepts local connections, also adds an engine session ID so that it can be
        connected to.
    """

    MESSAGE = "/message"
    """STOMP endpoint for client/server notifications. Handled through Websockets protocol."""

    CAPABILITIES = "/capabilities";
    """Public capabilities endpoint. Anything that has an API has capabilities."""

# class API():

#     API_BASE = "/api/v2"
#     """Base for many, but still not all, endpoints. TODO must use everywhere."""

#     def url(template, kvp):
#         """
#         Use to simply substitute parameters in URLs:
#         `API.url(API.RESOURCE.RESOLVE_URN, API.P_URN, urn)`
#         """
#         ret = template
#         if kvp:
#             for i in range(0, len(kvp)):
#                 what = kvp[i]
#                 i+=1
#                 wit = kvp[i]
#                 ret = template.replace(what, wit)
        
#         return ret
    
    
#     P_URN = "{urn}"
#     """Parameter: the URN being resolved in any endpoints that access resources."""

#     P_QUERY = "{query}"
#     """Parameter: query for any GET call used to search"""

#     P_CODELIST = "{codelist}"
#     """Parameter: a codelist name for GET requests."""


#     AUTHENTICATE_USER = "/api/v2/users/log-in"
#     """
#     Called by users to log in and receive an authentication token for a remote engine.
#     POST with username and password in data.
#     """

#     DEAUTHENTICATE_USER = "/api/v2/users/log-out"
#     """Called by users to log off from a remote engine."""


class NumberUtils():

    NaN = float('nan')
    POSITIVE_INFINITY = float('inf')
    NEGATIVE_INFINITY = float('-inf')

    @staticmethod
    def encodesInt(val) -> bool:
        try:
            int(val)
            return True
        except ValueError:
            return False

    @staticmethod
    def encodesFloat(val) -> bool:
        try:
            float(val)
            return True
        except ValueError:
            return False

    @staticmethod
    def objectArrayFromString(array: str,  splitRegex: str, cls: type) -> list:

        if array.startswith("["):
            array = array[1:]
        
        if array.endswith("]"):
            array = array[:-1]
        
        s = re.split(splitRegex, array)
        ret = []
        for i in range(0, len(s)):
                try:
                    ret.append(int(s[i]))
                except ValueError:
                    try:
                        ret.append(float(s[i]))
                    except ValueError:
                        try:
                            ret.append(bool(s[i]))
                        except ValueError:
                            ret.append(s[i])
            # if cls and !Object.class.equals(cls)) {
            #     ret[i] = Utils.parseAsType(s[i], cls);
            # } else {
                # if (encodesDouble(s[i].trim())) {
                #     ret[i] = Double.parseDouble(s[i].trim());
                # } else if (encodesInteger(s[i].trim())) {
                #     ret[i] = Integer.parseInt(s[i].trim());
                # } else {
                #     ret[i] = s[i];
                # }
        return ret

    @staticmethod
    def podArrayFromString(array: str, splitRegex: str, cls):
        pods = NumberUtils.objectArrayFromString(array, splitRegex, cls)
        iret = [None]*len(pods)
        fret = [None]*len(pods)
        bret = [None]*len(pods)
        nd = 0
        ni = 0
        cl = 0

        for i in  range(0, len(pods)):
            if isinstance(pods[i], float):
                cl = 4
                fret[i] = pods[i]
                nd+=1
            elif isinstance(pods[i], int):
                cl = 2
                iret[i] = pods[i]
                ni+=1
            elif isinstance(pods[i],bool):
                cl = 5
                bret[i] = pods[i]
                ni+=1
            
        if cl == 2:
            return iret
        elif cl == 4:
            return fret
        elif cl == 5:
            return bret
        
        raise KlabIllegalArgumentException("cannot turn array into PODs: type not handled")
