from pandas import DataFrame
from trading.adapter import DataAdapter
# from trading.utils import ACTIONS
# from trading.utils import BET_STATES
import pandas_ta as ta
# import pandas as pd

class Data4SmaPorcentaje(DataAdapter):
    def __init__(self, n_sma1: int, n_sma2: int, n_sma3: int, n_sma4: int) -> None:
        self.__n_sma1 = n_sma1
        self.__n_sma2 = n_sma2
        self.__n_sma3 = n_sma3
        self.__n_sma4 = n_sma4
        # self.__sws = 0
        # self.__swl = 0
        # self.__sls = 0
        # self.__sll = 0
        # self.__reference = 0
        
        # self.__index = ['reference', 'bet_state', 'stop_win', 'stop_loss']

    def get_history(self, df_: DataFrame) -> DataFrame:
        df = df_[df_['open_time']%(5*60000)==0].copy()        
        df['sma_' + str(self.__n_sma1)] = ta.sma(df['close'], self.__n_sma1)
        df['sma_' + str(self.__n_sma2)] = ta.sma(df['close'], self.__n_sma2)
        df['sma_' + str(self.__n_sma3)] = ta.sma(df['close'], self.__n_sma3)
        df['sma_' + str(self.__n_sma4)] = ta.sma(df['close'], self.__n_sma4)
        df['sma_' + str(self.__n_sma1) + '_prev'] = df['sma_' + str(self.__n_sma1)].shift(1)
        df['sma_' + str(self.__n_sma2) + '_prev'] = df['sma_' + str(self.__n_sma2)].shift(1)
        df['sma_' + str(self.__n_sma3) + '_prev'] = df['sma_' + str(self.__n_sma3)].shift(1)
        df['sma_' + str(self.__n_sma4) + '_prev'] = df['sma_' + str(self.__n_sma4)].shift(1)
        df_cleaned = df.dropna()
        if 'volume' in df_cleaned: df_cleaned = df_cleaned.drop(columns= ['volume'])
        df_cleaned.reset_index(drop=True, inplace=True)

        return df_cleaned
        
    """def get_extra_info(self, state: pd.Series, new_state: pd.Series, bet_state: int, act: int):
        close = new_state[4]
        sma = new_state.to_list()[5:9]
        sma_prev = new_state.to_list()[9:13]
        
        if (self.__trading_state == BET_STATES.IN_LONG.value and self.__reference_point < state['close']) or \
            (self.__trading_state == BET_STATES.IN_SHORT.value and self.__reference_point > state['close']):
            self.__reference = state.iloc[4]

        if bet_state == BET_STATES.WAITING.value:
            if sma_prev[0] <= sma_prev[1] and sma[0] > sma[1]:
                self.__swl = close * self.__factor_swl
                self.__sll = close * self.__factor_sll
                self.__reference = close

                extra_info = pd.Series([self.__reference, bet_state, self.__swl, self.__sll], index= self.__index)
            elif sma_prev[2] <= sma_prev[3] and sma[2] < sma[3]:
                self.__sls = close * self.__factor_sls
                self.__sws = close * self.__factor_sws
                self.__reference = close

                extra_info = pd.Series([self.__reference, bet_state, self.__sws, self.__sls], index= self.__index)

            else:
                extra_info = pd.Series([0, bet_state, 0, 0])
        elif bet_state == BET_STATES.IN_LONG.value:
            if close > self.__reference:
                self.__sll = close * self.__factor_sll
            
            extra_info = pd.Series([self.__reference, bet_state, self.__swl, self.__sll], index= self.__index)
        
        elif bet_state == BET_STATES.IN_SHORT.value:
            if close > self.__reference:
                self.__sls = close * self.__factor_sls
            
            extra_info = pd.Series([self.__reference, bet_state, self.__sws, self.__sls], index= self.__index)

        return extra_info"""