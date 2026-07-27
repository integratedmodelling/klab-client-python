from enum import Enum
import logging

import requests

from .exceptions import KlabIllegalArgumentException
from .messagebus import Message, MessageBus, MessageClass, MessageType
from .types import KimConceptType

LOGGER = logging.getLogger(__name__)


class SearchMode(Enum):
    """Mirrors org.integratedmodelling.klab.rest.SearchRequest.Mode."""
    SEMANTIC = "SEMANTIC"
    FREETEXT = "FREETEXT"
    UNDO = "UNDO"
    OPEN_SCOPE = "OPEN_SCOPE"
    CLOSE_SCOPE = "CLOSE_SCOPE"


class MatchType(Enum):
    """Mirrors org.integratedmodelling.klab.api.services.IIndexingService.Match.Type."""
    CONCEPT = "CONCEPT"
    PREFIX_OPERATOR = "PREFIX_OPERATOR"
    INFIX_OPERATOR = "INFIX_OPERATOR"
    OBSERVATION = "OBSERVATION"
    MODEL = "MODEL"
    MODIFIER = "MODIFIER"
    PRESET_OBSERVABLE = "PRESET_OBSERVABLE"
    RESOURCE = "RESOURCE"
    SEPARATOR = "SEPARATOR"
    OPEN_PARENTHESIS = "OPEN_PARENTHESIS"
    CLOSED_PARENTHESIS = "CLOSED_PARENTHESIS"
    VALUE_OPERATOR = "VALUE_OPERATOR"
    UNARY_OPERATOR = "UNARY_OPERATOR"
    SEMANTIC_MODIFIER = "SEMANTIC_MODIFIER"
    BINARY_OPERATOR = "BINARY_OPERATOR"
    INLINE_VALUE = "INLINE_VALUE"

    @staticmethod
    def fromValue(value: str):
        if not value:
            return None
        for mt in MatchType:
            if mt.value.lower() == value.lower():
                return mt
        raise KlabIllegalArgumentException(f"No MatchType available by the value: {value}")


class TokenClass(Enum):
    """Mirrors org.integratedmodelling.klab.rest.SearchMatch.TokenClass."""
    TOKEN = "TOKEN"
    TEXT = "TEXT"
    INTEGER = "INTEGER"
    DOUBLE = "DOUBLE"
    BOOLEAN = "BOOLEAN"
    UNIT = "UNIT"
    CURRENCY = "CURRENCY"

    @staticmethod
    def fromValue(value: str):
        if not value:
            return TokenClass.TOKEN
        for tc in TokenClass:
            if tc.value.lower() == value.lower():
                return tc
        raise KlabIllegalArgumentException(f"No TokenClass available by the value: {value}")


class SearchRequest():
    """
    Mirrors org.integratedmodelling.klab.rest.SearchRequest. Sent to the engine to execute a
    query with a partial match, incrementally as the user types.
    """

    def __init__(self) -> None:
        self.queryString: str = None
        self.contextId: str = None
        self.requestId: int = 0
        self.cancelSearch: bool = False
        self.defaultResults: bool = False
        self.maxResults: int = 9
        self.semanticTypes: set = set()
        self.matchTypes: set = set()
        self.searchMode: SearchMode = None

    def toDict(self) -> dict:
        return {
            "queryString": self.queryString,
            "contextId": self.contextId,
            "requestId": self.requestId,
            "cancelSearch": self.cancelSearch,
            "defaultResults": self.defaultResults,
            "maxResults": self.maxResults,
            "semanticTypes": [t.value for t in self.semanticTypes],
            "matchTypes": [t.value for t in self.matchTypes],
            "searchMode": self.searchMode.value if self.searchMode else None,
        }


class StyledKimToken():
    """Mirrors org.integratedmodelling.klab.rest.StyledKimToken. Read-only: sent by the engine."""

    def __init__(self) -> None:
        self.value: str = None
        self.color: str = None
        self.font: str = None
        self.description: str = None
        self.needsWhitespaceBefore: bool = False
        self.needsWhitespaceAfter: bool = False

    @staticmethod
    def fromDict(data: dict) -> "StyledKimToken":
        token = StyledKimToken()
        if not data:
            return token
        token.value = data.get("value")
        token.color = data.get("color")
        token.font = data.get("font")
        token.description = data.get("description")
        token.needsWhitespaceBefore = data.get("needsWhitespaceBefore", False)
        token.needsWhitespaceAfter = data.get("needsWhitespaceAfter", False)
        return token

    def __str__(self) -> str:
        return self.value or ""


