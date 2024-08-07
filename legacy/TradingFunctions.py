from backtesting import Backtest, Strategy

import numpy as np
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# ============================
# ========= GET DATA =========
# ============================

def getDataset(route='dataset.csv',dividir=True):
    data = pd.read_csv(route)
    data = data.rename({'open':'Open',
                        'high':'High',
                        'low':'Low',
                        'close':'Close'},axis=1).drop(['volume'],axis=1)

    data = data[data['open_time']%(5*60000)==0]

    data['open_time'] = pd.DatetimeIndex( data['open_time'].apply(lambda t:datetime.fromtimestamp(t/1000)) )
    data = data.set_index('open_time')
    data = data.sort_index(ascending=True)


    # # ============================
    # # ===== TRAIN TEST SPLIT =====
    # # ============================
    
    dataset_train = data.loc[:'2022-01-01 00:00:00']
    if dividir:
        dataset_train = [g for n, g in dataset_train.groupby(pd.Grouper(freq='M'))][1:-1]           # ME en LOCAL, M en colab
    dataset_valid = data.loc['2022-01-01 00:00:00':]

    return dataset_train,dataset_valid


# ==========================================
# ============== STRATEGY ==================
# ==========================================

def SMA(data,len):
    return ta.sma(data['close'],length=len)

def ATR(data,len):
    len = int(len)
    return ta.atr(data['high'],data['low'], data['close'],length=len)

def ADX(data,len):
    len = int(len)
    return ta.adx(data['high'],data['low'], data['close'],length=len)[f'ADX_{len}']

def DMP(data,len):
    len = int(len)
    return ta.adx(data['high'],data['low'], data['close'],length=len)[f'DMP_{len}']

def DMN(data,len):
    len = int(len)
    return ta.adx(data['high'],data['low'], data['close'],length=len)[f'DMN_{len}']

# ============== 4SMA ==================

class Strategy4sma_atr_inicial(Strategy):
    # x = [ 0=> len_sma1, 
    #       1=> len_sma2,
    #       2=> len_sma3,
    #       3=> len_sma4,
    #       4=> len_atr 
    #       5=> factor_swl,
    #       6=> factor_sll,
    #       7=> factor_sws,
    #       8=> factor_sls]
    x = np.array([0,0,0,0,0,0])

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
        self.atr =  self.I(ATR,data,self.x[4])

    def next(self):
        # OPEN POS
        if not self.position.is_long and not self.position.is_short:
            # LONG 
            if self.sma1[-2]<=self.sma2[-2] and self.sma1[-1]>self.sma2[-1]:
                self.buy()
                self.max_in_long = self.data.Close[-1]
                self.stop_win_long =   self.data.Close[-1]+self.atr[-1]*self.x[5]
                self.delta_loss_long = self.atr[-1]*self.x[6]
            # SHORT
            elif self.sma3[-2]>=self.sma4[-2] and self.sma3[-1]<self.sma4[-1]:
                self.sell()
                self.min_in_short = self.data.Close[-1]
                self.stop_win_short  =  self.data.Close[-1]-self.atr[-1]*self.x[7]
                self.delta_loss_short = self.atr[-1]*self.x[8]

        # IN POS LONG
        elif self.position.is_long:
            # subir stop loss long
            if self.data.Close[-1] > self.max_in_long: 
                self.max_in_long = self.data.Close[-1]
            # close pos long
            if (self.data.Close[-1]>self.stop_win_long) or (self.data.Close[-1]<(self.max_in_long-self.delta_loss_long) ):
                self.position.close()

        # IN POS SHORT
        elif self.position.is_short:
            # bajar stop loss short
            if self.data.Close[-1] < self.min_in_short:
                self.min_in_short = self.data.Close[-1]
            # close pos short
            if (self.data.Close[-1]<self.stop_win_short) or (self.data.Close[-1]>(self.min_in_short+self.delta_loss_short)):
                self.position.close()


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

# ============== 2SMA ==================

