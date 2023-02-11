from enum import Enum
from .exceptions import KlabIllegalArgumentException
import sys
from .utils import NumberUtils
from .types import Granularity, Type, TimeResolutionType, DimensionType
import functools



NONDIMENSIONAL = -1
"""Constant for non-dimensional (referenced but not distributed) return value of Dimension#getDimensionality()."""

UNDEFINED = -1
"""Constant for undefined dimension size."""

INFINITE_SIZE = sys.maxsize
"""Infinite size, only admitted for the time dimension."""

PARAMETER_SPACE_SHAPE = "shape"
"""Shape specs in WKB."""

PARAMETER_SPACE_BOUNDINGBOX = "bbox"
"""Bounding box as a [minX, maxX, minY, maxY]"""

PARAMETER_SPACE_LONLAT = "latlon"
"""Latitude,longitude as a [lon, lat]"""

PARAMETER_ENUMERATED_AUTHORITY = "authority"
"""Authority specifier for generic enumerated extent (may be D or S)"""

PARAMETER_ENUMERATED_BASE_IDENTITY = "baseidentity"
"""Base identity specifier for generic enumerated extent (may be D or S)"""

PARAMETER_ENUMERATED_IDENTIFIER = "identifier"
"""Concrete identity for enumerated extent (D or S)"""

PARAMETER_SPACE_PROJECTION = "proj"
PARAMETER_SPACE_GRIDRESOLUTION = "sgrid"
"""Grid resolution as a string 'n unit'"""

PARAMETER_SPACE_SHAPE = "shape"
"""Shape specs in WKB"""

PARAMETER_SPACE_RESOURCE_URN = "urn"
"""Resource URN to retrieve the space extent"""

PARAMETER_TIME_PERIOD = "period"
"""Time period as a [startMillis, endMillis]"""

PARAMETER_TIME_GRIDRESOLUTION = "tgrid"
"""time period as a long"""

PARAMETER_TIME_START = "tstart"
"""time period as a long"""

PARAMETER_TIME_END = "tend"
"""time period as a long"""

PARAMETER_TIME_REPRESENTATION = "ttype"
"""Time representation: one of generic, specific, grid or real."""

PARAMETER_TIME_TRANSITIONS = "transitions"
"""Irregular grid transition points, start to end."""

PARAMETER_TIME_SCOPE = "tscope"
"""Time scope: integer or floating point number of PARAMETER_TIME_SCOPE_UNITs."""

PARAMETER_TIME_LOCATOR = "time"
"""Specific time location, for locator geometries. Expects a long, a date or a ITimeInstant."""

PARAMETER_TIME_SCOPE_UNIT = "tunit"

PARAMETER_TIME_COVERAGE_UNIT = "coverageunit"

PARAMETER_TIME_COVERAGE_START = "coveragestart"

PARAMETER_TIME_COVERAGE_END = "coverageend"


def compareDimensions(item1, item2):
    if item1.getType() == Type.TIME:
        return -1
    else:
        return 0

