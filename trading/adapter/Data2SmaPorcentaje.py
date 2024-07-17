from pandas import DataFrame
from trading.adapter import DataAdapter
import pandas_ta as ta

class Data2SmaPorcentaje(DataAdapter):
    def __init__(self, n_sma1, n_sma2) -> None:
        self.__n_sma1 = n_sma1
        self.__n_sma2 = n_sma2

    def get_history(self, df: DataFrame) -> DataFrame:
        """df_grouped = df.groupby(df.index // range_time).agg({
                        'open_time': 'first',
                        'open': 'first',
                        'high': 'max',
                        'low': 'min',
                        'close': 'last',
                        'volume': 'sum'
                    }).reset_index(drop=True)"""
        
        df['sma_' + str(self.__n_sma1)] = ta.sma(df['close'], self.__n_sma1)
        df['sma_' + str(self.__n_sma2)] = ta.sma(df['close'], self.__n_sma2)
        df['sma_' + str(self.__n_sma1) + '_prev'] = df['sma_' + str(self.__n_sma1)].shift(1)
        df['sma_' + str(self.__n_sma2) + '_prev'] = df['sma_' + str(self.__n_sma2)].shift(1)
        df_cleaned = df.dropna()
        if 'volume' in df_cleaned: df_cleaned = df_cleaned.drop(columns= ['volume'])
        df_cleaned.reset_index(drop=True, inplace=True)

        return df_cleaned