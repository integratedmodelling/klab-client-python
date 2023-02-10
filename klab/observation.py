from enum import Enum
from .geometry import ShapeType
from .utils import NumberUtils, Export, ExportFormat
from .observable import Observable, Range
from .exceptions import *
# from .engine import TicketHandler, Engine
import klab.engine as E
from .ticket import Estimate, Ticket


class ObservationExportFormat():
    """Export formats for each observation."""

    def __init_(self, label: str = None, value: str = None, adapter: str = None, extension: str = None):
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


class ObservationType(Enum):
    PROCESS = "PROCESS"
    STATE = "STATE"
    SUBJECT = "SUBJECT"
    CONFIGURATION = "CONFIGURATION"
    EVENT = "EVENT"
    RELATIONSHIP = "RELATIONSHIP"
    GROUP = "GROUP"
    VIEW = "VIEW"


class KimConceptType(Enum):
    OBSERVABLE = "OBSERVABLE"
    PREDICATE = "PREDICATE"
    QUALITY = "QUALITY"
    PROCESS = "PROCESS"
    SUBJECT = "SUBJECT"
    EVENT = "EVENT"
    RELATIONSHIP = "RELATIONSHIP"
    EXTENSIVE_PROPERTY = "EXTENSIVE_PROPERTY"
    INTENSIVE_PROPERTY = "INTENSIVE_PROPERTY"
    TRAIT = "TRAIT"
    IDENTITY = "IDENTITY"
    ATTRIBUTE = "ATTRIBUTE"
    REALM = "REALM"
    SUBJECTIVE = "SUBJECTIVE"
    INTERNAL = "INTERNAL"
    ROLE = "ROLE"
    DENIABLE = "DENIABLE"
    CONFIGURATION = "CONFIGURATION"
    ABSTRACT = "ABSTRACT"
    NOTHING = "NOTHING"
    ORDERING = "ORDERING"
    CLASS = "CLASS"
    QUANTITY = "QUANTITY"
    DOMAIN = "DOMAIN"
    ENERGY = "ENERGY"
    ENTROPY = "ENTROPY"
    LENGTH = "LENGTH"
    MASS = "MASS"
    VOLUME = "VOLUME"
    WEIGHT = "WEIGHT"
    MONEY = "MONEY"
    DURATION = "DURATION"
    AREA = "AREA"
    ACCELERATION = "ACCELERATION"
    PRIORITY = "PRIORITY"
    ELECTRIC_POTENTIAL = "ELECTRIC_POTENTIAL"
    CHARGE = "CHARGE"
    RESISTANCE = "RESISTANCE"
    RESISTIVITY = "RESISTIVITY"
    PRESSURE = "PRESSURE"
    ANGLE = "ANGLE"
    VELOCITY = "VELOCITY"
    TEMPERATURE = "TEMPERATURE"
    VISCOSITY = "VISCOSITY"
    AGENT = "AGENT"
    FUNCTIONAL = "FUNCTIONAL"
    STRUCTURAL = "STRUCTURAL"
    BIDIRECTIONAL = "BIDIRECTIONAL"
    UNIDIRECTIONAL = "UNIDIRECTIONAL"
    DELIBERATIVE = "DELIBERATIVE"
    INTERACTIVE = "INTERACTIVE"
    REACTIVE = "REACTIVE"
    DIRECT_OBSERVABLE = "DIRECT_OBSERVABLE"
    COUNTABLE = "COUNTABLE"
    UNCERTAINTY = "UNCERTAINTY"
    PROBABILITY = "PROBABILITY"
    PROPORTION = "PROPORTION"
    PERCENTAGE = "PERCENTAGE"
    NUMEROSITY = "NUMEROSITY"
    DISTANCE = "DISTANCE"
    RATIO = "RATIO"
    VALUE = "VALUE"
    OCCURRENCE = "OCCURRENCE"
    PRESENCE = "PRESENCE"
    EXTENT = "EXTENT"
    MACRO = "MACRO"
    AMOUNT = "AMOUNT"
    OBSERVABILITY = "OBSERVABILITY"
    CATEGORY = "CATEGORY"
    MAGNITUDE = "MAGNITUDE"
    QUANTIFIABLE = "QUANTIFIABLE"
    UNION = "UNION"
    INTERSECTION = "INTERSECTION"
    MONETARY_VALUE = "MONETARY_VALUE"
    RESCALING = "RESCALING"
    CHANGE = "CHANGE"
    RATE = "RATE"
    CHANGED = "CHANGED"
    AUTHORITY_IDENTITY = "AUTHORITY_IDENTITY"


