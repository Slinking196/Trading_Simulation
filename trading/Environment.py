import numpy as np
import pandas as pd
import pandas_ta as ta
from enum import Enum
from trading.utils import BET_STATES, ACTIONS

class Environment():
    def __init__(self, file_name: str, range_time: int = 5, n_sma1: int = 10, n_sma2: int = 20, n_rsi: int = 15) -> None:
        self.__data = self.__prepare_init_data__(file_name, range_time, n_sma1, n_sma2, n_rsi)
        self.__fee_ratio = 0.0005
        self.__money = 1          
        self.__entry_price = 0    
        self.__exit_price = 0     
        self.__trading_state = BET_STATES.WAITING

        self.__reference_point = 0

        self.__time = 0          

    def __prepare_init_data__(self, file_name: str, range_time: int, n_sma1: int, n_sma2: int, n_atr: int):
        df = pd.read_csv(file_name)

        df_grouped = df.groupby(df.index // range_time).agg({
                        'open_time': 'first',
                        'open': 'first',
                        'high': 'max',
                        'low': 'min',
                        'close': 'last',
                        'volume': 'sum'
                    }).reset_index(drop=True)

        df_grouped['atr' + str(n_atr)] = ta.atr(df['high'], df['low'], df['close'], n_atr)
        df_grouped['sma_' + str(n_sma1)] = ta.sma(df['close'], n_sma1)
        df_grouped['sma_' + str(n_sma2)] = ta.sma(df['close'], n_sma2)
        df_grouped['sma_' + str(n_sma1) + '_prev'] = df_grouped['sma_' + str(n_sma1)].shift(1)
        df_grouped['sma_' + str(n_sma2) + '_prev'] = df_grouped['sma_' + str(n_sma2)].shift(1)
        df_cleaned = df_grouped.dropna()
        df_cleaned = df_cleaned.drop(columns= ['volume'])
        df_cleaned.reset_index(drop=True, inplace=True)

        return df_cleaned
    
    def reset(self) -> None:
        self.__money = 1
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

            if self.__trading_state == BET_STATES.IN_LONG: gross_pnl = self.__money * ((1 / self.__entry_price) - (1 / self.__exit_price))
            elif self.__trading_state == BET_STATES.IN_SHORT: gross_pnl = self.__money * ((1 / self.__exit_price) - (1 / self.__entry_price))

            entry_fee = self.__money * self.__fee_ratio * (1 / self.__entry_price)
            exit_fee = self.__money * self.__fee_ratio * (1 / self.__exit_price)
            fee_paid = entry_fee + exit_fee

            rewards = gross_pnl - (fee_paid)

            self.__money += rewards
        
        elif (self.__trading_state == BET_STATES.IN_LONG and self.__reference_point < state['close']) or \
            (self.__trading_state == BET_STATES.IN_SHORT and self.__reference_point > state['close']):
            self.__reference_point = state['close']

        self.__time += 1
        if self.__time == self.__data.shape[0]:
            return rewards, state, True

        new_state = self.__data.iloc[self.__time]
        new_state = pd.concat([new_state, pd.Series([self.__reference_point, self.__trading_state.value], index=['reference_point', 'state'])])

        return rewards, new_state, False
    
    def get_data(self):
        return self.__data

    def actual_state(self) -> pd.Series:
        actual = self.__data.iloc[self.__time]
        actual = pd.concat([actual, pd.Series([self.__reference_point, self.__trading_state.value], index=['reference_point', 'state'])])

        return actual

    def get_money(self) -> float:
        return self.__money
    
    def get_traiding_state(self) -> BET_STATES:
        return self.__trading_state