from abc import ABC
from abc import abstractmethod
from pandas import Series
import numpy as np

class TraidingStrategy(ABC):
    @abstractmethod
    def next(self, state: Series) -> np.ndarray:
        """
         Método en el que se realizará el proceso de analisis
         para poder tomar la decisión de compra o venta de 
         criptomoneda por cada vela japonesa que reciba
        """
        pass