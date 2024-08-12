from abc import abstractmethod
from abc import ABC
import pandas as pd

class DataAdapter(ABC):
    @abstractmethod
    def get_history(self, df: pd.DataFrame) -> pd.DataFrame:
        """
         En este método deben ir todas las tareas previas que se 
         le deseen realizar al dataset para la estrategía que se 
         quiera usar.
        """
        pass