class DimensionImpl():
    def __init__(self) -> None:
         self.regular = False
         self.dimensionality = 0
         self.generic = False
         self.coverage = 1.0
         self.parameters = {}
         self._shape = None
         self.type = None

    
    def getType(self) -> Type:
        return self.type

    def copy(self):
        ret =  DimensionImpl()
        ret.type = self.type
        ret.regular = self.regular
        ret.dimensionality = self.dimensionality
        if self._shape:
            ret._shape = self._shape[:]
        ret.parameters = dict(self.parameters)
        ret.generic = self.generic
        return ret;

    def isRegular(self) -> bool:
        return self.regular

    def isGeneric(self) -> bool:
        return self.generic
    
    def getDimensionality(self)-> int:
        return self.dimensionality

    def getCoverage(self)-> float:
        return self.coverage
    
    def size(self):
        if self._shape:
            self.product(self._shape)
        else:
            return UNDEFINED

    def product(self, shape2):
        ret = 1
        for l in self._shape:
            ret *= l
        return ret

    def shape(self) -> list:
        if not self._shape:
            return [UNDEFINED]*self.dimensionality
        return self._shape
    

    # @Override
    # public String encode(Encoding... options) {
    #     return encodeDimension(this);
    # }

    # // @Override
    # public long getOffset(long... offsets) {

    #     if (offsets == null) {
    #         return 0;
    #     }
    #     if (offsets.length != dimensionality) {
    #         throw new KlabIllegalArgumentException("geometry: cannot address a " + dimensionality
    #                 + "-dimensional extent with an offset array of lenght " + offsets.length);
    #     }
    #     if (_shape == null) {
    #         throw new KlabIllegalArgumentException("geometry: cannot address a geometry with no _shape");
    #     }

    #     if (offsets.length == 1) {
    #         return offsets[0];
    #     }

    #     if (this.type == Type.SPACE && offsets.length == 2) {

    #         /*
    #             * TODO this is arbitrary and repeats the addressing in Grid. I just can't go
    #             * over the entire codebase to just use this one at this moment. Should have a
    #             * centralized offsetting strategy and use that everywhere, configuring it
    #             * according to and extent types.
    #             */
    #         return ((_shape[1] - offsets[1] - 1) * _shape[0]) + offsets[0];
    #     }

    #     return 0;
    # }

    # // @Override
    # // public long getOffset(ILocator index) {
    # // throw new IllegalArgumentException("getOffset() is not implemented on basic
    # // geometry
    # // dimensions");
    # // }

    def getParameters(self) -> dict:
        return self.parameters
    

    # public long[] get_shape() {
    #     return _shape;
    # }

    # public void set_shape(long[] _shape) {
    #     this._shape = _shape;
    # }

    # public void setType(Type type) {
    #     this.type = type;
    # }

    # public void setRegular(boolean regular) {
    #     this.regular = regular;
    # }

    # public void setDimensionality(int dimensionality) {
    #     this.dimensionality = dimensionality;
    # }

    # public void setGeneric(boolean generic) {
    #     this.generic = generic;
    # }

    # public boolean isCompatible(Dimension dimension) {

    #     if (type != dimension.getType()) {
    #         return false;
    #     }

    #     if ((generic && !dimension.isGeneric()) /* || (!generic && dimension.isGeneric()) */) {
    #         return false;
    #     }

    #     // TODO must enable a boundary _shape to cut any geometry, regular or not, as
    #     // long
    #     // as the dimensionality agrees

    #     // if (regular && !(dimension.isRegular() || dimension.size() == 1)
    #     // || !regular && (dimension.isRegular() || dimension.size() == 1)) {
    #     // return false;
    #     // }

    #     return true;
    # }

    # @Override
    # public ExtentDimension getExtentDimension() {
    #     switch (this.type) {
    #     case NUMEROSITY:
    #         return ExtentDimension.CONCEPTUAL;
    #     case SPACE:
    #         return ExtentDimension.spatial(this.dimensionality);
    #     case TIME:
    #         return ExtentDimension.TEMPORAL;
    #     default:
    #         break;
    #     }
    #     return null;
    # }

    # @Override
    # public boolean isDistributed() {
    #     return size() > 1 || isRegular()
    #             || (this.type == Type.TIME && "GRID".equals(parameters.get(PARAMETER_TIME_REPRESENTATION)));
    # }

	


