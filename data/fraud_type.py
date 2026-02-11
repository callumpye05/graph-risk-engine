from enum import Enum
from enum import auto


class FraudType(Enum) : 
    LARGE_AMOUNT = auto()
    REPEATED_BURST = auto()
    CIRCULAR_LAUNDERING = auto()


 