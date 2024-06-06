import numpy as np
import pandas as pd
import pandas_ta as ta
from enum import Enum

class STATES(Enum):
    IN_LONG = 1
    IN_SHORT = 2
    WAITING = 3

class ACTIONS(Enum):
    OPEN_LONG = 1
    OPEN_SHORT = 2
    CLOSE_POS = 3
    NONE = 4

class Environment():
    def __init__(self, file_name: str, range_time: int = 5, n_sma1: int = 10, n_sma2: int = 20, n_rsi: int = 15) -> None:
        self.data = self.__prepare_init_data__(file_name, range_time, n_sma1, n_sma2, n_rsi)
        self.money = 1          # Entorno
        self.entry_price = 0    # Entorno
        self.exit_price = 0     # Entorno
        self.max_long = 0       # Estrategia
        self.min_short = 0      # Estrategia
        self.stop_win = 0       # Estrategia
        self.trading_state = STATES.WAITING # Entorno
        self.time = 0           # Entorno
        self.historial_capital = [] # Entorno

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

        print(df_grouped.head(50))

        return df_grouped
    
    def reset(self) -> None:
        self.money = 1
        self.entry_price = 0
        self.exit_price = 0
        self.max_long = 0
        self.min_short = 0
        self.stop_win = 0
        self.trading_state = STATES.WAITING
        self.time = 0
        self.historial_capital = []

    def step(self, actions: np.ndarray, x: np.ndarray):
        act = np.argmax(actions)
        stop_long = x[-4]           # Estrategia
        stop_short = x[-3]          # Estrategia
        take_profit_long = x[-2]    # Estrategia
        take_profit_short = x[-1]   # Estrategia

        state = self.data.iloc[self.time]
        rewards = 0
        end = False

        if self.trading_state == STATES.WAITING:
            if act == ACTIONS.OPEN_LONG:
                self.entry_price =  state['close']
                self.max_long = state['close']
                self.stop_win = self.entry_price * take_profit_long
                self.trading_state = STATES.IN_LONG

            if act == ACTIONS.OPEN_SHORT:
                self.entry_price =  state['open']
                self.min_short = state['open']
                self.stop_win = self.entry_price * take_profit_short
                self.trading_state = STATES.IN_SHORT

        elif self.trading_state == STATES.IN_LONG:
            if state['open'] > self.max_long: self.max_long = state['open']

            if (state['open'] < self.max_long * stop_long) or (state['open'] > self.stop_win):
                # Calculo de ganancia
                self.exit_price = state['open']
                rewards = self.exit_price - self.entry_price
                
                end = True
                self.money += rewards
                self.trading_state = STATES.WAITING

        elif self.trading_state == STATES.IN_SHORT:
            if state['open'] < self.min_short: self.min_short = state['price']

            if (state['open'] > self.min_short * stop_short) or (state['price'] < self.stop_win):
                self.exit_price = state['open']
                rewards = self.entry_price - self.exit_price

                end = True
                self.money += rewards
                self.trading_state = STATES.WAITING

        self.historial_capital.append((self.money, self.time))

        self.time += 1
        new_state = self.data.iloc[self.time]

        return rewards, new_state, end
    
    def get_historial(self) -> np.ndarray:
        return np.array(self.historial_capital)
    
    def get_money(self) -> float:
        return self.money
    
    def get_traiding_state(self) -> STATES:
        return self.trading_state
                
env = Environment('./dataset.csv')