class KlabGeometry():
    def __init__(self) -> None:
        self._scalar = False
        self.granularity = Granularity.SINGLE
        self.dimensions = []
        self.child = None

    def isEmpty(self)->bool:
        return not self.scalar and len(self.dimensions)==0 and self.child == None
	
    def isScalar(self)->bool:
        return self._scalar

    @staticmethod
    def create(geometrySpec:str):
        return KlabGeometry.makeGeometry(geometrySpec, 0)

    @staticmethod
    def empty():
        return KlabGeometry()
    
    @staticmethod
    def scalar():
        ret = KlabGeometry()
        ret._scalar = True
        return ret
    
    def newDimension(self) -> DimensionImpl:
        return DimensionImpl()
    
    def addDimension(self, dim:DimensionImpl):
        self.dimensions.append(dim)
	
    @staticmethod
    def makeGeometry(geometry:str, i:int):
        """
        read the geometry defined starting at the i-th character
        """

        ret = KlabGeometry();

        if geometry == None or geometry == "X":
            return KlabGeometry.empty()

        if geometry == "*":
            return KlabGeometry._scalar();
        
        idx = i
        while idx < len(geometry):
            c = geometry[idx]
            if c == '#':
                ret.granularity = Granularity.MULTIPLE
            elif (c >= 'A' and c <= 'z') or c == '\u03C3' or c == '\u03C4' or c == '\u03A3' or c == '\u03A4':
                dimensionality = ret.newDimension()
                if c == 'S' or c == 's' or c == '\u03C3' or c == '\u03A3':
                    dimensionality.type = Type.SPACE
                    if c == '\u03C3' or c == '\u03A3':
                        dimensionality.generic = True
                    dimensionality.regular = c == 'S' or c == '\u03A3'

                elif c == 'T' or c == 't' or c == '\u03C4' or c == '\u03A4':
                    dimensionality.type = Type.TIME
                    if c == '\u03C4' or c == '\u03A4':
                        dimensionality.generic = True
                    dimensionality.regular = c == 'T' or c == '\u03A4'

                else:
                    raise KlabIllegalArgumentException(f"unrecognized geometry dimension identifier {c}");

                idx += 1
                if geometry[idx] == '.':
                    dimensionality.dimensionality = NONDIMENSIONAL
                else:
                    dimensionality.dimensionality = int(geometry[idx]);
                

                if len(geometry) > (idx + 1) and geometry[idx + 1] == '(':
                    idx += 2;
                    shape = ""
                    while geometry[idx] != ')':
                        shape += geometry[idx]
                        idx+=1
                    
                    dims = shape.strip().split(",")
                    sdimss = []
                    for d in range(0, len(dims)):
                        dimspec = dims[d].strip()
                        dsize = NONDIMENSIONAL
                        if len(dimspec)>0:
                            if dimspec == "\u221E":
                                dsize =  INFINITE_SIZE 
                            else: 
                                dsize = int(dimspec)
                        
                        sdimss.append(dsize)
                    
                    dimensionality.dimensionality = len(sdimss)
                    dimensionality.shape = sdimss
                
                if len(geometry) > (idx + 1) and geometry[idx + 1] == '{':
                    idx += 2
                    shape = ""
                    while geometry[idx] != '}':
                        shape += geometry[idx]
                        idx+=1
                    
                    if len(shape)>0:
                        dimensionality.parameters.update(KlabGeometry.readParameters(shape))

                ret.dimensions.append(dimensionality)
                idx += 1

            elif c == ',':
                ret.child = KlabGeometry.makeGeometry(geometry, idx + 1)
                break;
            
        return ret
        
    @staticmethod
    def readParameters(kvs:str) -> dict:
        ret = {}
        kvpList = kvs.strip().split(",")
        for kvp in kvpList:
            kk = kvp.strip().split("=")
            if len(kk) != 2:
                raise KlabIllegalArgumentException(f"wrong key/value pair in geometry definition: {kvp}")
            
            key = kk[0].strip()
            val = kk[1].strip()
            val = KlabGeometry.decodeForSerialization(val);
            v = None
            if val.startswith("[") and val.endswith("]"):
                v = NumberUtils.podArrayFromString(val, r"\s+", None) #getParameterPODType(key));
            elif PARAMETER_SPACE_SHAPE != key and NumberUtils.encodesInt(val):
                v = int(val)
            elif PARAMETER_SPACE_SHAPE != key and NumberUtils.encodesFloat(val):
                v = float(val)
            else:
                v = val

            ret[key] = v

        return ret

    @staticmethod
    def decodeForSerialization(val:str):
        return val.replace("&comma;", ",").replace("&eq;", "=")
    
    @staticmethod
    def encodeForSerialization(val:str):
        return val.replace(",", "&comma;").replace("=", "&eq;")

    def encode(self) -> str:
        """
        Encode into a string representation. Keys in parameter maps are sorted so the
	    results can be compared for equality.
	    """

        if self.isEmpty():
            return "X"

        if self.isScalar():
            return "*"

        dims = self.dimensions[:]
        dims = sorted(dims, key=functools.cmp_to_key(compareDimensions))

        ret = ""
        if self.granularity == Granularity.MULTIPLE:
            ret = "#"

        for dim in dims:
            ret += self.encodeDimension(dim)
        
        if self.child:
            ret += "," + self.child.encode()
        
        return ret
    
    @staticmethod
    def encodeDimension(dim:DimensionImpl) -> str:
        ret = ""

        if dim.getType() == Type.SPACE:
            if dim.isGeneric():
                if dim.isRegular():
                    ret += "\u03a3"
                else: 
                    ret += "\u03c3"
            else: 
                if dim.isRegular():
                    ret += "S"
                else: 
                    ret += "s"
        elif dim.getType() == Type.TIME:
            if dim.isGeneric():
                if dim.isRegular():
                    ret += "\u03a4"
                else: 
                    ret += "\u03c4"
            else: 
                if dim.isRegular():
                    ret += "T"
                else: 
                    ret += "t"
        else:
            raise NotImplementedError()

        ret += str(dim.getDimensionality())
        
        if dim.shape and not KlabGeometry.isUndefined(dim.shape):
            ret += "("
            for i in range(0, len(dim.shape)):
                sep = ","
                if i == 0:
                    sep = ""
                size = str(dim.shape[i])
                if dim.shape[i] == INFINITE_SIZE:
                    size = "\u221E"
                ret += sep + size

            ret += ")"
        
        if len(dim.getParameters()) > 0:
            ret += "{"
            first = True

            keys =sorted( list(dim.getParameters().keys()))
            
            for key in keys:
                sep = ","
                if first:
                    sep = ""
                ret += sep + key + "=" + KlabGeometry.encodeVal(dim.getParameters().get(key))
                first = False
            
            ret += "}"
        
        return ret
    
    @staticmethod
    def encodeVal(val:any):
        ret = ""
        if  isinstance(val, list):
            ret = "[";
            for v in val:
                sp = " "
                if len(ret) == 1:
                    sp = ""
                ret += sp + str(v)
            ret += "]"
        else:
            ret = str(val)
        
        return ret
    

    @staticmethod
    def isUndefined(shape) -> bool:
        for l in shape:
            if l < 0:
                return True
        return False
	


    

