from .types import KimConceptType, ShapeType, ValueType, ObservationType, GeometryType, TimeResolutionType
from .utils import NumberUtils, ExportFormat

class ActionReference():
    """
    Describes a possible action to be performed on an observation. The engine
    sends all possible actions with each new observation and handles
    ActionRequest with action reference ID.
    
    Actions may be regular ones (with the ID to communicate to the back end along
    with the observation ID), separators (which do nothing except cause a
    separator to be put in the menu) and downloads (which have a null actionId
    but a non-null downloadUrl and downloadFileExtension, which should be handled
    by the front end to produce a file download).
    
    Actions may also have sub-actions, in which case they correspond to
    sub-menus.
    """

    def __init__(self, label:str = None, id:str = None) -> None:
        self._actionLabel = label
        self._actionId = id
        self._downloadUrl = None
        self._downloadFileExtension = None
        self._enabled = True
        self._separator = False
        self._submenu = []

    @staticmethod
    def fromDict(dataMap:dict):
        ar = ActionReference()
        ar._actionLabel = dataMap.get('actionLabel')
        ar._actionId = dataMap.get('actionId')
        ar._downloadUrl = dataMap.get('downloadUrl')
        ar._downloadFileExtension = dataMap.get('downloadFileExtension')
        ar._enabled = dataMap.get('enabled')
        ar._separator = dataMap.get('separator')
        ar._submenu = dataMap.get('submenu')
        return ar
    
    @staticmethod
    def fromList(dataList:list):
        return [ ActionReference.fromDict(obj) for obj in dataList ]


class ScaleReference():
    """
    Used to communicate spatio/temporal regions of interest. Space values should
    be in decimal latitude and longitude.

    Sent from back-end to communicate new resolution when extent is changed on
    the front end. Sent by front-end when user wants to set resolution, which
    locks the scale to the user choice. A front-end message with just unlockSpace
    == true resets the behavior to automatic resolution definition.
    """

    def __init__(self) -> None:
        self._name = None
        self._east = 0.0
        self._west = 0.0
        self._north = 0.0
        self._south = 0.0
        self._spaceScale = 0
        self._timeScale = 0
        self._spaceResolution = 0.0
        self._spaceResolutionDescription = None
        self._spaceResolutionConverted = 0.0
        self._spaceUnit = None
        self._timeResolutionMultiplier = 0.0
        self._timeUnit = None
        self._timeResolutionDescription = None
        self._shape = None
        self._timeType = None
        self._timeGeometry = None
        self._spaceGeometry = None
        self._start = 0
        self._end = 0
        self._step = 0
        self._spaceExtension = set()
        self._spaceEnumerated = False
        self._contextId = None
        self._featureUrn = None
        self._metadata = {}
        # // FIXME REMOVE
        # private String resolutionDescription;
        # private int year = -1;

    @staticmethod
    def fromDict(dataMap:dict):
        sr = ScaleReference()
        sr._name = dataMap.get('name')
        sr._east = dataMap.get('east')
        sr._west = dataMap.get('west')
        sr._north = dataMap.get('north')
        sr._south = dataMap.get('south')
        sr._spaceScale = dataMap.get('spaceScale')
        sr._timeScale = dataMap.get('timeScale')
        sr._spaceResolution = dataMap.get('spaceResolution')
        sr._spaceResolutionDescription = dataMap.get('spaceResolutionDescription')
        sr._spaceResolutionConverted = dataMap.get('spaceResolutionConverted')
        sr._spaceUnit = dataMap.get('spaceUnit')
        sr._timeResolutionMultiplier = dataMap.get('timeResolutionMultiplier')
        sr._timeUnit = TimeResolutionType.fromValue(dataMap.get('timeUnit'))
        sr._timeResolutionDescription = dataMap.get('timeResolutionDescription')
        sr._shape = dataMap.get('shape')
        sr._timeType = dataMap.get('timeType')
        sr._timeGeometry = dataMap.get('timeGeometry')
        sr._spaceGeometry = dataMap.get('spaceGeometry')
        sr._start = dataMap.get('start')
        sr._end = dataMap.get('end')
        sr._step = dataMap.get('step')
        sr._spaceExtension = dataMap.get('spaceExtension')
        sr._spaceEnumerated = dataMap.get('spaceEnumerated')
        sr._contextId = dataMap.get('contextId')
        sr._featureUrn = dataMap.get('featureUrn')
        sr._metadata = dataMap.get('metadata')
        return sr



    # TODO add properties

    def __str__(self) -> str:
        return f"ScaleReference [east={self.east}, west={self.west}, north={self.north}, south={self.south}, spaceScale={self.spaceScale}, resolutionDescription={self.spaceResolutionDescription}]"


