from .exceptions import KlabIllegalStateException
from .utils import NumberUtils

class Range():

    def __init__(self, lower:float = None, upper:float = None, lowerExclusive:bool = None, upperExclusive:bool = None):
        self.lowerBound = NumberUtils.NEGATIVE_INFINITY
        if lower:
            self.lowerBound = lower
        self.upperBound = NumberUtils.POSITIVE_INFINITY
        if upper:
            self.upperBound = upper
        self.lowerExclusive = False
        if lowerExclusive:
            self.lowerExclusive = lowerExclusive
        self.upperExclusive = False
        if upperExclusive:
            self.upperExclusive = upperExclusive
        self.lowerInfinite = True
        self.upperInfinite = True
    
    def getLowerBound(self):
        return self.lowerBound
    
    def getUpperBound(self):
        return self.upperBound
    
    def __eq__(self, other: object) -> bool:
        if id(self) == id(other):
            return True
        if other == None:
            return False
        if not isinstance(other, Range):
            return False
        if self.lowerInfinite != other.lowerInfinite:
            return False
        if self.lowerBound != other.lowerBound:
            return False
        if self.lowerExclusive != other.lowerExclusive:
            return False
        if self.upperInfinite != other.upperInfinite:
            return False
        if self.upperBound != other.upperBound:
            return False
        if self.upperExclusive != other.upperExclusive:
            return False
        return True
    
    def contains(self, other) -> bool:
        if self == other:
            return True
        
        if not self.lowerInfinite and not other.lowerInfinite and (self.lowerBound >= other.lowerBound if self.lowerExclusive else self.lowerBound > other.lowerBound):
            return False
        
        if not self.upperInfinite and not other.upperInfinite and (self.upperBound <= other.upperBound if self.upperExclusive else self.upperBound < other.upperBound):
            return False
        
        if not self.upperInfinite and other.upperInfinite:
            return False
        
        if not self.lowerInfinite and other.lowerInfinite:
            return False
        
        return True
    


class Observable():
    """
    Textual peer of a true observable with fluent API and minimal validation.
    Used to discriminate observables in inputs of the observation functions.
    """

    def __init__(self, s:str):
        self.semantics = s
        self.name = None
        self.unit = None
        self.value = None
        self.range = None

    @staticmethod
    def create(s):
        return Observable(s)
    

    def named(self, name):
        if self.name:
            raise KlabIllegalStateException("cannot add modifiers more than once")
        
        self.name = name
        return self
    
    def range(self, range:Range):
        if self.unit or self.range:
            raise KlabIllegalStateException("cannot add modifiers more than once")

        self.range = range
        return self
    

    def value(self, value:any):
        if self.value:
            raise KlabIllegalStateException("cannot add modifiers more than once")
        
        self.value = value
        return self

    def unit(self, unit):
        """Pass a valid unit or currency. No validation is done."""
        if self.unit or self.range:
            raise KlabIllegalStateException("cannot add modifiers more than once")
        
        self.unit = unit
        return self

    def __str__(self) -> str:
        string = ""
        if self.value:
            string += f"{self.value} as "
        string += self.semantics
        if self.range:
            string += f" {self.range.getLowerBound()} to {self.range.getUpperBound()}"
        if self.unit:
            string += f" in {self.unit}"
        if self.name:
            string += f" named {self.name}"
        return string

    def getName(self):
        return self.name