class SearchMatch():
    """Mirrors org.integratedmodelling.klab.rest.SearchMatch. Read-only: sent by the engine."""

    def __init__(self) -> None:
        self.name: str = None
        self.id: str = None
        self.description: str = None
        self.index: int = 0
        self.typeLabel: str = None
        self.mainSemanticType: KimConceptType = None
        self.semanticType: set = set()
        self.matchType: MatchType = None
        self.nextTokenClass: TokenClass = TokenClass.TOKEN
        self.state: str = None
        self.extendedDescription: str = None
        self.openGroup: bool = False
        self.closeGroup: bool = False

    @staticmethod
    def fromDict(data: dict) -> "SearchMatch":
        match = SearchMatch()
        if not data:
            return match
        match.name = data.get("name")
        match.id = data.get("id")
        match.description = data.get("description")
        match.index = data.get("index", 0)
        match.typeLabel = data.get("typeLabel")
        match.mainSemanticType = KimConceptType.fromValue(data.get("mainSemanticType"))
        match.semanticType = KimConceptType.fromListToSet(data.get("semanticType") or [])
        match.matchType = MatchType.fromValue(data.get("matchType"))
        match.nextTokenClass = TokenClass.fromValue(data.get("nextTokenClass"))
        match.state = data.get("state")
        match.extendedDescription = data.get("extendedDescription")
        match.openGroup = data.get("openGroup", False)
        match.closeGroup = data.get("closeGroup", False)
        return match

    def __str__(self) -> str:
        return f"SearchMatch [id={self.id}, name={self.name}, matchType={self.matchType}]"


class SearchResponse():
    """Mirrors org.integratedmodelling.klab.rest.SearchResponse. Read-only: sent by the engine."""

    def __init__(self) -> None:
        self.contextId: str = None
        self.requestId: int = 0
        self.matches: list = []
        self.code: list = []
        self.error: bool = False
        self.last: bool = False
        self.elapsedTimeMs: int = 0
        self.errorMessage: str = None
        self.parenthesisDepth: int = 0

    @staticmethod
    def fromDict(data: dict) -> "SearchResponse":
        response = SearchResponse()
        if not data:
            return response
        response.contextId = data.get("contextId")
        response.requestId = data.get("requestId", 0)
        response.matches = [SearchMatch.fromDict(m) for m in (data.get("matches") or [])]
        response.code = [StyledKimToken.fromDict(c) for c in (data.get("code") or [])]
        response.error = data.get("error", False)
        response.last = data.get("last", False)
        response.elapsedTimeMs = data.get("elapsedTimeMs", 0)
        response.errorMessage = data.get("errorMessage")
        response.parenthesisDepth = data.get("parenthesisDepth", 0)
        return response


class SearchMatchAction():
    """
    Mirrors org.integratedmodelling.klab.rest.SearchMatchAction. Sent when one of the matches
    for the passed context ID was accepted by the user.
    """

    def __init__(self, contextId: str = None, matchId: str = None, matchIndex: int = -1,
                 added: bool = True) -> None:
        self.contextId = contextId
        self.matchId = matchId
        self.matchIndex = matchIndex
        self.added = added

    def toDict(self) -> dict:
        return {
            "contextId": self.contextId,
            "matchId": self.matchId,
            "matchIndex": self.matchIndex,
            "added": self.added,
        }


class QueryStatusResponse():
    """
    Mirrors org.integratedmodelling.klab.rest.QueryStatusResponse. Sent by the engine when a
    selection is made from a semantic search, reporting the status of the observable being built.
    """

    def __init__(self) -> None:
        self.code: list = []
        self.errors: list = []
        self.contextId: str = None
        self.currentType: KimConceptType = None
        self.description: str = None

    @staticmethod
    def fromDict(data: dict) -> "QueryStatusResponse":
        status = QueryStatusResponse()
        if not data:
            return status
        status.code = [StyledKimToken.fromDict(c) for c in (data.get("code") or [])]
        status.errors = list(data.get("errors") or [])
        status.contextId = data.get("contextId")
        status.currentType = KimConceptType.fromValue(data.get("currentType"))
        status.description = data.get("description")
        return status


