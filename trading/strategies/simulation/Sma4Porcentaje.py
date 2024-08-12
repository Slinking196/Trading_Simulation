from pandas import Series
from trading.strategies.simulation import TraidingStrategy
from trading.utils import BET_STATES, ACTIONS
import numpy as np

class Sma4Porcentaje(TraidingStrategy):
    def __init__(self, 
                 factor_swl: float, 
                 factor_sll: float, 
                 factor_sws: float, 
                 facto_sls: float
                 ) -> None:
        self.__factor_swl = factor_swl
        self.__factor_sll = factor_sll
        self.__factor_sws = factor_sws
        self.__factor_sls = facto_sls

    def next(self, state: Series) -> np.ndarray:
        close = state.iloc[4]
        sma = state.to_list()[5:9]
        sma_prev = state.to_list()[9:13]
        reference = state.iloc[13]
        bet_state = state.iloc[14]
        
        actions = np.zeros((4, ))

        if bet_state == BET_STATES.WAITING.value:
            if sma_prev[0] <= sma_prev[1] and sma[0] > sma[1]:
                actions[ACTIONS.OPEN_LONG.value] = 1
                self.__swl = close * self.__factor_swl
                self.__sll = close * self.__factor_sll
            elif sma_prev[2] >= sma_prev[3] and sma[2] < sma[3]:
                actions[ACTIONS.OPEN_SHORT.value] = 1
                self.__sls = close * self.__factor_sls
                self.__sws = close * self.__factor_sws
            else:
                actions[ACTIONS.NONE.value] = 1
        
        elif bet_state == BET_STATES.IN_LONG.value:
            if close > reference:
                self.__sll = close * self.__factor_sll
            
            if close > self.__swl or close < self.__sll:
                actions[ACTIONS.CLOSE_POS.value] = 1
            else:
                actions[ACTIONS.NONE.value] = 1

        elif bet_state == BET_STATES.IN_SHORT.value:
            if close < reference:
                self.__sls = close * self.__factor_sls

            if close < self.__sws or close > self.__sls:
                actions[ACTIONS.CLOSE_POS.value] = 1
            else:
                actions[ACTIONS.NONE.value] = 1
        
        return actions