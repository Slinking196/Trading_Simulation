from backtesting import Strategy
from trading.technical_indicators import SMA
from trading.utils import ACTIONS
import pandas as pd
import numpy as np

class Strategy2sma_porcentaje(Strategy):
    # x = [ 0=> len_sma1, 
    #       1=> len_sma2, 
    #       2=> factor_swl,
    #       3=> factor_sll,
    #       4=> factor_sws,
    #       5=> factor_sls]
    x = np.array([0,0,0,0,0,0])
    

    def init(self):
        data = {
            'high': pd.Series(self.data.High),
            'low':  pd.Series(self.data.Low),
            'close':pd.Series(self.data.Close),
        }        
        self.sma1 = self.I(SMA,data,self.x[0])
        self.sma2 = self.I(SMA,data,self.x[1])
        self.cont = np.zeros((4, ))
    
    def next(self):
        # OPEN POS
        # print(f"sma1[-2]: {self.sma1[-2]} sma2[-2]: {self.sma2[-2]}; sma1[-1]: {self.sma1[-1]} sma2[-1]: {self.sma2[-1]}")
        if not self.position.is_long and not self.position.is_short:
            # LONG 
            if self.sma1[-2]<=self.sma2[-2] and self.sma1[-1]>self.sma2[-1]:
                self.buy()
                self.max_in_long = self.data.Close[-1]
                self.stop_win_long  = self.data.Close[-1]*self.x[2]
                self.stop_loss_long = self.data.Close[-1]*self.x[3]
                self.cont[ACTIONS.OPEN_LONG.value] += 1
            # SHORT
            elif self.sma1[-2]>=self.sma2[-2] and self.sma1[-1]<self.sma2[-1]:
                self.sell()
                self.min_in_short = self.data.Close[-1]
                self.stop_win_short  = self.data.Close[-1]*self.x[4]
                self.stop_loss_short = self.data.Close[-1]*self.x[5]
                self.cont[ACTIONS.OPEN_SHORT.value] += 1
            else:
                self.cont[ACTIONS.NONE.value] += 1

        # IN POS LONG
        elif self.position.is_long:
            # subir stop loss long
            if self.data.Close[-1] > self.max_in_long: 
                self.max_in_long = self.data.Close[-1]
                self.stop_loss_long = self.data.Close[-1]*self.x[3]
            # close pos long
            if (self.data.Close[-1]>self.stop_win_long) or (self.data.Close[-1]<self.stop_loss_long):
                self.position.close()
                self.cont[ACTIONS.CLOSE_POS.value] += 1
            else:
                self.cont[ACTIONS.NONE.value] += 1

        # IN POS SHORT
        elif self.position.is_short:
            # bajar stop loss short
            if self.data.Close[-1] < self.min_in_short:
                self.min_in_short = self.data.Close[-1]
                self.stop_loss_short = self.data.Close[-1]*self.x[5]
            # close pos short
            if (self.data.Close[-1]<self.stop_win_short) or (self.data.Close[-1]>self.stop_loss_short):
                self.position.close()
                self.cont[ACTIONS.CLOSE_POS.value] += 1
            else:
                self.cont[ACTIONS.NONE.value] += 1
        print(self.cont)