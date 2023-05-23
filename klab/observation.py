from enum import Enum
from .utils import NumberUtils, Export, ExportFormat
from .observable import Observable, Range
from .exceptions import *
import io
import klab.engine as E
from .ticket import Estimate, Ticket
from .types import ObservationType, ValueType
from .references import ObservationReference


class ObservationExportFormat():
    """Export formats for each observation."""

    def __init__(self, label: str = None, value: str = None, adapter: str = None, extension: str = None):
        self._label = label
        self._value = value
        self._adapter = adapter
        self._extension = extension

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, label):
        self._label = label

    @property
    def adapter(self) -> str:
        return self._adapter

    @adapter.setter
    def adapter(self, adapter):
        self._adapter = adapter

    @property
    def extension(self) -> str:
        return self._extension

    @extension.setter
    def extension(self, extension):
        self._extension = extension


class Observation():

    def __init__(self, reference: ObservationReference, engine):
        self.reference = reference
        self.engine = engine
        self.catalogIds = {}
        self.catalog = {}

    def getSemantics(self) -> set:
        return self.reference.semantics

    def getObservable(self) -> Observable:
        return Observable(self.reference.observable)

    # @Override
    # public boolean is(Object type) {
    #     // TODO
    #     return false;
    # }

    def notifyObservation(self, id: str):
        names = self.reference.childIds.keys()
        for name in names:
            if id == self.reference.childIds.get(name):
                self.catalogIds[name] = id
                self.getObservation(name)
                break

    def exportToFile(self, target: Export, eformat: ExportFormat,  path: str, parameters: list = []) -> bool:
        stream = io.BytesIO()
        self.export(target, eformat, stream, parameters)
        with open(path, 'wb') as file:
            file.write(stream.getbuffer())
        
        return True 

    def exportToString(self, target: Export, eformat: ExportFormat) -> str:
        if not eformat.isText():
            raise KlabIllegalArgumentException(f"illegal export format {eformat} for string export of {target.name}")
        
        stream = io.BytesIO()
        self.export(target, eformat, stream)

        bytesBuffer = stream.getvalue()
        return bytesBuffer.decode("utf-8")

    def export(self, target: Export, eformat: ExportFormat,  output:io.BytesIO,  parameters: list = []) -> bool:
        if not eformat.isExportAllowed(target):
            raise KlabIllegalArgumentException(
                "export format is incompatible with target")

        return self.engine.streamExport(self.reference.id, target, eformat, output, parameters)

    def getObservation(self, name: str):
        id = self.catalogIds.get(name)
        if id:
            ret = self.catalog.get(id)
            if not ret:
                ref = self.engine.getObservation(id)
                if ref and ref.id:
                    ret = Observation(ref, self.engine)
                    self.catalog[id] = ret
                else:
                    raise KlabRemoteException(
                        f"server error retrieving observation {id}")
            return ret
        return None

    # @Override
    # public Context promote() {
    #     return null;
    # }

    def getDataRange(self) -> Range:
        if not self.reference or self.reference.observationType != ObservationType.STATE:
            raise KlabIllegalStateException(
                "getDataRange called on a non-state or null observation")

        return Range(lower=self.reference.dataSummary.minValue, upper=self.reference.dataSummary.maxValue)

    def getScalarValue(self):
        literalValue = self.reference.overallValue
        if literalValue:
            if self.reference.valueType == ValueType.BOOLEAN:
                return bool(literalValue)
            elif self.reference.valueType == ValueType.NUMBER:
                return float(literalValue)

        return literalValue

    def getAggregatedValue(self):
        if not self.reference or self.reference.observationType != ObservationType.STATE:
            raise KlabIllegalStateException(
                "getDataRange called on a non-state or null observation")

        #  FIXME this is NOT the correct result
        return self.reference.dataSummary.mean

    def isEmpty(self) -> bool:
        return self.reference == None