class ValueType(Enum):
    """
    The value of this enum defines the type of values this observation contains.
        All non-quality observations have value type VOID.
    """
    VOID = "VOID"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    CATEGORY = "CATEGORY"


class GeometryType(Enum):
    """
    The value of this enum represents both the "nature" of the data
        representation and its natural geometry, specifying a way for an observation
        to be encoded when any representation of it is requested.

        TODO the name is really not right. At the moment it is part of observation
        bean methods so changing it is a little complex. It should probably be called
        DataEncoding or something like that.
    """

    RASTER = "RASTER"
    """A grid raster map with a number, boolean or category value type."""

    SHAPE = "SHAPE"
    """
    A single shape, of type determined by
    ObservationReference#getShapeType(). May be providing spatial context
    for a timeseries or other value, so not necessarily void.
    """

    SCALAR = "SCALAR"
    """
    A scalar value with no temporal or spatial representation. In this case,
    ObservationReference#getLiteralValue() returns a string
    representation of the scalar value.
    """

    TIMESERIES = "TIMESERIES"
    """
    Observation is distributed in time. It may or may not be located in space, in
    which case ObservationReference#getGeometryTypes() will contain also
    the spatial type). An observation may be a scalar at initialization and be
    turned into a timeseries after time transitions. The value type is never void
    if this is returned.
    """

    NETWORK = "NETWORK"
    """
    Observation is a structure of relationships connecting subjects.
    {@link ObservationReference#getStructure()} will return all vertices and
    connections The spatial and temporal character of the observations linked and
    linking will determine the best way of displaying the connections.
    """

    PROPORTIONS = "PROPORTIONS"
    """
    One possible "other" representations for derived products to be defined
    later. No worries about this now, for later use.
    """

    COLORMAP = "COLORMAP"
    """
    Used in requests to get the colormap instead of the image for an observation
    with distributed values.
    """

    TABLE = "TABLE",
    """
    Used in requests to get the values in tabular form instead of another
    representation.
    """

    RAW = "RAW"
    """Used in request to get the "raw" export data paired with an output format."""

    GROUP = "GROUP"
    """
    Corresponding to geometry #... - a folder, empty or ready to receive other
    observations. Communicated always with childrenCount == 0, children may
    arrive later.
    """


class DataSummary():

    def __init__(self) -> None:
        self._nodataProportion = 0.0
        self._minValue = NumberUtils.NaN
        self._maxValue = NumberUtils.NaN
        self._mean = NumberUtils.NaN
        self._categorized = False
        self._histogram = []
        self._categories = []

    @property
    def nodataProportion(self):
        return self._nodataProportion

    @nodataProportion.setter
    def nodataProportion(self, nodataProportion):
        self._nodataProportion = nodataProportion

    @property
    def minValue(self):
        return self._minValue

    @minValue.setter
    def minValue(self, minValue):
        self._minValue = minValue

    @property
    def maxValue(self):
        return self._maxValue

    @maxValue.setter
    def maxValue(self, maxValue):
        self._maxValue = maxValue

    @property
    def categorized(self):
        return self._categorized

    @categorized.setter
    def categorized(self, categorized):
        self._categorized = categorized

    @property
    def histogram(self):
        return self._histogram

    @histogram.setter
    def histogram(self, histogram):
        self._histogram = histogram

    @property
    def categories(self):
        return self._categories

    @categories.setter
    def categories(self, categories):
        self._categories = categories

    @property
    def mean(self):
        return self._mean

    @mean.setter
    def mean(self, mean):
        self._mean = mean


