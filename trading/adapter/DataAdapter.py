from abc import abstractmethod
from abc import ABC
import pandas as pd

class DataAdapter(ABC):
    @abstractmethod
    def get_history(self, df: pd.DataFrame) -> pd.DataFrame:
        pass