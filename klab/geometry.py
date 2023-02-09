from enum import Enum
from .exceptions import KlabIllegalArgumentException
import sys
from .utils import NumberUtils

class Granularity(Enum):
        SINGLE = "SINGLE"
        MULTIPLE = "MULTIPLE"

class Type(Enum):
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


NONDIMENSIONAL = -1
"""Constant for non-dimensional (referenced but not distributed) return value of Dimension#getDimensionality()."""

UNDEFINED = -1
"""Constant for undefined dimension size."""

INFINITE_SIZE = sys.maxsize
"""Infinite size, only admitted for the time dimension."""

PARAMETER_SPACE_SHAPE = "shape"
"""Shape specs in WKB."""

class DimensionImpl():
    def __init__(self) -> None:
         self.regular = False
         self.dimensionality = 0
         self.generic = False
         self.coverage = 1.0
         self.parameters = {}
         self.shape = None
         self.type = None

    
    def getType() -> Type:
        return type

    def copy(self):
        ret =  DimensionImpl()
        ret.type = self.type
        ret.regular = self.regular
        ret.dimensionality = self.dimensionality
        if self.shape:
            ret.shape = self.shape[:]
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
        if self.shape:
            self.product(self.shape)
        else:
            return UNDEFINED

    def product(self, shape2):
        ret = 1
        for l in self.shape:
            ret *= l
        return ret

    # public long[] shape() {
    #     return shape == null ? Utils.newArray(UNDEFINED, dimensionality) : shape;
    # }

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
    #     if (shape == null) {
    #         throw new KlabIllegalArgumentException("geometry: cannot address a geometry with no shape");
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
    #         return ((shape[1] - offsets[1] - 1) * shape[0]) + offsets[0];
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
    

    # public long[] getShape() {
    #     return shape;
    # }

    # public void setShape(long[] shape) {
    #     this.shape = shape;
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

    #     // TODO must enable a boundary shape to cut any geometry, regular or not, as
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
        self.scalar = False
        self.granularity = Granularity.SINGLE
        self.dimensions = []
        self.child = None

    @staticmethod
    def create(geometrySpec:str):
        return KlabGeometry.makeGeometry(geometrySpec, 0)

    @staticmethod
    def empty():
        return KlabGeometry()
    
    @staticmethod
    def scalar():
        ret = KlabGeometry()
        ret.scalar = True
        return ret
    
    def newDimension(self) -> DimensionImpl:
        return DimensionImpl()
	
    @staticmethod
    def makeGeometry(geometry:str, i:int):
        """
        read the geometry defined starting at the i-th character
        """

        ret = KlabGeometry();

        if geometry == None or geometry == "X":
            return KlabGeometry.empty()

        if geometry == "*":
            return KlabGeometry.scalar();
        
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
    def readParameters(kvs:str):
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

        

        dims.sort(key=self.compare);

        ret = ""
        if self.granularity == Granularity.MULTIPLE:
            ret = "#"

        for dim in dims:
            ret += self.encodeDimension(dim);
        
        if self.child:
            ret += "," + self.child.encode();
        
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

        ret += dim.getDimensionality()
        if dim.shape() and not KlabGeometry.isUndefined(dim.shape()):
            ret += "("
            for i in range(0, len(dim.shape())):
                sep = ","
                if i == 0:
                    sep = ""
                size = str(dim.shape()[i])
                if dim.shape()[i] == INFINITE_SIZE:
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
                ret += key + "=" + KlabGeometry.encodeVal(dim.getParameters().get(key))
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
	

    def compare(item1, item2):
        if item1.getType() == Type.TIME:
            return -1
        else:
            return 0