class ObservationReference():

    def __init__(self) -> None:
        self._shapeType = ShapeType.EMPTY
        self._encodedShape = None
        self._spatialProjection = None
        self._id = None
        self._rootContextId = None
        self._label = None
        self._observable = None
        self._exportLabel = None
        self._valueType = None
        self._observationType = None
        self._semantics = set()
        self._geometryTypes = set()
        self._literalValue = None
        self._overallValue = None
        self._traits = []
        self._metadata = {}
        self._taskId = None
        self._contextId = None
        self._empty = False
        self._style = None
        self._primary = False
        self._dataSummary = None
        self._exportFormats = []
        self._originalGroupId = None
        self._alive = False
        self._main = False
        self._dynamic = False
        self._timeEvents = []

        # TODO
        # Histogram histogram
        # Colormap colormap;
        # ScaleReference scaleReference;
        # private List<ObservationReference> children = new ArrayList<>();
        # private List<ActionReference> actions = new ArrayList<>();
        # private List<Connection> structure = new ArrayList<>();

        self._childIds = {}
        self._childrenCount = 0
        self._roles = []
        self._observableType = None
        self._parentId = None
        self._parentArtifactId = None
        self._contextTime = -1
        self._creationTime = 0
        self._urn = None
        self._valueCount = 0
        self._previouslyNotified = False
        self._contextualized = False
        self._lastUpdate = 0
        self._key = None

    @property
    def shapeType(self) -> ShapeType:
        return self._shapeType

    @shapeType.setter
    def shapeType(self, shapeType):
        self._shapeType = shapeType

    @property
    def encodedShape(self) -> str:
        return self._encodedShape

    @encodedShape.setter
    def encodedShape(self, encodedShape):
        self._encodedShape = encodedShape

    @property
    def spatialProjection(self) -> str:
        return self._spatialProjection

    @spatialProjection.setter
    def spatialProjection(self, spatialProjection):
        self._spatialProjection = spatialProjection

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def rootContextId(self) -> str:
        return self._rootContextId

    @rootContextId.setter
    def rootContextId(self, rootContextId):
        self._rootContextId = rootContextId

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, label):
        self._label = label

    @property
    def observable(self) -> str:
        return self._observable

    @observable.setter
    def observable(self, observable):
        self._observable = observable

    @property
    def exportLabel(self) -> str:
        return self._exportLabel

    @exportLabel.setter
    def exportLabel(self, exportLabel):
        self._exportLabel = exportLabel

    @property
    def valueType(self) -> ValueType:
        return self._valueType

    @valueType.setter
    def valueType(self, valueType):
        self._valueType = valueType

    @property
    def observationType(self) -> ObservationType:
        return self._observationType

    @observationType.setter
    def observationType(self, observationType):
        self._observationType = observationType

    @property
    def semantics(self) -> KimConceptType:
        return self._semantics

    @semantics.setter
    def semantics(self, semantics):
        self._semantics = semantics

    @property
    def geometryTypes(self) -> GeometryType:
        return self._geometryTypes

    @geometryTypes.setter
    def geometryTypes(self, geometryTypes):
        self._geometryTypes = geometryTypes

    @property
    def literalValue(self) -> str:
        return self._literalValue

    @literalValue.setter
    def literalValue(self, literalValue):
        self._literalValue = literalValue

    @property
    def overallValue(self) -> str:
        return self._overallValue

    @overallValue.setter
    def overallValue(self, overallValue):
        self._overallValue = overallValue

    @property
    def traits(self) -> list:
        return self._traits

    @traits.setter
    def traits(self, traits):
        self._traits = traits

    @property
    def metadata(self) -> dict:
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        self._metadata = metadata

    @property
    def taskId(self) -> str:
        return self._taskId

    @taskId.setter
    def taskId(self, taskId):
        self._taskId = taskId

    @property
    def contextId(self) -> str:
        return self._contextId

    @contextId.setter
    def contextId(self, contextId):
        self._contextId = contextId

    @property
    def empty(self) -> bool:
        return self._empty

    @empty.setter
    def empty(self, empty):
        self._empty = empty

    @property
    def style(self) -> str:
        return self._style

    @style.setter
    def style(self, style):
        self._style = style

    @property
    def primary(self) -> bool:
        return self._primary

    @primary.setter
    def primary(self, primary):
        self._primary = primary

    @property
    def dataSummary(self) -> DataSummary:
        return self._dataSummary

    @dataSummary.setter
    def dataSummary(self, dataSummary):
        self._dataSummary = dataSummary

    @property
    def exportFormats(self) -> list:
        return self._exportFormats

    @exportFormats.setter
    def exportFormats(self, exportFormats):
        self._exportFormats = exportFormats

    @property
    def originalGroupId(self) -> str:
        return self._originalGroupId

    @originalGroupId.setter
    def originalGroupId(self, originalGroupId):
        self._originalGroupId = originalGroupId

    @property
    def alive(self) -> bool:
        return self._alive

    @alive.setter
    def alive(self, alive):
        self._alive = alive

    @property
    def main(self) -> bool:
        return self._main

    @main.setter
    def main(self, main):
        self._main = main

    @property
    def dynamic(self) -> bool:
        return self._dynamic

    @dynamic.setter
    def dynamic(self, dynamic):
        self._dynamic = dynamic

    @property
    def timeEvents(self) -> list:
        return self._timeEvents

    @timeEvents.setter
    def timeEvents(self, timeEvents):
        self._timeEvents = timeEvents

    @property
    def childIds(self) -> dict:
        return self._childIds

    @childIds.setter
    def childIds(self, childIds):
        self._childIds = childIds

    @property
    def childrenCount(self) -> int:
        return self._childrenCount

    @childrenCount.setter
    def childrenCount(self, childrenCount):
        self._childrenCount = childrenCount

    @property
    def roles(self) -> list:
        return self._roles

    @roles.setter
    def roles(self, roles):
        self._roles = roles

    @property
    def observableType(self) -> KimConceptType:
        return self._observableType

    @observableType.setter
    def observableType(self, observableType):
        self._observableType = observableType

    @property
    def parentId(self) -> str:
        return self._parentId

    @parentId.setter
    def parentId(self, parentId):
        self._parentId = parentId

    @property
    def parentArtifactId(self) -> str:
        return self._parentArtifactId

    @parentArtifactId.setter
    def parentArtifactId(self, parentArtifactId):
        self._parentArtifactId = parentArtifactId

    @property
    def contextTime(self) -> int:
        return self._contextTime

    @contextTime.setter
    def contextTime(self, contextTime):
        self._contextTime = contextTime

    @property
    def creationTime(self) -> int:
        return self._creationTime

    @creationTime.setter
    def creationTime(self, creationTime):
        self._creationTime = creationTime

    @property
    def urn(self) -> str:
        return self._urn

    @urn.setter
    def urn(self, urn):
        self._urn = urn

    @property
    def valueCount(self) -> int:
        return self._valueCount

    @valueCount.setter
    def valueCount(self, valueCount):
        self._valueCount = valueCount

    @property
    def previouslyNotified(self) -> bool:
        return self._previouslyNotified

    @previouslyNotified.setter
    def previouslyNotified(self, previouslyNotified):
        self._previouslyNotified = previouslyNotified

    @property
    def contextualized(self) -> bool:
        return self._contextualized

    @contextualized.setter
    def contextualized(self, contextualized):
        self._contextualized = contextualized

    @property
    def lastUpdate(self) -> int:
        return self._lastUpdate

    @lastUpdate.setter
    def lastUpdate(self, lastUpdate):
        self._lastUpdate = lastUpdate

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, key):
        self._key = key


