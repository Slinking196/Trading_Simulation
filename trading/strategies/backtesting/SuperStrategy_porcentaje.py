from backtesting import Strategy
from trading.technical_indicators import ADX
from trading.technical_indicators import DMP
from trading.technical_indicators import DMN
from trading.technical_indicators import SMA
import pandas as pd
import numpy as np

class SuperStategy_porcentaje(Strategy):
    # x = [ 0=> len_adx, 
    #       1=> len_sma, 
    #       2=> thres_adx,
    #       3=> factor_swl,
    #       4=> factor_sll,
    #       5=> factor_sws,
    #       6=> factor_sls]
    x = np.array([0,0,0,0,0,0])

    def init(self):
        data = {
            'high': pd.Series(self.data.High),
            'low':  pd.Series(self.data.Low),
            'close':pd.Series(self.data.Close),
        }

        self.adx = self.I(ADX, data, self.x[0])
        self.dmp = self.I(DMP, data, self.x[0])
        self.dmn = self.I(DMN, data, self.x[0])
        self.sma = self.I(SMA, data, self.x[1])

    def next(self):

        # OPEN POS
        if not self.position.is_long and not self.position.is_short:
            dir = 'LONG' if self.dmp[-1] >= self.dmn else 'SHORT'
            if self.adx[-1] >= self.x[2]:
                if dir=='LONG' and self.data.Close[-1]<self.sma[-1]:
                    self.buy()
                    self.max_in_long = self.data.Close[-1]
                    self.stop_win_long  = self.data.Close[-1]*self.x[3]
                    self.stop_loss_long = self.data.Close[-1]*self.x[4]
                if dir=='SHORT' and self.data.Close[-1]>self.sma[-1]:
                    self.sell()
                    self.min_in_short = self.data.Close[-1]
                    self.stop_win_short  = self.data.Close[-1]*self.x[5]
                    self.stop_loss_short = self.data.Close[-1]*self.x[6]

        # IN POS LONG
        elif self.position.is_long:
            # subir stop loss long
            if self.data.Close[-1] > self.max_in_long: 
                self.max_in_long = self.data.Close[-1]
                self.stop_loss_long = self.data.Close[-1]*self.x[4]
            # close pos long
            if (self.data.Close[-1]>self.stop_win_long) or (self.data.Close[-1]<self.stop_loss_long):
                self.position.close()

        # IN POS SHORT
        elif self.position.is_short:
            # bajar stop loss short
            if self.data.Close[-1] < self.min_in_short:
                self.min_in_short = self.data.Close[-1]
                self.stop_loss_short = self.data.Close[-1]*self.x[6]
            # close pos short
            if (self.data.Close[-1]<self.stop_win_short) or (self.data.Close[-1]>self.stop_loss_short):
                self.position.close()