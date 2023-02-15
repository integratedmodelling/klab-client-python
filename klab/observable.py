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
        self._semantics = s
        self._name = None
        self._unit = None
        self._value = None
        self._range = None

    @staticmethod
    def create(s):
        return Observable(s)
    

    def named(self, name):
        if self._name:
            raise KlabIllegalStateException("cannot add modifiers more than once")
        
        self._name = name
        return self
    
    def range(self, range:Range):
        if self._unit or self._range:
            raise KlabIllegalStateException("cannot add modifiers more than once")

        self._range = range
        return self
    

    def value(self, value:any):
        if self._value:
            raise KlabIllegalStateException("cannot add modifiers more than once")
        
        self._value = value
        return self

    def unit(self, unit):
        """Pass a valid unit or currency. No validation is done."""
        if self._unit or self._range:
            raise KlabIllegalStateException("cannot add modifiers more than once")
        
        self._unit = unit
        return self

    def __str__(self) -> str:
        string = ""
        if self._value:
            string += f"{self._value} as "
        string += self._semantics
        if self._range:
            string += f" {self._range.getLowerBound()} to {self._range.getUpperBound()}"
        if self._unit:
            string += f" in {self._unit}"
        if self._name:
            string += f" named {self._name}"
        return string

    def getName(self):
        return self._name