class ObservationImpl():

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

    # @Override
    # public boolean export(Export target, ExportFormat format, File file, Object... parameters) {
    #     boolean ret = false;
    #     try (OutputStream stream = new FileOutputStream(file)) {
    #         ret = export(target, format, stream, parameters);
    #     } catch (FileNotFoundException e) {
    #         throw new KlabIllegalStateException(e.getMessage());
    #     } catch (IOException e) {
    #         throw new KlabIOException(e.getMessage());
    #     }
    #     return ret;
    # }

    # @Override
    # public String export(Export target, ExportFormat format) {
    #     if (!format.isText()) {
    #         throw new KlabIllegalArgumentException(
    #                 "illegal export format " + format + " for string export of " + target);
    #     }
    #     try (ByteArrayOutputStream output = new ByteArrayOutputStream()) {
    #         boolean ok = export(target, format, output);
    #         if (ok) {
    #             return new String(output.toByteArray(), StandardCharsets.UTF_8);
    #         }
    #     } catch (IOException e) {
    #         // just return null
    #     }
    #     return null;
    # }

    def export(self, target: Export,  format: ExportFormat,  output,  parameters: list) -> bool:
        if not format.isExportAllowed(target):
            raise KlabIllegalArgumentException(
                "export format is incompatible with target")

        return self.engine.streamExport(self.reference.id, target, format, output, parameters)

    def getObservation(self, name: str):
        id = self.catalogIds.get(name)
        if id:
            ret = self.catalog.get(id)
            if not ret:
                ref = self.engine.getObservation(id)
                if ref and ref.id:
                    ret = ObservationImpl(ref, self.engine)
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

        return Range.create(self.reference.dataSummary.minValue,
                            self.reference.dataSummary.maxValue)

    def getScalarValue(self):
        literalValue = self.reference.overallValue
        if literalValue:
            match self.reference.valueType:
                case ValueType.BOOLEAN:
                    return bool(literalValue)
                case ValueType.NUMBER:
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
        
    def __init__(self, urn:str = None, contextId:str = None, contextSearchId:str = None) -> None:
        self._urn = urn
        self._contextId = contextId
        self._searchContextId = contextSearchId
        self._estimate = False
        self._estimatedCost = -1
        self._scenarios = []
        self._states = {}
        self._objects = {}
            
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
        ret = """{{"geometry":"{0}","contextType":"{1}","observables":{2},"scenarios":{3},"estimate":{4},"estimatedCost":{5}}}"""
        ret = ret.format(self._geometry, self._contextType, self._observables, self._scenarios, es, self._estimatedCost)
        return ret #.encode('utf-8')


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



