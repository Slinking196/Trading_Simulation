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
        self.__entry_price = 0    
        self.__exit_price = 0     
        self.__trading_state = BET_STATES.WAITING

        self.__reference_point = 0

        self.__time = 0          

    def __prepare_init_data__(self, file: str | pd.DataFrame):
        df = file if type(file) == pd.DataFrame else pd.read_csv(file)

        return self.__data_adapter.get_history(df)
    
    def reset(self) -> None:
        self.__cash = self.__init_cash
        self.__entry_price = 0
        self.__exit_price = 0
        self.__trading_state = BET_STATES.WAITING
        self.__time = 0

        return self.__data.iloc[self.__time]

    def step(self, actions: np.ndarray) -> tuple:
        act = np.argmax(actions)

        state = self.__data.iloc[self.__time]
        rewards = 0

        if self.__trading_state == BET_STATES.WAITING:
            if act == ACTIONS.OPEN_LONG.value:
                self.__reference_point = state['close']
                self.__entry_price =  state['close']
                self.__trading_state = BET_STATES.IN_LONG

            if act == ACTIONS.OPEN_SHORT.value:
                self.__reference_point = state['close']
                self.__entry_price =  state['close']
                self.__trading_state = BET_STATES.IN_SHORT

        elif act == ACTIONS.CLOSE_POS.value:
            self.__exit_price = state['close']

            if self.__trading_state == BET_STATES.IN_LONG: gross_pnl = self.__exit_price * self.__cash * ((1 / self.__entry_price) - (1 / self.__exit_price))
            elif self.__trading_state == BET_STATES.IN_SHORT: gross_pnl = self.__exit_price * self.__cash * ((1 / self.__exit_price) - (1 / self.__entry_price))

            entry_fee = self.__cash * self.__fee_ratio
            exit_fee =  (self.__cash/self.__entry_price) * self.__exit_price *  self.__fee_ratio
            fee_paid = entry_fee + exit_fee

            rewards = gross_pnl - fee_paid

            self.__trading_state = BET_STATES.WAITING
            self.__cash += rewards
        
        elif (self.__trading_state == BET_STATES.IN_LONG and self.__reference_point < state['close']) or \
            (self.__trading_state == BET_STATES.IN_SHORT and self.__reference_point > state['close']):
            self.__reference_point = state['close']

        if self.__time + 1 == self.__data.shape[0]:
            return rewards, state, True

        self.__time += 1
        new_state = self.__data.iloc[self.__time]
        new_state = pd.concat([new_state, pd.Series([self.__reference_point, self.__trading_state.value], index=['reference_point', 'state'])])

        return rewards, new_state, False
    
    def get_summary(self) -> None:
        return_percent = (100 * self.__cash - self.__init_cash) / self.__init_cash

        print(f"Return [%] {round(return_percent, 1):>40}")
    
    def get_data(self):
        return self.__data

    def actual_state(self) -> pd.Series:
        actual = self.__data.iloc[self.__time]
        actual = pd.concat([actual, pd.Series([self.__reference_point, self.__trading_state.value], index=['reference_point', 'state'])])

        return actual

    def get_money(self) -> float:
        return self.__cash
    
    def get_traiding_state(self) -> BET_STATES:
        return self.__trading_state
    
    def get_time(self) -> int:
        return self.__time