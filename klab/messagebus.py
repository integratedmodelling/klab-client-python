from enum import Enum
import json
import logging
import random
import string
import threading
import time
import uuid

import websocket

from .exceptions import KlabRemoteException

LOGGER = logging.getLogger(__name__)

NUL = "\x00"


class MessageClass(Enum):
    """
    Mirrors (the subset of) org.integratedmodelling.klab.api.monitoring.IMessage.MessageClass
    needed to talk to the engine's message bus.
    """
    Void = "Void"
    Query = "Query"
    Search = "Search"
    UserInterface = "UserInterface"
    EngineLifecycle = "EngineLifecycle"
    Notification = "Notification"


class MessageType(Enum):
    """
    Mirrors (the subset of) org.integratedmodelling.klab.api.monitoring.IMessage.Type
    needed to talk to the engine's message bus.
    """
    Void = "Void"
    SemanticSearch = "SemanticSearch"
    SubmitSearch = "SubmitSearch"
    MatchAction = "MatchAction"
    SemanticMatch = "SemanticMatch"
    QueryResult = "QueryResult"
    QueryStatus = "QueryStatus"
    EngineUp = "EngineUp"
    EngineDown = "EngineDown"


class Message():
    """Python mirror of org.integratedmodelling.klab.monitoring.Message."""

    def __init__(self) -> None:
        self.type: MessageType = None
        self.messageClass: MessageClass = None
        self.identity: str = None
        self.payloadClass: str = None
        self.payload = None
        self.id: str = str(uuid.uuid4())
        self.inResponseTo: str = None
        self.timestamp: int = int(time.time() * 1000)
        self.repeatability: str = "Once"

    @staticmethod
    def create(identity: str, messageClass: MessageClass, messageType: MessageType, payload=None,
               payloadClass: str = None) -> "Message":
        message = Message()
        message.identity = identity
        message.messageClass = messageClass
        message.type = messageType
        message.payload = payload
        message.payloadClass = payloadClass
        return message

    def toDict(self) -> dict:
        return {
            "type": self.type.value if isinstance(self.type, MessageType) else self.type,
            "messageClass": self.messageClass.value if isinstance(self.messageClass, MessageClass) else self.messageClass,
            "identity": self.identity,
            "payloadClass": self.payloadClass,
            "payload": self.payload,
            "id": self.id,
            "inResponseTo": self.inResponseTo,
            "timestamp": self.timestamp,
            "repeatability": self.repeatability,
        }

    def toJson(self) -> str:
        return json.dumps(self.toDict())

    @staticmethod
    def fromDict(data: dict) -> "Message":
        message = Message()
        if not data:
            return message
        message.type = data.get("type")
        message.messageClass = data.get("messageClass")
        message.identity = data.get("identity")
        message.payloadClass = data.get("payloadClass")
        message.payload = data.get("payload")
        message.id = data.get("id")
        message.inResponseTo = data.get("inResponseTo")
        message.timestamp = data.get("timestamp")
        message.repeatability = data.get("repeatability")
        return message

    def __str__(self) -> str:
        return f"{{{self.identity}: {self.messageClass}/{self.type}: {self.payload}}}"


def _stomp_frame(command: str, headers: dict = None, body: str = "") -> str:
    lines = [command]
    for key, value in (headers or {}).items():
        lines.append(f"{key}:{value}")
    return "\n".join(lines) + "\n\n" + body + NUL


def _parse_stomp_frame(raw: str):
    raw = raw.rstrip(NUL)
    if not raw:
        return None, {}, ""
    head, _, body = raw.partition("\n\n")
    lines = head.split("\n")
    command = lines[0]
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key] = value
    return command, headers, body


