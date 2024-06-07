import numpy as np
import pandas as pd
import pandas_ta as ta
from enum import Enum
from utils import STATES, ACTIONS

class Environment():
    def __init__(self, file_name: str, range_time: int = 5, n_sma1: int = 10, n_sma2: int = 20, n_rsi: int = 15) -> None:
        self.data = self.__prepare_init_data__(file_name, range_time, n_sma1, n_sma2, n_rsi)
        self.fee_ratio = 0.0005
        self.money = 1          
        self.entry_price = 0    
        self.exit_price = 0     
        self.trading_state = STATES.WAITING 
        self.time = 0           

    def __prepare_init_data__(self, file_name: str, range_time: int, n_sma1: int, n_sma2: int, n_rsi: int):
        df = pd.read_csv(file_name)

        df_grouped = df.groupby(df.index // range_time).agg({
                        'open_time': 'first',
                        'open': 'first',
                        'high': 'max',
                        'low': 'min',
                        'close': 'last',
                        'volume': 'sum'
                    }).reset_index(drop=True)
        
        df_grouped['sma_' + str(n_sma1)] = ta.sma(df['close'], n_sma1)
        df_grouped['sma_' + str(n_sma2)] = ta.sma(df['close'], n_sma2)
        df_grouped['rsi_' + str(n_rsi)] = ta.rsi(df['close'], n_rsi)
        df_cleaned = df_grouped.dropna()
        df_cleaned.reset_index(drop=True, inplace=True)

        return df_cleaned
    
    def reset(self) -> None:
        self.money = 1
        self.entry_price = 0
        self.exit_price = 0
        self.trading_state = STATES.WAITING
        self.time = 0

    def step(self, actions: np.ndarray) -> tuple:
        act = np.argmax(actions)

        state = self.data.iloc[self.time]
        rewards = 0
        end = False

        if self.trading_state == STATES.WAITING:
            if act == ACTIONS.OPEN_LONG:
                self.entry_price =  state['close']
                self.trading_state = STATES.IN_LONG

            if act == ACTIONS.OPEN_SHORT:
                self.entry_price =  state['close']
                self.trading_state = STATES.IN_SHORT

        elif act == ACTIONS.CLOSE_POS:
            self.exit_price = state['close']

            if self.trading_state == STATES.IN_LONG: gross_pnl = ((1 / self.entry_price) - (1 / self.exit_price))
            elif self.trading_state == STATES.IN_SHORT: gross_pnl = ((1 / self.exit_price) - (1 / self.entry_price))

            entry_fee = self.fee_ratio * (1 / self.entry_price)
            exit_fee = self.fee_ratio * (1 / self.exit_price)
            fee_paid = entry_fee + exit_fee

            rewards = gross_pnl - (fee_paid)
            end = True

        self.time += 1
        new_state = self.data.iloc[self.time]

        return rewards, new_state, end
    
    def get_money(self) -> float:
        return self.money
    
    def get_traiding_state(self) -> STATES:
        return self.trading_state