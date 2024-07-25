from backtesting import Strategy
from trading.technical_indicators import SMA
import pandas as pd

class Strategy4sma_porcentaje(Strategy):
    # x = [ 0=> len_sma1, 
    #       1=> len_sma2,
    #       2=> len_sma3,
    #       3=> len_sma4,
    #       4=> factor_swl,
    #       5=> factor_sll,
    #       6=> factor_sws,
    #       7=> factor_sls]
    # x = np.array([0,0,0,0,0,0])

    def init(self):
        data = {
            'high': pd.Series(self.data.High),
            'low':  pd.Series(self.data.Low),
            'close':pd.Series(self.data.Close),
        }        
        self.sma1 = self.I(SMA,data,self.x[0])
        self.sma2 = self.I(SMA,data,self.x[1])
        self.sma3 = self.I(SMA,data,self.x[2])
        self.sma4 = self.I(SMA,data,self.x[3])

    def next(self):
        # OPEN POS
        if not self.position.is_long and not self.position.is_short:
            # LONG 
            
            if self.sma1[-2]<=self.sma2[-2] and self.sma1[-1]>self.sma2[-1]:
                self.buy()
                self.max_in_long = self.data.Close[-1]
                self.stop_win_long  = self.data.Close[-1]*self.x[4]
                self.stop_loss_long = self.data.Close[-1]*self.x[5]
            # SHORT
            elif self.sma3[-2]>=self.sma4[-2] and self.sma3[-1]<self.sma4[-1]:
                self.sell()
                self.min_in_short = self.data.Close[-1]
                self.stop_win_short  = self.data.Close[-1]*self.x[6]
                self.stop_loss_short = self.data.Close[-1]*self.x[7]

        # IN POS LONG
        elif self.position.is_long:
            # subir stop loss long
            if self.data.Close[-1] > self.max_in_long: 
                self.max_in_long = self.data.Close[-1]
                self.stop_loss_long = self.data.Close[-1]*self.x[5]

            # close pos long
            if (self.data.Close[-1]>self.stop_win_long) or (self.data.Close[-1]<self.stop_loss_long):
                self.position.close()

        # IN POS SHORT
        elif self.position.is_short:
            # bajar stop loss short
            if self.data.Close[-1] < self.min_in_short:
                self.min_in_short = self.data.Close[-1]
                self.stop_loss_short = self.data.Close[-1]*self.x[7]
            # close pos short
            if (self.data.Close[-1]<self.stop_win_short) or (self.data.Close[-1]>self.stop_loss_short):
                self.position.close()