class MessageBus():
    """
    Minimal SockJS + STOMP client replicating what the k.LAB IDE/modeler front end does over
    the engine's websocket message bus (see WebsocketsConfiguration/WebsocketsMessageBus on the
    Java side): connect with SockJS over the "/message" endpoint, CONNECT with STOMP, SUBSCRIBE
    to "/message/{identity}" and SEND application messages to "/klab/message".

    This is a much lighter substitute for what a full Stomp.js/SockJS client does in the browser,
    supporting only what is needed to post messages and correlate responses (either by
    `inResponseTo`, mirroring `IMessageBus.post(message, responder)`/`ask(message)` on the Java
    side, or through a generic listener for unsolicited messages, mirroring subscription-based
    receivers such as `KlabPeer`).
    """

    def __init__(self, engineUrl: str) -> None:
        self._httpUrl = engineUrl.rstrip("/")
        self._identity = None
        self._ws: websocket.WebSocketApp = None
        self._wsThread: threading.Thread = None
        self._connectedEvent = threading.Event()
        self._subscribedEvent = threading.Event()
        self._responders = {}
        self._respondersLock = threading.Lock()
        self._pending = {}
        self._pendingLock = threading.Lock()
        self._listeners = []
        self._subId = "sub-0"
        self._closed = False

    def _wsUrl(self) -> str:
        scheme = "wss" if self._httpUrl.startswith("https") else "ws"
        rest = self._httpUrl.split("://", 1)[1]
        server = str(random.randint(0, 999)).zfill(3)
        session = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        return f"{scheme}://{rest}/message/{server}/{session}/websocket"

    def connect(self, identity: str, headers: list = None, cookie: str = None, timeoutSeconds: float = 10.0) -> None:
        """
        Open the websocket, complete the SockJS+STOMP handshake and subscribe for `identity`.

        `headers`/`cookie` are forwarded on the handshake request so that, on a remote/clustered
        engine sitting behind a load balancer, this connection lands on the same backend instance
        that handled the login: the engine keeps registered identities in an in-process map, so a
        websocket routed to a different instance than the one that authenticated the session would
        silently never find it and every request would time out with no error at all.
        """

        self._identity = identity
        url = self._wsUrl()

        self._ws = websocket.WebSocketApp(
            url,
            header=headers,
            cookie=cookie,
            on_message=self._onWsMessage,
            on_error=self._onWsError,
            on_close=self._onWsClose,
        )
        self._wsThread = threading.Thread(target=self._ws.run_forever, kwargs={"ping_interval": 20}, daemon=True)
        self._wsThread.start()

        if not self._subscribedEvent.wait(timeoutSeconds):
            raise KlabRemoteException(f"timed out connecting to the message bus at {url}")

    def isConnected(self) -> bool:
        return self._connectedEvent.is_set() and not self._closed

    def _onWsError(self, ws, error) -> None:
        LOGGER.error(f"message bus error: {error}")

    def _onWsClose(self, ws, code, msg) -> None:
        self._connectedEvent.clear()
        self._subscribedEvent.clear()

    def _onWsMessage(self, ws, raw: str) -> None:
        if not raw:
            return
        kind = raw[0]
        if kind == "o":
            # SockJS session open: start the STOMP handshake.
            self._sendSockjs([_stomp_frame("CONNECT", {"accept-version": "1.1,1.2", "heart-beat": "0,0"})])
        elif kind == "h":
            pass
        elif kind == "c":
            self._connectedEvent.clear()
            self._subscribedEvent.clear()
        elif kind == "a":
            for frame in json.loads(raw[1:]):
                self._handleStompFrame(frame)

    def _sendSockjs(self, stompFrames: list) -> None:
        self._ws.send(json.dumps(stompFrames))

    def _handleStompFrame(self, rawFrame: str) -> None:
        command, _headers, body = _parse_stomp_frame(rawFrame)
        if command == "CONNECTED":
            self._connectedEvent.set()
            self._subscribe()
        elif command == "MESSAGE":
            self._dispatchPayload(body)
        elif command == "ERROR":
            LOGGER.error(f"STOMP error from engine: {body}")

    def _subscribe(self) -> None:
        destination = f"/message/{self._identity}"
        frame = _stomp_frame("SUBSCRIBE", {"id": self._subId, "destination": destination})
        self._sendSockjs([frame])
        self._subscribedEvent.set()

    def _dispatchPayload(self, body: str) -> None:
        try:
            data = json.loads(body)
        except (TypeError, ValueError):
            return

        message = Message.fromDict(data)
        inResponseTo = message.inResponseTo

        if inResponseTo:
            with self._pendingLock:
                pending = self._pending.pop(inResponseTo, None)
            if pending is not None:
                event, holder = pending
                holder.append(message)
                event.set()
                return

            with self._respondersLock:
                responder = self._responders.pop(inResponseTo, None)
            if responder is not None:
                responder(message)
                return

        for listener in list(self._listeners):
            try:
                listener(message)
            except Exception:
                LOGGER.exception("error in message bus listener")

    def subscribe(self, listener) -> None:
        """Register a listener called for every message that is not a correlated response,
        mirroring subscription-based receivers on the Java side (e.g. KlabPeer)."""
        self._listeners.append(listener)

    def unsubscribe(self, listener) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    def post(self, message: Message, responder=None) -> None:
        """Post a message, optionally registering a responder called when a message with
        `inResponseTo` equal to this message's id arrives. Mirrors IMessageBus.post(message)/
        post(message, responder)."""
        if responder is not None:
            with self._respondersLock:
                self._responders[message.id] = responder
        self._sendAppMessage(message)

    def ask(self, message: Message, timeoutSeconds: float = 30.0) -> Message:
        """Post a message and block until the correlated response arrives. Mirrors
        IMessageBus.ask(message)."""
        event = threading.Event()
        holder = []
        with self._pendingLock:
            self._pending[message.id] = (event, holder)

        self._sendAppMessage(message)

        if not event.wait(timeoutSeconds):
            with self._pendingLock:
                self._pending.pop(message.id, None)
            raise KlabRemoteException(f"timed out waiting for a response to message {message.id}")

        return holder[0]

    def _sendAppMessage(self, message: Message) -> None:
        if not self._subscribedEvent.wait(10.0):
            raise KlabRemoteException("message bus is not connected")
        frame = _stomp_frame(
            "SEND", {"destination": "/klab/message", "content-type": "application/json"}, message.toJson())
        self._sendSockjs([frame])

    def close(self) -> None:
        self._closed = True
        try:
            if self._ws:
                self._ws.close()
        except Exception:
            pass