class ObservationRequest():

    def __init__(self, urn: str = None, contextId: str = None, contextSearchId: str = None) -> None:
        self._urn = urn
        self._contextId = contextId
        self._searchContextId = contextSearchId
        self._estimate = False
        self._estimatedCost = -1
        self._scenarios = []
        self._states = {}
        self._objects = {}

    def toJson(self):
        es = str(self._estimate).lower()

        scen = [str(s) for s in self._scenarios]
        scen = str(scen).replace("'", "\"")

        st = str(self._states).replace("'", "\"")
        ob = str(self._objects).replace("'", "\"")

        scId = ""
        if self.searchContextId:
            scId = """"contextSearchId":"{0}", """.format(self.searchContextId)

        ret = """{{"urn":"{0}","contextId":"{1}",{2}"estimate":{3},"estimatedCost":{4},"scenarios":{5},"states":{6},"objects":{7}}}"""
        ret = ret.format(self._urn, self._contextId, scId, es, self._estimatedCost, scen, st, ob)

        ret = ret.encode('utf-8').decode('unicode-escape')
        return ret

    @property
    def urn(self) -> str:
        return self._urn

    @urn.setter
    def urn(self, urn):
        self._urn = urn

    @property
    def searchContextId(self) -> str:
        return self._searchContextId

    @searchContextId.setter
    def searchContextId(self, searchContextId):
        self._searchContextId = searchContextId

    @property
    def contextId(self) -> str:
        return self._contextId

    @contextId.setter
    def contextId(self, contextId):
        self._contextId = contextId

    @property
    def scenarios(self) -> list:
        return self._scenarios

    @scenarios.setter
    def scenarios(self, scenarios):
        self._scenarios = scenarios

    @property
    def estimate(self) -> bool:
        return self._estimate

    @estimate.setter
    def estimate(self, estimate):
        self._estimate = estimate

    @property
    def estimatedCost(self) -> int:
        return self._estimatedCost

    @estimatedCost.setter
    def estimatedCost(self, estimatedCost):
        self._estimatedCost = estimatedCost

    @property
    def states(self) -> dict:
        return self._states

    @states.setter
    def states(self, states):
        self._states = states

    @property
    def objects(self) -> dict:
        return self._objects

    @objects.setter
    def objects(self, objects):
        self._objects = objects

    def __str__(self) -> str:
        return f"ObservationRequest [\n\turn={self.urn}\n\tcontextId={self.contextId}\n\tsearchContextId={self.searchContextId}\n\tscenarios={self.scenarios}]"


class ContextRequest():

    def __init__(self) -> None:
        self._geometry = None
        self._contextType = None
        self._urn = None
        self._scenarios = []
        self._observables = []
        self._estimate = False
        self._estimatedCost = -1

    def toJson(self):
        es = str(self._estimate).lower()

        obs = [str(o) for o in self._observables]
        obs = str(obs).replace("'", "\"")
        scen = [str(s) for s in self._scenarios]
        scen = str(scen).replace("'", "\"")

        ret = """{{"geometry":"{0}","contextType":"{1}","observables":{2},"scenarios":{3},"estimate":{4},"estimatedCost":{5}}}"""
        ret = ret.format(self._geometry, self._contextType,
                         obs, scen, es, self._estimatedCost)

        ret = ret.encode('utf-8').decode('unicode-escape')
        return ret

    @property
    def geometry(self) -> str:
        return self._geometry

    @geometry.setter
    def geometry(self, geometry):
        self._geometry = geometry

    @property
    def contextType(self) -> str:
        return self._contextType

    @contextType.setter
    def contextType(self, contextType):
        self._contextType = contextType

    @property
    def urn(self) -> str:
        return self._urn

    @urn.setter
    def urn(self, urn):
        self._urn = urn

    @property
    def scenarios(self) -> list:
        return self._scenarios

    @scenarios.setter
    def scenarios(self, scenarios):
        self._scenarios = scenarios

    @property
    def observables(self) -> list:
        return self._observables

    @observables.setter
    def observables(self, observables):
        self._observables = observables

    @property
    def estimate(self) -> bool:
        return self._estimate

    @estimate.setter
    def estimate(self, estimate):
        self._estimate = estimate

    @property
    def estimatedCost(self) -> int:
        return self._estimatedCost

    @estimatedCost.setter
    def estimatedCost(self, estimatedCost):
        self._estimatedCost = estimatedCost

    def __str__(self) -> str:
        return f"ContextRequest [\n\turn={self.urn}\n\contextType={self.contextType}\n\geometry={self.geometry}\n\tscenarios={self.scenarios}]"