class Strategy2sma_atr_inicial(Strategy):
    # x = [ 0=> len_sma1, 
    #       1=> len_sma2,
    #       2=> len_atr 
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
        self.sma1 = self.I(SMA,data,self.x[0])
        self.sma2 = self.I(SMA,data,self.x[1])
        self.atr =  self.I(ATR,data,self.x[2])

    def next(self):
        # OPEN POS
        if not self.position.is_long and not self.position.is_short:
            # LONG 
            if self.sma1[-2]<=self.sma2[-2] and self.sma1[-1]>self.sma2[-1]:
                self.buy()
                self.max_in_long = self.data.Close[-1]
                self.stop_win_long =   self.data.Close[-1]+self.atr[-1]*self.x[3]
                self.delta_loss_long = self.atr[-1]*self.x[4]
            # SHORT
            elif self.sma1[-2]>=self.sma2[-2] and self.sma1[-1]<self.sma2[-1]:
                self.sell()
                self.min_in_short = self.data.Close[-1]
                self.stop_win_short  =  self.data.Close[-1]-self.atr[-1]*self.x[5]
                self.delta_loss_short = self.atr[-1]*self.x[6]

        # IN POS LONG
        elif self.position.is_long:
            # subir stop loss long
            if self.data.Close[-1] > self.max_in_long: 
                self.max_in_long = self.data.Close[-1]
            # close pos long
            if (self.data.Close[-1]>self.stop_win_long) or (self.data.Close[-1]<(self.max_in_long-self.delta_loss_long) ):
                self.position.close()

        # IN POS SHORT
        elif self.position.is_short:
            # bajar stop loss short
            if self.data.Close[-1] < self.min_in_short:
                self.min_in_short = self.data.Close[-1]
            # close pos short
            if (self.data.Close[-1]<self.stop_win_short) or (self.data.Close[-1]>(self.min_in_short+self.delta_loss_short)):
                self.position.close()
        
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
            # SHORT
            elif self.sma1[-2]>=self.sma2[-2] and self.sma1[-1]<self.sma2[-1]:
                self.sell()
                self.min_in_short = self.data.Close[-1]
                self.stop_win_short  = self.data.Close[-1]*self.x[4]
                self.stop_loss_short = self.data.Close[-1]*self.x[5]

        # IN POS LONG
        elif self.position.is_long:
            # subir stop loss long
            if self.data.Close[-1] > self.max_in_long: 
                self.max_in_long = self.data.Close[-1]
                self.stop_loss_long = self.data.Close[-1]*self.x[3]
            # close pos long
            if (self.data.Close[-1]>self.stop_win_long) or (self.data.Close[-1]<self.stop_loss_long):
                self.position.close()

        # IN POS SHORT
        elif self.position.is_short:
            # bajar stop loss short
            if self.data.Close[-1] < self.min_in_short:
                self.min_in_short = self.data.Close[-1]
                self.stop_loss_short = self.data.Close[-1]*self.x[5]
            # close pos short
            if (self.data.Close[-1]<self.stop_win_short) or (self.data.Close[-1]>self.stop_loss_short):
                self.position.close()
        
# ============= SUPER ==================
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


# ==========================================
# ============== OBJECTIVE==================
# ==========================================


# def objective(sol,data):
#     scores = []
#     for periodo in data:
#         # bt = Backtest(periodo, SuperStategy,cash=1e6, commission=.0005,exclusive_orders=True)
#         bt = Backtest(periodo, Strategy4sma_porcentaje,cash=1e6, commission=.0005,exclusive_orders=True)
#         output = bt.run(x = sol)
#         scores.append( 1+output['Return [%]']/100 )

#     return -np.mean(scores),np.std(scores)


def objective(sol,data):
    scores = []
    trade_durations = []
    for periodo in data:
        # bt = Backtest(periodo, SuperStategy,cash=1e6, commission=.0005,exclusive_orders=True)
        bt = Backtest(periodo, Strategy4sma_porcentaje,cash=1e6, commission=.0005,exclusive_orders=True)
        output = bt.run(x = sol)
        scores.append( 1+output['Return [%]']/100 )
        try:        trade_durations.append( output['Max. Trade Duration'].total_seconds() )
        except:     trade_durations.append(10000000)

    trade_duration_constraint = float( np.max(trade_durations) - 5*24*60*60 )
    return -np.mean(scores),np.std(scores), trade_duration_constraint
