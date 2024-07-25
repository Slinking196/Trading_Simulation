import pandas_ta as ta

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