class Context(Observation):

    def __init__(self, reference: ObservationReference, engine):
        super().__init__(reference, engine)

        # if defined, these are submitted at the next submit() before the main
        # observable is queried, then cleared.
        self.injectedStates = []  # supposed to be (Observable, Object)
        self.injectedObjects = []  # supposed to be (Observable, IGeometry)

    def estimate(self, observable: Observable, arguments: list = []):
        request = ObservationRequest()
        request.contextId = self.reference.id
        request.estimate = False
        request.urn = str(observable)

        for state in self.injectedStates:
            # state is a tuple of (Observable, Object)
            request.states[str(state[0])] = str(state[1])

        for object in self.injectedObjects:
            # object is a tuple of (Observable, IGeometry)
            request.states[str(object[0])] = str(object[1].encode())

        self.injectedStates.clear()
        self.injectedObjects.clear()

        for o in arguments:
            if isinstance(o, str):
                request.scenarios.append(o)

        ticket = self.engine.submitObservation(request)
        if ticket:
            return E.TicketHandler(self.engine, ticket.id, self)

        raise KlabIllegalArgumentException(
            f"Cannot build estimate request from arguments: {arguments}")

    def submit(self, observable: Observable, arguments: list = []):

        request = ObservationRequest()
        request.contextId = self.reference.id
        request.estimate = False
        request.urn = str(observable)

        for state in self.injectedStates:
            # state is a tuple of (Observable, Object)
            request.states[str(state[0])] = str(state[1])

        for object in self.injectedObjects:
            # object is a tuple of (Observable, IGeometry)
            request.states[str(object[0])] = str(object[1].encode())

        self.injectedStates.clear()
        self.injectedObjects.clear()

        for o in arguments:
            if isinstance(o, str):
                request.scenarios.append(o)

        ticket = self.engine.submitObservation(request)
        if ticket:
            return E.TicketHandler(self.engine, ticket.id, self)

        raise KlabIllegalArgumentException(
            f"Cannot build observation request from arguments: {arguments}")

    # @Override
    # public Future<Observation> submit(Estimate estimate) {

    #     if (((EstimateImpl) estimate).getTicketType() != Type.ObservationEstimate) {
    #         throw new KlabIllegalArgumentException("the estimate passed is not a context estimate");
    #     }
    #     String ticket = engine.submitEstimate(((EstimateImpl) estimate).getEstimateId());
    #     if (ticket != null) {
    #         // the handler updates the context catalog when the observation arrives
    #         return new TicketHandler<Observation>(engine, ticket, this);
    #     }

    #     throw new KlabIllegalStateException("estimate cannot be used");

    # }

    def getDataflow(self, eformat: ExportFormat) -> str:
        if eformat != ExportFormat.ELK_GRAPH_JSON and eformat != ExportFormat.KDL_CODE:
            raise KlabIllegalArgumentException(f"cannot export a dataflow to {eformat.name}")
        
        stream = io.BytesIO()
        self.engine.streamExport(self.reference.id, Export.DATAFLOW, eformat, stream)
        bytesBuffer = stream.getvalue()
        return bytesBuffer.decode("utf-8")
    
    def getProvenance(self, simplified: bool, eformat: ExportFormat) -> str:
        if eformat != ExportFormat.ELK_GRAPH_JSON and eformat != ExportFormat.KIM_CODE:
            raise KlabIllegalArgumentException(f"cannot export the provenance graph to {eformat.name}")
        
        exp = Export.PROVENANCE_FULL
        if simplified:
            exp = Export.PROVENANCE_SIMPLIFIED

        stream = io.BytesIO()
        self.engine.streamExport(self.reference.id, exp, eformat, stream)
        bytesBuffer = stream.getvalue()
        return bytesBuffer.decode("utf-8")

    # @Override
    # public Context with(Observable concept, Object value) {

    #     if (value instanceof IGeometry) {
    #         if (concept.getName() == null) {
    #             throw new KlabIllegalStateException("observables that create objects must be given an explicit name");
    #         }
    #         this.injectedObjects.add(new Pair<>(concept, (IGeometry) value));
    #     } else {
    #         this.injectedStates.add(new Pair<>(concept, value));
    #     }

    #     return this;
    # }

    def updateWith(self, ret: Observation):
        """
        Called after an observation to update the context data and ensure the context
        has the new observation in its catalog.
        """
        self.reference = self.engine.getObservation(self.reference.id)
        names = list(self.reference.childIds.keys())
        for name in names:
            if ret.reference.id == self.reference.childIds.get(name):
                self.catalogIds[name] = ret.reference.id
                self.catalog[ret.reference.id] = ret
                break
