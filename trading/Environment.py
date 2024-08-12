import numpy as np
import pandas as pd
import pandas_ta as ta
from trading.utils import BET_STATES, ACTIONS
from trading.adapter import DataAdapter

class Environment():
    def __init__(self, file: str | pd.DataFrame, data_adapter: DataAdapter, cash: int) -> None:
        self.__data_adapter = data_adapter
        self.__data = self.__prepare_init_data__(file)
        self.__fee_ratio = 0.0005
        self.__cash = cash
        self.__init_cash = cash       
        self.__entry_price = 1   
        self.__exit_price = 0     
        self.__trading_state = BET_STATES.WAITING.value
        self.__last_act = 0

        # Max in long or min in short
        self.__reference_point = 1

        self.__time = 0          

    def __prepare_init_data__(self, file: str | pd.DataFrame):
        df = file if type(file) == pd.DataFrame else pd.read_csv(file)

        return self.__data_adapter.get_history(df)
    
    def reset(self) -> None:
        self.__cash = self.__init_cash
        self.__entry_price = 1
        self.__exit_price = 0
        self.__trading_state = BET_STATES.WAITING.value
        self.__time = 0
        self.__last_act = ACTIONS.NONE.value
        self.__reference_point = 1

        actual = self.__data.iloc[self.__time]
        extra_info = pd.Series([self.__reference_point, self.__trading_state], index= ['reference', 'trading_state'])
        actual = pd.concat([actual, extra_info])

        return actual

    def step(self, actions: np.ndarray) -> tuple:
        self.__last_act = np.argmax(actions)

        state = self.__data.iloc[self.__time]
        rewards = 0

        if self.__trading_state == BET_STATES.WAITING.value:
            if self.__last_act == ACTIONS.OPEN_LONG.value:
                self.__reference_point = state['close']
                self.__entry_price =  state['close']
                self.__trading_state = BET_STATES.IN_LONG.value

            if self.__last_act == ACTIONS.OPEN_SHORT.value:
                self.__reference_point = state['close']
                self.__entry_price =  state['close']
                self.__trading_state = BET_STATES.IN_SHORT.value

        elif self.__last_act == ACTIONS.CLOSE_POS.value:
            self.__exit_price = state['close']

            if self.__trading_state == BET_STATES.IN_LONG.value: gross_pnl = self.__exit_price * self.__cash * ((1 / self.__entry_price) - (1 / self.__exit_price))
            elif self.__trading_state == BET_STATES.IN_SHORT.value: gross_pnl = self.__exit_price * self.__cash * ((1 / self.__exit_price) - (1 / self.__entry_price))

            entry_fee = self.__cash * self.__fee_ratio
            exit_fee =  (self.__cash/self.__entry_price) * self.__exit_price *  self.__fee_ratio
            fee_paid = entry_fee + exit_fee

            rewards = gross_pnl - fee_paid

            self.__trading_state = BET_STATES.WAITING.value
            self.__cash += rewards
        
        elif (self.__trading_state == BET_STATES.IN_LONG.value and self.__reference_point < state['close']) or \
            (self.__trading_state == BET_STATES.IN_SHORT.value and self.__reference_point > state['close']):
            self.__reference_point = state['close']

        if self.__time + 1 == self.__data.shape[0]:
            state = pd.concat([state, pd.Series([self.__reference_point, self.__trading_state], index= ['reference', 'trading_state'])])
            ml_state = state.to_list()[0:5] + [state.iloc[9] - state.iloc[10]] + [state.iloc[5] - state.iloc[6]] + [state.iloc[7] - state.iloc[8]] + [state.iloc[11] - state.iloc[12]] + state.to_list()[13:15] + [state.iloc[4] / self.__entry_price] + [state.iloc[4] / self.__reference_point]

            ml_state = pd.Series(ml_state, index= ['open_time', 'open', 'high', 'low', 'close', 'sma1_prev', 'sma1', 'sma2', 'sma2_prev', 'reference', 'bet_state', 'price %', 'reference %'])

            return rewards, state, ml_state, True

        self.__time += 1
        new_state = self.__data.iloc[self.__time]
        extra_info = pd.Series([self.__reference_point, self.__trading_state], index= ['reference', 'trading_state'])
        new_state = pd.concat([new_state, extra_info])

        ml_state = new_state.to_list()[0:5] + [new_state.iloc[9] - new_state.iloc[10]] + [new_state.iloc[5] - new_state.iloc[6]] + [new_state.iloc[7] - new_state.iloc[8]] + [new_state.iloc[11] - new_state.iloc[12]] + new_state.to_list()[13:15] + [new_state.iloc[4] / self.__entry_price] + [new_state.iloc[4] / self.__reference_point]

        ml_state = pd.Series(ml_state, index= ['open_time', 'open', 'high', 'low', 'close', 'sma1_prev', 'sma1', 'sma2', 'sma2_prev', 'reference', 'bet_state', 'price %', 'reference %'])

        return rewards, new_state, ml_state, False
    
    def get_summary(self) -> None:
        return_percent = (100 * self.__cash - self.__init_cash) / self.__init_cash

        print(f"Return [%] {round(return_percent, 1):>40}")
    
    def get_data(self):
        return self.__data

    def actual_state(self) -> pd.Series:
        actual = self.__data.iloc[self.__time]
        extra = pd.Series([self.__reference_point, self.__trading_state], index= ['reference', 'trading_state'])
        actual = pd.concat([actual, extra])

        ml_state = actual.to_list()[0:5] + [actual.iloc[9] - actual.iloc[10]] + [actual.iloc[5] - actual.iloc[6]] + [actual.iloc[7] - actual.iloc[8]] + [actual.iloc[11] - actual.iloc[12]] + actual.to_list()[13:15] + [actual.iloc[4] / self.__entry_price] + [actual.iloc[4] / self.__reference_point]

        ml_state = pd.Series(ml_state, index= ['open_time', 'open', 'high', 'low', 'close', 'sma1_prev', 'sma1', 'sma2', 'sma2_prev', 'reference', 'bet_state', 'price %', 'reference %'])

        return actual, ml_state

    def get_money(self) -> float:
        return self.__cash
    
    def get_traiding_state(self) -> BET_STATES:
        return self.__trading_state
    
    def get_time(self) -> int:
        return self.__time