class KlabSpace():

    @staticmethod
    def isWKT(urn:str):
        return ("POLYGON" in urn or "POINT" in urn or "LINESTRING" in urn) and "(" in urn and ")" in urn


class SpaceBuilder():
    def __init__(self, space:DimensionImpl) -> None:
        self.space = space

    def generic(self):
        self.space.generic = True
        return self
    
    def regular(self):
        self.space.regular = True
        return self
    
    def size(self, x:int, y:int):
        self.space.shape = [x,y]
        self.space.regular = True
        return self

    def sizeN(self, n:int):
        self.space.shape = [n]
        self.space.regular = False
        return self

    def boundingBox(self, x1:float, x2:float,  y1:float,  y2:float):
        self.space.parameters[PARAMETER_SPACE_BOUNDINGBOX] = [x1, x2, y1, y2]
        return self

    def shape(self, wktb:str):
        self.space.parameters[PARAMETER_SPACE_SHAPE] = KlabGeometry.encodeForSerialization(wktb)
        return self

    def urn(self, urn:str):
        self.space.parameters[PARAMETER_SPACE_RESOURCE_URN] = KlabGeometry.encodeForSerialization(urn)
        return self

    def resolution(self, gridResolution:str):
        self.space.parameters[PARAMETER_SPACE_GRIDRESOLUTION] = gridResolution
        return self

    def build(self) -> DimensionImpl:
        return self.space
    
class TimeBuilder():
    def __init__(self, time:DimensionImpl) -> None:
        self.time = time
    
    def generic(self):
        self.time.generic = True
        return self
    
    def regular(self):
        self.time.regular = True
        return self
    
    def covering(self, start:int, end:int):
        self.time.parameters[PARAMETER_TIME_COVERAGE_START] = start
        self.time.parameters[PARAMETER_TIME_COVERAGE_END] = end
        return self
    
    def start(self, start:int):
        self.time.parameters[PARAMETER_TIME_START] = start
        return self
    
    def end(self, end:int):
        self.time.parameters[PARAMETER_TIME_END] = end
        return self
    
    def resolution(self, resolution:TimeResolutionType, multiplier:float):
        self.time.parameters[PARAMETER_TIME_SCOPE] = multiplier
        self.time.parameters[PARAMETER_TIME_SCOPE_UNIT] = resolution.name.lower()
        return self

    def size(self, n:int):
        self.time.shape = [n]
        self.time.regular = False
        return self

    def build(self) -> DimensionImpl:
        return self.time
    

