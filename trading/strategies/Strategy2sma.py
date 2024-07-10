import numpy as np
from pandas import Series
from trading.utils import ACTIONS, BET_STATES

class Strategy2sma():
    def __init__(self, factor_swl, factor_sll, factor_sws, factor_sls) -> None:
        self.__factor_swl = factor_swl
        self.__factor_sll = factor_sll
        self.__factor_sws = factor_sws
        self.__factor_sls = factor_sls
    
    def next(self, state: Series) -> np.ndarray:
        actions = np.zeros(shape=(4))
        trading_state = state.iloc[11]
        sma1 = [state.iloc[6], state.iloc[8]]
        sma2 = [state.iloc[7], state.iloc[9]]
        atr = state.iloc[5]
        reference = state.iloc[10]
        close = state.iloc[4]

        # OPEN POS
        if trading_state == BET_STATES.WAITING.value:
            # LONG
            if sma1[-2] <= sma2[-2] and sma1[-1] > sma2[-1]:
                actions[ACTIONS.OPEN_LONG.value] = 1

            # SHORT
            elif sma1[-2] >= sma2[-2] and sma1[-1] < sma2[-1]:
                actions[ACTIONS.OPEN_SHORT.value] = 1
            else:
                actions[ACTIONS.NONE.value] = 1
        
        # IN LONG
        elif trading_state == BET_STATES.IN_LONG.value:
            # RAISE BET
            if close > reference:
                actions[ACTIONS.NONE.value] = 1

            # CLOSE POS
            elif close > atr * self.__factor_swl or close < atr * self.__factor_sll:
                actions[ACTIONS.CLOSE_POS.value] = 1
        
        # IN SHORT
        elif trading_state == BET_STATES.IN_SHORT.value:
            # LOWER BET
            if close < reference:
                actions[ACTIONS.NONE.value] = 1
            
            # CLOSE POS
            elif close < self.__factor_sws * atr or close > self.__factor_sls * atr:
                actions[ACTIONS.CLOSE_POS.value] = 1

        return actions