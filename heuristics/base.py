from abc import ABC, abstractmethod

class Heuristic(ABC) : 

    @abstractmethod
    def evaluate(self , account_id , stats) ->float:
        pass 