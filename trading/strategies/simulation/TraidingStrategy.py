from abc import ABC
from abc import abstractmethod
from pandas import Series
import numpy as np

class TraidingStrategy(ABC):
    @abstractmethod
    def next(self, state: Series) -> np.ndarray:
        pass