class ContextImpl(ObservationImpl):

    def __init__(self, reference: ObservationReference, engine):
        super().__init__(reference, engine)

        # if defined, these are submitted at the next submit() before the main
        # observable is queried, then cleared.
        self.injectedStates = [] #supposed to be (Observable, Object)
        self.injectedObjects = [] # supposed to be (Observable, IGeometry)


    
    async def estimate(self, observable:Observable, arguments:list) -> Estimate:
        request = ObservationRequest()
        request.contextId =self.reference.id
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
            return E.TicketHandler<Estimate>(self.engine, ticket, self)
        
        raise KlabIllegalArgumentException(
                f"Cannot build estimate request from arguments: {arguments}" )
    

    async def submit(self, observable:Observable, arguments:list) -> ObservationImpl:

        request = ObservationRequest()
        request.contextId =self.reference.id
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
            return E.TicketHandler<Estimate>(self.engine, ticket, self)

        raise KlabIllegalArgumentException(
            f"Cannot build observation request from arguments: {arguments}" )

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

    # @Override
    # public String getDataflow(ExportFormat format) {

    #     if (format != ExportFormat.ELK_GRAPH_JSON && format != ExportFormat.KDL_CODE) {
    #         throw new KlabIllegalArgumentException("cannot export a dataflow to " + format);
    #     }

    #     try (ByteArrayOutputStream output = new ByteArrayOutputStream()) {
    #         if (engine.streamExport(reference.getId(), Export.DATAFLOW, format, output)) {
    #             return output.toString();
    #         }
    #     } catch (IOException e) {
    #         throw new KlabIOException(e);
    #     }

    #     return null;
    # }

    # @Override
    # public String getProvenance(boolean simplified, ExportFormat format) {

    #     if (format != ExportFormat.ELK_GRAPH_JSON && format != ExportFormat.KIM_CODE) {
    #         throw new KlabIllegalArgumentException("cannot export the provenance graph to " + format);
    #     }

    #     try (ByteArrayOutputStream output = new ByteArrayOutputStream()) {
    #         if (engine.streamExport(reference.getId(),
    #                 simplified ? Export.PROVENANCE_SIMPLIFIED : Export.PROVENANCE_FULL, format, output)) {
    #             return output.toString();
    #         }
    #     } catch (IOException e) {
    #         throw new KlabIOException(e);
    #     }

    #     return null;
    # }

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

    # /*
    #     * Called after an observation to update the context data and ensure the context
    #     * has the new observation in its catalog.
    #     * 
    #     * @Non-API should be package private
    #     * 
    #     * @param ret
    #     */
    def updateWith(self, ret:ObservationImpl):
        pass
    #     this.reference = engine.getObservation(reference.getId());
    #     for (String name : this.reference.getChildIds().keySet()) {
    #         if (ret.reference.getId().equals(this.reference.getChildIds().get(name))) {
    #             catalogIds.put(name, ret.reference.getId());
    #             catalog.put(ret.reference.getId(), ret);
    #             break;
    #         }
    #     }

    # }


