from enum import Enum
import re
class Item:
    __slots__ = 'value', 
    
    def __init__(self, value):
        self.value = value
        try:
            type(self).pattern
        except AttributeError:
            raise TypeError(
                f"children of '{Item.__name__}' must define a .pattern "
                f"'{type(self).__name__}' doesnt.")

    def __repr__(self):
        return f'{type(self).__name__}<{self.value}>'
    
    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return type(self) is type(other)

    def __new__(cls, value, *args, **kwargs):
        if cls is Item:
            raise TypeError(f"only children of '{cls.__name__}' may be instantiated")
        return object.__new__(cls, *args, **kwargs)

    @property
    def name(self):
        return type(self).__name__


class Name(Item):
    pattern = '[a-zA-Z]\w*'
    
class Number(Item):
    pattern = '\d*'

class Unknown(Item):
    pattern = '(?:.|\n)*'

class OperatorWildcard(Item):
    pattern = 'Anyop'
    def __eq__(self, other):
        return isinstance(other, Operator) or type(self) is type(other)
    def __hash__(self):
        return hash(self.value)

class NotName(Item):
    pattern = 'Notname'
    def __eq__(self, other):
        return not isinstance(other, Name) or type(self) is type(other)
    def __hash__(self):
        return hash(self.value)

class FixedToken(Enum):

    def __repr__(self):
        return f'<{self.value}>'

    @property
    def pattern(self):
        return re.escape(self.value)


class Separator(FixedToken):
    OPEN_CURLY = '{'
    CLOSE_CURLY = '}'
    OPEN_PAR = '('
    CLOSE_PAR = ')'
    ASSIGN = '='
    BODYDEF = '=>'
    EXPR_SPLITTER = ';'



class Operator(FixedToken):
    POWER = '^'
    POWER_PYTHONIC = '**'
    MULT = '*'
    DIV = '/'
    PLUS = '+'
    MINUS = '-'
    MODULO = '%'

class KW(FixedToken):
    ...

class RuleKW(KW):
    SHAPE = 'shape'
    SUB = 'sub'

class FlowKW(KW):
    APPLY = 'apply'
    WITH = 'with'
    TO = 'to'
    REVERSE = 'reverse'

class SugarKW(KW):
    EXPAND = 'expand'

class ApplyStratKW(KW):
    ALL = 'all'
    FIRST = 'first'


const_types = (
    Separator,
    Operator,
    RuleKW,
    FlowKW,
    SugarKW,
    ApplyStratKW
)

varying_types = (
    OperatorWildcard,
    NotName,
    Name,
    Number,
    Unknown
)