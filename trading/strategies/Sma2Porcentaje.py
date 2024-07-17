from pandas import Series
from trading.strategies import TraidingStrategy
from trading.utils import BET_STATES, ACTIONS
import numpy as np

class Sma2Porcentaje(TraidingStrategy):
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
        sma1, sma2 = state.iloc[5], state.iloc[6]
        sma1_prev, sma2_prev = state.iloc[7], state.iloc[8]
        reference = state.iloc[9]
        bet_state = state.iloc[10]

        actions = np.zeros(shape=(4, ))

        # OPEN POS
        if bet_state == BET_STATES.WAITING.value:

            # LONG
            if sma1_prev <= sma2_prev and sma1 > sma2:
                actions[ACTIONS.OPEN_LONG.value] = 1
                self.__swl = close * self.__factor_swl
                self.__sll = close * self.__factor_sll
            # SHORT
            elif sma1_prev >= sma2_prev and sma1 < sma2:
                actions[ACTIONS.OPEN_SHORT.value] = 1
                self.__sws = close * self.__factor_sws
                self.__sls = close * self.__factor_sls
            else:
                actions[ACTIONS.NONE.value] = 1

        # IN POS LONG
        elif bet_state == BET_STATES.IN_LONG.value:
            if close > self.__swl or \
                close < self.__sll:
                actions[ACTIONS.CLOSE_POS.value] = 1
            else:
                actions[ACTIONS.NONE.value] = 1
            if close > reference:
                actions[ACTIONS.NONE.value] = 1
                self.__sll = close * self.__factor_sll

        # IN POS SHORT
        elif bet_state == BET_STATES.IN_SHORT.value:
            if close < self.__sws or \
                close > self.__sls:
                actions[ACTIONS.CLOSE_POS.value] = 1
            else:
                actions[ACTIONS.NONE.value] = 1
            if close < reference:
                actions[ACTIONS.NONE.value] = 1
                self.__sls = close * self.__factor_sls

        return actions  