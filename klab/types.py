from .exceptions import KlabIllegalArgumentException
from enum import Enum

class Granularity(Enum):
        SINGLE = "SINGLE"
        MULTIPLE = "MULTIPLE"

class DimensionType(Enum):
        NUMEROSITY = "NUMEROSITY"
        TIME = "TIME"
        SPACE = "SPACE"

class ShapeType(Enum):
    EMPTY="EMPTY" 
    POINT="POINT" 
    LINESTRING="LINESTRING" 
    POLYGON="POLYGON" 
    MULTIPOINT="MULTIPOINT" 
    MULTILINESTRING="MULTILINESTRING" 
    MULTIPOLYGON="MULTIPOLYGON"	

    @staticmethod
    def fromValue(value:str):
        if not value:
            return None
        for st in ShapeType:
            if st.value.lower() == value.lower():
                return st
        raise KlabIllegalArgumentException(f"No ShapeType available by the value: {value}")


class ObservationType(Enum):
    PROCESS = "PROCESS"
    STATE = "STATE"
    SUBJECT = "SUBJECT"
    CONFIGURATION = "CONFIGURATION"
    EVENT = "EVENT"
    RELATIONSHIP = "RELATIONSHIP"
    GROUP = "GROUP"
    VIEW = "VIEW"

    @staticmethod
    def fromValue(value: str):
        if not value:
            return None
        for ot in ObservationType:
            if ot.value.lower() == value.lower():
                return ot
        raise KlabIllegalArgumentException(
            f"No ObservationType available by the value: {value}")


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

    @staticmethod
    def fromValue(value:str):
        if not value:
            return None
        for kct in KimConceptType:
            if kct.value.lower() == value.lower():
                return kct
        raise KlabIllegalArgumentException(f"No KimConceptType available by the value: {value}")

    @staticmethod
    def fromListToSet(value:list):
        kcts = set()
        for v in value:
            kct = KimConceptType.fromValue(v)
            if kct:
                kcts.add(kct)
        return kcts


class ValueType(Enum):
    """
    The value of this enum defines the type of values this observation contains.
        All non-quality observations have value type VOID.
    """
    VOID = "VOID"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    CATEGORY = "CATEGORY"

    @staticmethod
    def fromValue(value: str):
        if not value:
            return None
        for vt in ValueType:
            if vt.value.lower() == value.lower():
                return vt
        raise KlabIllegalArgumentException(
            f"No ValueType available by the value: {value}")


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

    @staticmethod
    def fromValue(value:str):
        if not value:
            return None
        for gt in GeometryType:
            if gt.value.lower() == value.lower():
                return gt
        raise KlabIllegalArgumentException(f"No GeometryType available by the value: {value}")

    @staticmethod
    def fromListToSet(value:list):
        gts = set()
        for v in value:
            gt = GeometryType.fromValue(v)
            if gt:
                gts.add(gt)
        return gts

class TimeResolutionType(Enum):
    MILLENNIUM=0
    CENTURY=1
    DECADE=2
    YEAR=3
    MONTH=4
    WEEK=5
    DAY=6
    HOUR=7
    MINUTE=8
    SECOND=9
    MILLISECOND=10

    @staticmethod
    def fromValue(value:int):
        if not value:
            return None
        for trt in TimeResolutionType:
            if trt.value == value:
                return trt
        raise KlabIllegalArgumentException(f"No TimeResolutionType available by the value: {value}")
