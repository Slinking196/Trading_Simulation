from backtesting import Strategy
from trading.technical_indicators import ATR
from trading.technical_indicators import ADX
from trading.technical_indicators import DMP
from trading.technical_indicators import DMN
from trading.technical_indicators import SMA
import pandas as pd
import numpy as np

class SuperStategy_atr(Strategy):
    # x = [ 0=> len_atr, 
    #       1=> len_adx, 
    #       2=> len_sma, 
    #       3=> thres_adx,
    #       4=> factor_swl,
    #       5=> factor_sll,
    #       6=> factor_sws,
    #       7=> factor_sls]
    x = np.array([0,0,0,0,0,0,0])

    def init(self):
        data = {
            'high': pd.Series(self.data.High),
            'low':  pd.Series(self.data.Low),
            'close':pd.Series(self.data.Close),
        }

        self.atr = self.I(ATR, data, self.x[0])
        self.adx = self.I(ADX, data, self.x[1])
        self.dmp = self.I(DMP, data, self.x[1])
        self.dmn = self.I(DMN, data, self.x[1])
        self.sma = self.I(SMA, data, self.x[2])

    def next(self):

        # OPEN POS
        if not self.position.is_long and not self.position.is_short:
            dir = 'LONG' if self.dmp[-1] >= self.dmn else 'SHORT'
            if self.adx[-1] >= self.x[3]:
                if dir=='LONG' and self.data.Close[-1]<self.sma[-1]:
                    self.buy()
                    self.max_in_long = self.data.Close[-1]
                    self.stop_win_long  = self.data.Close[-1]+self.x[4]*self.atr[-1]
                    self.stop_loss_long = self.data.Close[-1]-self.x[5]*self.atr[-1]
                if dir=='SHORT' and self.data.Close[-1]>self.sma[-1]:
                    self.sell()
                    self.min_in_short = self.data.Close[-1]
                    self.stop_win_short  = self.data.Close[-1]-self.x[6]*self.atr[-1]
                    self.stop_loss_short = self.data.Close[-1]+self.x[7]*self.atr[-1]

        # IN POS LONG
        elif self.position.is_long:
            # subir stop loss long
            if self.data.Close[-1] > self.max_in_long: 
                self.max_in_long = self.data.Close[-1]
                self.stop_loss_long = self.data.Close[-1]-self.x[5]*self.atr[-1]
            # close pos long
            if (self.data.Close[-1]>self.stop_win_long) or (self.data.Close[-1]<self.stop_loss_long):
                self.position.close()

        # IN POS SHORT
        elif self.position.is_short:
            # bajar stop loss short
            if self.data.Close[-1] < self.min_in_short:
                self.min_in_short = self.data.Close[-1]
                self.stop_loss_short = self.data.Close[-1]+self.x[7]*self.atr[-1]
            # close pos short
            if (self.data.Close[-1]<self.stop_win_short) or (self.data.Close[-1]>self.stop_loss_short):
                self.position.close()