class KnowledgeSearch():
    """
    Incremental knowledge search, ported from the k.LAB Modeler's
    org.integratedmodelling.klab.ide.views.SearchView#search(String) and the rest of that class'
    interaction with the engine's semantic search.

    Each call to `search(text)` sends a new SEMANTIC search request built on top of the context
    established by the previous one (so that consecutive calls refine the same expression, just
    like typing in the Modeler's search box), and returns the matches found so far. Accepting a
    match with `acceptMatch()` commits it to the expression under construction; `removeLastMatch()`
    undoes the last accepted match; `reset()` starts over.

    Use `Klab.knowledgeSearch()` to create one bound to the current session.
    """

    def __init__(self, engine) -> None:
        self._engine = engine
        self._identity = engine.session_id
        self._bus = MessageBus(engine.url)
        self._contextId: str = None
        self._requestId: int = 0
        self._accepted: list = []
        self._status: QueryStatusResponse = None

        # Forwarded on the websocket handshake so a remote/clustered engine routes this
        # connection to the same backend instance that authenticated the session; see
        # MessageBus.connect for why this matters.
        headers = []
        if engine.session_id:
            headers.append(f"klab-authorization: {engine.session_id}")
        if engine.authorization:
            headers.append(f"Authentication: {engine.authorization}")
        cookies = requests.utils.dict_from_cookiejar(engine.session.cookies)
        cookie = "; ".join(f"{k}={v}" for k, v in cookies.items())

        self._bus.connect(self._identity, headers=headers, cookie=cookie)
        self._bus.subscribe(self._handleUnsolicited)

    def _handleUnsolicited(self, message: Message) -> None:
        if message.messageClass == MessageClass.UserInterface.value and message.type == MessageType.QueryStatus.value:
            status = QueryStatusResponse.fromDict(message.payload)
            self._status = status
            self._contextId = status.contextId
        elif message.messageClass == MessageClass.Notification.value:
            LOGGER.warning(f"knowledge search: notification from engine: {message.payload}")

    @property
    def contextId(self) -> str:
        return self._contextId

    @property
    def accepted(self) -> list:
        """The list of SearchMatch objects accepted so far in this search."""
        return self._accepted

    @property
    def status(self) -> QueryStatusResponse:
        """The last QueryStatusResponse received (description/errors of the expression built so far)."""
        return self._status

    def search(self, text: str, maxResults: int = 50) -> SearchResponse:
        """
        Perform one step of the incremental semantic search, equivalent to SearchView.search(text)
        being called at each keystroke. Blocks until the engine responds.
        """

        if not text or not text.strip():
            raise KlabIllegalArgumentException("search text cannot be empty")

        request = SearchRequest()
        request.maxResults = maxResults
        request.queryString = text
        request.searchMode = SearchMode.SEMANTIC
        request.contextId = self._contextId
        request.requestId = self._requestId
        self._requestId += 1

        message = Message.create(self._identity, MessageClass.Search, MessageType.SemanticSearch,
                                  payload=request.toDict(), payloadClass="SearchRequest")

        response = self._bus.ask(message)
        searchResponse = SearchResponse.fromDict(response.payload)
        self._contextId = searchResponse.contextId
        return searchResponse

    def acceptMatch(self, match: SearchMatch) -> None:
        """Accept a match returned by `search()`, committing it to the expression being built."""

        self._accepted.append(match)
        action = SearchMatchAction(contextId=self._contextId, matchId=match.id, matchIndex=match.index)
        message = Message.create(self._identity, MessageClass.Search, MessageType.SemanticMatch,
                                  payload=action.toDict(), payloadClass="SearchMatchAction")
        self._bus.post(message)

    def removeLastMatch(self) -> None:
        """Undo the last accepted match."""

        if self._accepted:
            self._accepted.pop()

        request = SearchRequest()
        request.searchMode = SearchMode.UNDO
        request.contextId = self._contextId
        message = Message.create(self._identity, MessageClass.Search, MessageType.SemanticSearch,
                                  payload=request.toDict(), payloadClass="SearchRequest")
        self._bus.post(message)

    def openParenthesis(self) -> None:
        request = SearchRequest()
        request.searchMode = SearchMode.OPEN_SCOPE
        request.contextId = self._contextId
        message = Message.create(self._identity, MessageClass.Search, MessageType.SemanticSearch,
                                  payload=request.toDict(), payloadClass="SearchRequest")
        self._bus.post(message)

    def closeParenthesis(self) -> None:
        request = SearchRequest()
        request.searchMode = SearchMode.CLOSE_SCOPE
        request.contextId = self._contextId
        message = Message.create(self._identity, MessageClass.Search, MessageType.SemanticSearch,
                                  payload=request.toDict(), payloadClass="SearchRequest")
        self._bus.post(message)

    def getMatchedText(self) -> str:
        """The URN built so far by concatenating the ids of the accepted matches."""
        return " ".join(m.id for m in self._accepted)

    def reset(self) -> None:
        """Cancel the current search context and start over, mirroring SearchView.reset()."""

        request = SearchRequest()
        request.contextId = self._contextId
        request.cancelSearch = True
        message = Message.create(self._identity, MessageClass.Search, MessageType.SemanticSearch,
                                  payload=request.toDict(), payloadClass="SearchRequest")
        self._bus.post(message)

        self._accepted.clear()
        self._contextId = None
        self._status = None

    def close(self) -> None:
        """Release the underlying message bus connection."""
        self._bus.close()
