from enum import Enum


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

P_EXPORT = "{export}";
P_CONTEXT = "{context}";
P_OBSERVATION = "{observation}";
P_TICKET = "{ticket}";
P_ESTIMATE = "{estimate}";

class Export(Enum):
    STRUCTURE = "structure",
    DATA = "data",
    VIEW = "view",
    LEGEND = "legend",
    REPORT = "report",
    DATAFLOW = "dataflow",
    PROVENANCE_FULL = "provenance_full",
    PROVENANCE_SIMPLIFIED = "provenance_simplified"


ENDPOINT_AUTHENTICATE_USER = API_BASE + "/users/log-in"
"""Called by users to log in and receive an authentication token for a remote engine. Duplicate from HUB. POST with username and password in data."""

ENDPOINT_DEAUTHENTICATE_USER = API_BASE + "/users/log-out"
"""Called by users to log off from a remote engine. Duplicate from HUB."""

ENDPOINT_CREATE_CONTEXT = PUBLIC_BASE + "/submit/context"
"""Post a `ContextRequest` to create a context or get an estimate for it. Returns a ticket to poll and retrieve the outcome when done."""

ENDPOINT_OBSERVE_IN_CONTEXT = PUBLIC_BASE + "/submit/observation/" + P_CONTEXT
"""Post a `ObservationRequest` to make an observation in an existing context or get an estimate for it. Returns a a ticket to poll and retrieve the outcome when done."""

ENDPOINT_SUBMIT_ESTIMATE = PUBLIC_BASE + "/submit/estimate/" + P_ESTIMATE
"""Call as GET with an estimate ID to accept the estimate and start an observation (context
or observation) for which an estimation was previously made. Returns the ticket
corresponding to the running task."""

ENDPOINT_EXPORT_DATA = PUBLIC_BASE + "/export/" + P_EXPORT + "/" + P_OBSERVATION
"""Retrieve any of the exportable items in the {@link Export} enum. The Observation path
variable should contain the context ID for those request that apply to the entire
context, like report, dataflows etc. The Accept header selects the format, which must be
appropriate for the content requested."""

ENDPOINT_TICKET_INFO = PUBLIC_BASE + "/ticket/info/" + P_TICKET
"""Check the status of the passed ticket. Same as the one in API.TICKET but only accessing
tickets created by calls in the public API and requesting the session as a parameter. GET
request returns the entire ticket for inspection; asking for a ticket not created in the
same session is an error."""

class API():

    API_BASE = "/api/v2"
    """Base for many, but still not all, endpoints. TODO must use everywhere."""

    def url(template, kvp):
        """
        Use to simply substitute parameters in URLs:
        `API.url(API.RESOURCE.RESOLVE_URN, API.P_URN, urn)`
        """
        ret = template
        if kvp:
            for i in range(0, len(kvp)):
                what = kvp[i]
                i+=1
                wit = kvp[i]
                ret = template.replace(what, wit)
        
        return ret
    
    
    P_URN = "{urn}"
    """Parameter: the URN being resolved in any endpoints that access resources."""

    P_QUERY = "{query}"
    """Parameter: query for any GET call used to search"""

    P_CODELIST = "{codelist}"
    """Parameter: a codelist name for GET requests."""

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

    AUTHENTICATE_USER = "/api/v2/users/log-in"
    """
    Called by users to log in and receive an authentication token for a remote engine.
    POST with username and password in data.
    """

    DEAUTHENTICATE_USER = "/api/v2/users/log-out"
    """Called by users to log off from a remote engine."""