class DataSummary():

    def __init__(self) -> None:
        self._nodataProportion = 0.0
        self._minValue = NumberUtils.NaN
        self._maxValue = NumberUtils.NaN
        self._mean = NumberUtils.NaN
        self._categorized = False
        self._histogram = []
        self._categories = []

    @staticmethod
    def fromDict(dataMap:dict):
        ds = DataSummary()
        ds._nodataProportion = dataMap.get('nodataProportion')
        ds._minValue = dataMap.get('minValue')
        ds._maxValue = dataMap.get('maxValue')
        ds._mean = dataMap.get('mean')
        ds._categorized = dataMap.get('categorized')
        ds._histogram = dataMap.get('histogram')
        ds._categories = dataMap.get('categories')
        return ds

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
        self._scaleReference = None
        self._actions = []
        # TODO
        # Histogram histogram
        # Colormap colormap;
        # private List<ObservationReference> children = new ArrayList<>();
        # private List<Connection> structure = new ArrayList<>();

    @staticmethod
    def fromDict(dataMap: dict):
        obr = ObservationReference()
        obr._shapeType = ShapeType.fromValue(
            dataMap.get('shapeType'))  # ShapeType.EMPTY
        obr._encodedShape = dataMap.get('encodedShape')  # None
        obr._spatialProjection = dataMap.get('spatialProjection')  # None
        obr._id = dataMap.get('id')  # None
        obr._rootContextId = dataMap.get('rootContextId')  # None
        obr._label = dataMap.get('label')  # None
        obr._observable = dataMap.get('observable')  # None
        obr._exportLabel = dataMap.get('exportLabel')  # None
        obr._valueType = ValueType.fromValue(dataMap.get('valueType'))  # None
        obr._observationType = ObservationType.fromValue(dataMap.get('observationType'))  # None
        obr._semantics = KimConceptType.fromListToSet(dataMap.get('semantics'))  # set()
        obr._geometryTypes = GeometryType.fromListToSet(dataMap.get('geometryTypes'))  # set()
        obr._literalValue = dataMap.get('literalValue')  # None
        obr._overallValue = dataMap.get('overallValue')  # None
        obr._traits = dataMap.get('traits')  # []
        obr._metadata = dataMap.get('metadata')  # {}
        obr._taskId = dataMap.get('taskId')  # None
        obr._contextId = dataMap.get('contextId')  # None
        obr._empty = dataMap.get('empty')  # False
        obr._style = dataMap.get('style')  # None
        obr._primary = dataMap.get('primary')  # False
        obr._dataSummary = dataMap.get('dataSummary')  # None
        obr._exportFormats = ExportFormat.fromMediaTypeList(dataMap.get('exportFormats'))  # []
        obr._originalGroupId = dataMap.get('originalGroupId')  # None
        obr._alive = dataMap.get('alive')  # False
        obr._main = dataMap.get('main')  # False
        obr._dynamic = dataMap.get('dynamic')  # False
        obr._timeEvents = dataMap.get('timeEvents')  # []
        obr._childIds = dataMap.get('childIds')  # {}
        obr._childrenCount = dataMap.get('childrenCount')  # 0
        obr._roles = dataMap.get('roles')  # []
        obr._observableType = dataMap.get('observableType')  # None
        obr._parentId = dataMap.get('parentId')  # None
        obr._parentArtifactId = dataMap.get('parentArtifactId')  # None
        obr._contextTime = dataMap.get('contextTime')  # -1
        obr._creationTime = dataMap.get('creationTime')  # 0
        obr._urn = dataMap.get('urn')  # None
        obr._valueCount = dataMap.get('valueCount')  # 0
        obr._previouslyNotified = dataMap.get('previouslyNotified')  # False
        obr._contextualized = dataMap.get('contextualized')  # False
        obr._lastUpdate = dataMap.get('lastUpdate')  # 0
        obr._key = dataMap.get('key')  # None
        obr._scaleReference = ScaleReference.fromDict(dataMap.get('scaleReference') ) # None
        obr._actions = ActionReference.fromList(dataMap.get('actions') ) # None

        return obr

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
    def semantics(self) -> set:
        return self._semantics

    @semantics.setter
    def semantics(self, semantics):
        self._semantics = semantics

    @property
    def geometryTypes(self) -> set:
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

    @property
    def scaleReference(self) -> str:
        return self._scaleReference

    @scaleReference.setter
    def scaleReference(self, scaleReference):
        self._scaleReference = scaleReference

    @property
    def actions(self) -> str:
        return self._actions

    @actions.setter
    def actions(self, actions):
        self._actions = actions