class GeometryBuilder():
    def __init__(self) -> None:
        self.space = None
        self.time = None

    #     /**
    #     * Create a spatial region from a resource URN (specifying a polygon). The
    #     * string may also specify a WKT polygon using the k.LAB conventions (preceded
    #     * by the EPSG: projection). The resulting
    #     *
    #     * @param urn
    #     * @param resolution a string in the format "1 km"
    #     * @return
    #     */
    def region(self, urn:str):
        if KlabSpace.isWKT(urn):
            return self.space().shape(urn).size(1).build()
        return self.space().urn(urn).size(1).build()
    

    # /**
    #     * Create a spatial polygon of multiplicity 1 from a lat/lon bounding box and a
    #     * resolution. The box is "straight" with the X axis specifying
    #     * <em>longitude</em>.
    #     *
    #     * @param resolution a string in the format "1 km"
    #     * @return
    #     */
    # public GeometryBuilder grid(double x1, double x2, double y1, double y2) {
    #     return space().regular().boundingBox(x1, x2, y1, y2).build();
    # }

    # /**
    #     * Create a spatial grid from a resource URN (specifying a polygon) and a
    #     * resolution. The string may also specify a WKT polygon using the k.LAB
    #     * conventions (preceded by the EPSG: projection).
    #     *
    #     * @param urn
    #     * @param resolution a string in the format "1 km"
    #     * @return
    #     */
    # public GeometryBuilder grid(String urn, String resolution) {
    #     if (ISpace.isWKT(urn)) {
    #         return space().regular().resolution(resolution).shape(urn).build();
    #     }
    #     return space().regular().resolution(resolution).urn(urn).build();
    # }

    # /**
    #     * Create a spatial grid from a lat/lon bounding box and a resolution. The box
    #     * is "straight" with the X axis specifying <em>longitude</em>.
    #     *
    #     * @param resolution a string in the format "1 km"
    #     * @return
    #     */
    # public GeometryBuilder grid(double x1, double x2, double y1, double y2, String resolution) {
    #     return space().regular().resolution(resolution).boundingBox(x1, x2, y1, y2).build();
    # }

    # /**
    #     * Create a temporal extent in years. If one year is passed, build a single-year
    #     * extent; otherwise build a yearly grid from the first year to the second.
    #     * 
    #     * @param years
    #     * @return
    #     */
    # public GeometryBuilder years(int... years) {
    #     if (years != null) {
    #         if (years.length == 1) {
    #             return time().start(startOfYear(years[0])).end(startOfYear(years[0] + 1)).size(1).build();
    #         } else if (years.length == 2) {
    #             return time().start(startOfYear(years[0])).end(startOfYear(years[1])).size((long) (years[1] - years[0]))
    #                     .resolution(ITime.Resolution.Type.YEAR, 1).build();
    #         }
    #         // TODO irregular coverage?
    #     }
    #     throw new KlabIllegalArgumentException("wrong year parameters passed to TimeBuilder.years");
    # }

    # private long startOfYear(int i) {
    #     ZonedDateTime date = LocalDateTime.of(i, 1, 1, 0, 0).atZone(ZoneOffset.UTC);
    #     return date.toInstant().toEpochMilli();
    # }


    def space() -> SpaceBuilder:
        space = DimensionImpl()
        space.type  = DimensionType.SPACE
        space.dimensionality = 2
        return SpaceBuilder(space)
    

    def time() -> TimeBuilder:
        time = DimensionImpl()
        time.type = DimensionType.TIME
        time.dimensionality = 1
        return TimeBuilder()
    

    def build(self) -> KlabGeometry:
        ret = KlabGeometry()
        if self.space:
            ret.addDimension(self.space)
        
        if self.time:
            ret.addDimension(self.time)
        
        return ret
    