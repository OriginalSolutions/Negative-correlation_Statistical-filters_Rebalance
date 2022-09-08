#!/usr/bin/env python3.8
from pybit import spot
from datetime import datetime
import time
import pandas as pd # do wyświetlenia serii danych i obliczeń statystychnych
import numpy as np # skumulowana suma
import matplotlib
import matplotlib.pyplot as plt
#
import pylab

####################################################
session_unauth = spot.HTTP(endpoint="https://api.bybit.com")
####################################################

interval = "1m"   
symbol_long = "BTC3LUSDT" 
symbol_short ="BTC3SUSDT"


# symbol_long = "LTC2LUSDT",
# symbol_short = "LTC2SUSDT",
# symbol_long = "FTM2LUSDT",
# symbol_short = "FTM2SUSDT",

# symbol_long = "LINK2LUSDT",  ####  SUPER WYNIKI 
# symbol_short = "LINK2SUSDT",

# symbol_long = "APE2LUSDT",
# symbol_short = "APE2SUSDT"

# symbol_long = "ETH3LUSDT",
# symbol_short = "ETH3SUSDT"


# symbol_long = "BTCUSDT" 
# # symbol_short ="LINKUSDT"  #    * -1
# symbol_short ="XRPUSDT"     #    * -1

##############################################################################################
#  PARAMETRY  STRATEGIA 
##############################################################################################
range_log = 4   # dla 1h = 550    # dla 30m = 250       #  dla 1m = 4,  8, 16,  !!! 32 !!!          #  [ 1m = 4  (dla strategii mieszanej:  BTC  i  LINK)  oraz MINUS_STD (4.6 * (0.9 * PLUS_STD)) ]

invested_capital = int(200)  # $
indicator_balancing = float(1.0)  # od  0.35  do  0.5 - według autorskiego algorytmu


##############################################################################################
#  IMPORT  DANYCH  
##############################################################################################

LONG = session_unauth.query_kline(
    symbol=symbol_long,
    interval=interval
)


klines_L = LONG['result']
close_long =list()

for kline in klines_L:
    close_long.append(float(kline[4])) 

#####################################################

SHORT = session_unauth.query_kline(
    symbol=symbol_short,
    interval=interval
)


klines_S = SHORT['result']
close_short = list()

for kline in klines_S:
    close_short.append(float(kline[4]))




##############################################################################################
#  OBLICZANIE BALANCU  DLA  POSZCZEGÓLNYCH  TOKENÓW
##############################################################################################

i=0   
balance_long = list()

time_balance_long = list()


while i <= len(close_long)-1:
    if i==0:
        balance_long.append((invested_capital/2))
        #
        time_balance_long.append(datetime.fromtimestamp(round(LONG['result'][i][0]) / 1000).strftime("%Y-%m-%d %H:%M:%S"))  # SPOT
        #
    else:
        balance_long.append((invested_capital/2) * (float(close_long[i]/close_long[0])))    #  wyrażone  w  ilorazie
        #
        time_balance_long.append(datetime.fromtimestamp(round(LONG['result'][i][0]) / 1000).strftime("%Y-%m-%d %H:%M:%S"))  # SPOT
        #
    i+=1
    
    

# print( " balance_long = " f'{balance_long}' )
# print(len(balance_long))
print("   "*100)

#####################################################



i=0  
balance_short = list()

time_balance_short = list()



while i <= len(close_short)-1:
    if i==0:
        balance_short.append((invested_capital/2))
        #
        time_balance_short.append(datetime.fromtimestamp(round(SHORT['result'][i][0]) / 1000).strftime("%Y-%m-%d %H:%M:%S"))  
        #
    else:
        balance_short.append((invested_capital/2) * (float(close_short[i]/close_short[0])))     #  wyrażone  w   $
        #
        time_balance_short.append(datetime.fromtimestamp(round(SHORT['result'][i][0]) / 1000).strftime("%Y-%m-%d %H:%M:%S"))  
        #
    i+=1



# print( " balance_short = " f'{balance_short}' )
# print(len(balance_short))
print("   "*100)




#########################################################################
# OBLICZANIE  CAŁKOWITEJ WARTOŚĆI PORTFELA    (WZGLĘDEM PIERWSZEJ CENY ZAMKNIĘCIA)
#########################################################################

i=0
balance = list()

while i <= len(balance_short)-1: 
    balance.append(float(balance_short[i] + balance_long[i]))                    #  dodawanie zysków lub strat  ( short + long )
    i+=1


# print(" balance = " f'{balance}')



#########################################################################
# OBLICZANIE  CAŁKOWITEJ WARTOŚĆI PORTFELA    -  DODANIE INDEXU CZASU 
#########################################################################

log=0
timeseries_log = dict()

while log <= len(balance)-1:           
    timeseries_log[datetime.fromtimestamp(round(LONG['result'][log][0]) / 1000).strftime("%Y-%m-%d %H:%M:%S")] = balance[log]  # SPOT
    log+=1




#########################################################################
# OBLICZANIE DANYCH STATYSTYCZNYCH 
#########################################################################


ts_log =  pd.Series(timeseries_log)
statistyc_log = ts_log.describe()

print("--"*20)
print("STATYSTYKA SKŁADANEGO PROCENTU")
print(statistyc_log)
print("--"*20)




time_log  = ts_log.index                                      # tylko   czas,   bez indeksu danych 
data_log = ts_log.reset_index(drop=True)           # tylko   dane,   bez indeksu czasu     -    cała kowita wartość portfela  (nie uwzględniająca prowizji)




# print(balance[0:10])
# # ts_log =  pd.Series(balance[0:10])
# print(pd.Series(balance[0:10]).describe()[1]) # MA
# print(pd.Series(balance[0:10]).describe()[2]) # STD






print(" " * 50)
# print("data_log - bez indexu czasu =  " f'{data_log}')
print(" " * 50)

# print(" timeseries_log =  " f'{timeseries_log}' )
# print(" " * 50)
# print("  czas  LONG =  " f'{klines_L}' )



pylab.plot(time_log, data_log) 
pylab.title('WYKRES ZAMIANY WARTOŚĆI CAŁEGO PORTFELA WZGLĘDEM PIERWSZEJ WARTOŚCI')  
pylab.grid(True)
pylab.show()




#########################################################################
#  OBLICZANIE ŚREDNICH KROCZĄCYCH   ( NA PODSTAWIE WSZEŚNIEJ OBLICZONYCH DANYCH STATYSTYCZNYCH )
#########################################################################


s_log=0
MA_log = dict()
MSTD_log= dict()




while s_log <= len(ts_log)-range_log:  
    MA_log[s_log+range_log] = ts_log[s_log:s_log+range_log].describe()[1]          # krocząca  średnia
    MSTD_log[s_log+range_log] = ts_log[s_log:s_log+range_log].describe()[2]     # krączące  jedno  odchylenia standardowe
    s_log+=1
    
    
    
    

print(" " * 50)
# print("  MA_log = " f'{MA_log}' )
# print(" " * 50)
# print("  MSTD_log = " f'{MSTD_log}' )




#########################################################################
#  OBLICZANIE ŚREDNICH KROCZĄCYCH  c.d.
#########################################################################


ma_log = list()
std_plus_log = list()
std_minus_log = list()
multiplier_plus_log = float(2.6)   #  0.9 !    #  float(1.2)       #  dla: 1h = 2.5     # dla 5m = 1.55       #  dla  1m  =   1.05        #  bezpieczne:    0.4
multiplier_minus_log =  1.0 * multiplier_plus_log  #  1.6 !   #  1.3     #  dla   30m i 1h  = 2        #  dla  1m  =   1.1    #  bezpieczne:   5.93 
m_log = 0





#  for data_log[m_log] in data_log:   
#
for balance[m_log] in balance:    
    #
    if int(m_log) <= int(range_log-1):  ###    a może:   ... int(range_log - 2)    ?????????????????
        #
        ma_log.append((data_log[m_log]-data_log[m_log]) + invested_capital)        
        std_plus_log.append((data_log[m_log]-data_log[m_log]) + invested_capital)
        std_minus_log.append((data_log[m_log]-data_log[m_log]) + invested_capital)
        m_log+=1
        #
        # print("  m_log = " f'{m_log}')
        # print("  range_log-1 = " f'{range_log-1}')    
        #
    else:
        #
        ma_log.append((data_log[m_log]-data_log[m_log]) + MA_log[m_log])
        std_plus_log.append((data_log[m_log]-data_log[m_log]) + (MA_log[m_log]+(MSTD_log[m_log]*multiplier_plus_log)))
        std_minus_log.append((data_log[m_log]-data_log[m_log]) + (MA_log[m_log]-(MSTD_log[m_log]*multiplier_minus_log)))
        m_log+=1
        if m_log == len(balance)+1:
            break





pylab.plot(time_log,data_log)  
pylab.plot(time_log,ma_log)
pylab.plot(time_log,std_plus_log)
pylab.plot(time_log,std_minus_log)   #   SPOT


# print("  ma_log = " f'{ma_log}')
# print("  std_plus_log = " f'{std_plus_log}')
# print("  std_minus_log = " f'{std_minus_log}')


pylab.title('WYKRES ZAMIANY WARTOŚĆI CAŁEGO PORTFELA WZGLĘDEM PIERWSZEJ WARTOŚCI + FILTR STATYSTYCZNY')
pylab.grid(True)
pylab.show()





#########################################################################
#  OBLICZANIE ZYSKU   BRUTTO  -  bez prowizji
#########################################################################

buy = list()
buy_minus_commission = list()
profit_from_one_transaction_log = list()  #  bez  uwzględniania  prowizji
profit_net_from_one_transaction_log = list()  #  po uwzględniania  prowizji
b=range_log
commission = float(0.001)  #  0.1 procenta


time_buy = list()
time_sell = list()


# buy_and_sell_balanc = list()






while b <= len(data_log)-1:
    #
    if data_log[b] < std_minus_log[b] and len(buy) == 0:  
        #
        print("  data_log[b] = " f'{data_log[b]}')
        print("  balance[b] = " f'{balance[b]}')
        print("  balance_long[b] = " f'{balance_long[b]}')
        print("  balance_short[b] = " f'{balance_short[b]}')
        print(" KONIEC  KUPNA")
        print("  "*30)
        # print("  std_minus_log[b] = " f'{std_minus_log[b]}')
        #
        # buy_and_sell_balanc.append(data_log[b]) 
        #
        buy_minus_commission.append(data_log[b] - (data_log[b] * commission))      # wartość  całego portfela (long+short)  po uwzględnieniu prowizji
        #
        #
        buy.append(data_log[b])     #  bez prowizji
        #print("  buy  =   " f'{buy}' )
        #
        time_buy.append(time_log[b])  
        #
        #
        #
    elif data_log[b] > std_plus_log[b] and len(buy_minus_commission) == 1 and len(buy) == 1:  #  Po uwzględnieniu prowizji 
        #
        print("  data_log[b] = " f'{data_log[b]}')
        print("  balance[b] = " f'{balance[b]}')
        print("  balance_long[b] = " f'{balance_long[b]}')
        print("  balance_short[b] = " f'{balance_short[b]}')
        print(" KONIEC  SPRZEDAŻY")
        print("  "*30)
        #
        # buy_and_sell_balanc.append(data_log[b]) 
        #
        #
        balance_gross = (buy_minus_commission[0] * (data_log[b]/buy[0]))
        profit_net_from_one_transaction_log.append(balance_gross - (balance_gross * commission) - buy[0])   # po uwzględnieniu prowizji 
        #
        #
        profit_from_one_transaction_log.append(data_log[b] - buy[0])   #  bez  uwzględniania  prowizji
        #
        #
        del(buy[0])
        del(buy_minus_commission[0])
        #
        time_sell.append(time_log[b]) 
        #
        #
    b+=1
   
   
   
print("GŁÓWNA  STRATEGIA")
print("  time_buy = " f'{time_buy}' )
# print("   " * 30)
print("  len(time_buy) = " f'{len(time_buy)}' )
print("   " * 30 )
print("  time_sell = " f'{time_sell}' )
print("  len(time_sell) = " f'{len(time_sell)}' )




print("  "*20)
print(" PROFIT  FROM  ONE  TRANSACTION ")
print(profit_from_one_transaction_log)

profit =  pd.Series(profit_from_one_transaction_log, dtype='object')
cumsum_profit = profit.cumsum()

print("CUMSUM PROFIT BRUTTO")
print(cumsum_profit)

print("  "*20)
print("estimated commission value")
len_profit = int(len(cumsum_profit))
print(len_profit * 2 * commission * invested_capital)



#########################
# NETTO
#########################

print("  "*20)
print(" PROFIT  NET  FROM  ONE  TRANSACTION ")
print(profit_net_from_one_transaction_log)


profit_net =  pd.Series(profit_net_from_one_transaction_log, dtype='object')
cumsum_profit_net = profit_net.cumsum()


print("CUMSUM PROFIT NETTO")
print(cumsum_profit_net)




############################################################################################################################
############################################################################################################################
############################################################################################################################
#
#
#
######    BALANCING   START   #######   
#
######    BALANCING  względem interwału poprzedniego
######    BALANCING  z otwieraniem pozycji według  ILORAZU  a nie jak wyżej   różnicy balancu
#
#
#


# long_capital_before_balancing = list()
# short_capital_before_balancing = list()  # kapitał zgromadzony  przed  rebelansing-iem

# long_capital_before_balancing.append(invested_capital/2)
# short_capital_before_balancing.append(invested_capital/2)



long_capital_before_balancing = list()
short_capital_before_balancing = list() # kapitał zgromadzony przed rebelans

# long_capital_before_balancing.append(invested_capital/2)
# long_capital_before_balancing.append(invested_capital/2)



long_capital_after_balancing = list()
short_capital_after_balancing = list()  # kapitał zgromadzony po rebelans

long_capital_after_balancing.append(invested_capital/2)
short_capital_after_balancing.append(invested_capital/2)




profit_long = list()
profit_short = list()


buy_long = list()
buy_short = list()

# net_profit_balancing = list()

b = range_log
commission = float(0.001)  #   0.1 %
i = 0
j = 1




time_buy_long = list()
time_buy_short = list()

time_sell_long = list()
time_sell_short = list()






time_buy_long.append(time_balance_long[b]) #  do wstawienia w pętli
time_buy_short.append(time_balance_short[b])

time_sell_long.append(time_balance_long[b])
time_sell_short.append(time_balance_short[b])



buy_and_sell_balanc_long_plus_short = list()






while b <= len(data_log)-1:
    #
    #
    if data_log[b] < std_minus_log[b] and len(buy_long) == 0 and len(buy_short) == 0:   #  KUPUJ
        print("  balance_long[b] = " f'{balance_long[b]}')
        print("  balance_short[b] = " f'{balance_short[b]}')
        print(" KONIEC  KUPNA")
        #
        #
        #
        buy_and_sell_balanc_long_plus_short.append(balance_long[b] + balance_short[b])
        #
        #
        #
        # buy_long.append( balance_long[b] - ( balance_long[b] * commission) ) 
        # buy_short.append( balance_short[b] - ( balance_short[b] * commission) ) 
        #
        # 
        buy_long.append( balance_long[b] ) 
        buy_short.append( balance_short[b] ) 
        #
        #
        time_buy_long.append(time_balance_long[b]) 
        time_buy_short.append(time_balance_short[b])
        #
        #
        ############ ########### ########### ########### ###########
        # print(" buy_long = " f'{buy_long}' )
        # print(" buy_short = " f'{buy_short}' )
        # print(" KONIEC   KUPNA ")
        # print("  "*30)
        ############ ########### ########### ########### ###########
        #
        #
        #
    elif data_log[b] > std_plus_log[b] and len(buy_long) == 1 and len(buy_short) == 1:   #  SPRZEDAWAJ
        print("  balance_long[b] = " f'{balance_long[b]}')
        print("  balance_short[b] = " f'{balance_short[b]}')
        print(" KONIEC  SPRZEDAŻY")
        #
        #
        #
        buy_and_sell_balanc_long_plus_short.append(balance_long[b] + balance_short[b])
        #
        #
        #
        # print(" buy_long[0]  = " f'{buy_long[0]}' )
        # print(" buy_short[0]  = " f'{buy_short[0]}' )
        #
        # profit_long.append( (balance_long[b] - (balance_long[b] * commission)) - buy_long[0] )
        # profit_short.append( (balance_short[b] - (balance_short[b] * commission)) - buy_short[0] )
        #
        #
        # profit_long.append( (balance_long[b] - (balance_long[b] * commission)) / buy_long[0] )  #  zysk wyrażony w ilorazie, (np. 1.25)
        # profit_short.append( (balance_short[b] - (balance_short[b] * commission)) / buy_short[0] )
        #
        #
        #
        #
        #
         ############ ########### ########### ########### ###########
        # print(" balance_long[b]  = " f'{balance_long[b]}' )
        # print(" balance_short[b] = " f'{balance_short[b]}' )
        # print(" KONIEC   SPRZEDAŻY ")
        # print("  "*30)
        ############ ########### ########### ########### ###########
        #
        #
        #
        profit_long.append( balance_long[b] / buy_long[len(buy_long)-1] )
        profit_short.append( balance_short[b] / buy_short[len(buy_short)-1] )
        print( "  profit_long[len(profit_long)-1]    =   " f'{profit_long[len(profit_long)-1]}' )
        print( "  profit_short[len(profit_short)-1]  = " f'{profit_short[len(profit_short)-1]}' )
        print("  " * 100)
        #
        #
        # profit_long.append( ( ((buy_long[len(buy_long)-1] - (buy_long[len(buy_long)-1]*commission)) * (balance_long[b] / buy_long[len(buy_long)-1])) / buy_long[len(buy_long)-1])-(commission*(((buy_long[len(buy_long)-1]-(buy_long[len(buy_long)-1]*commission))*(balance_long[b]/buy_long[len(buy_long)-1])) / buy_long[len(buy_long)-1] ) ) )  #  zysk wyrażony w ilorazie, (np. 1.25)
        # #
        # #
        # profit_short.append( ( ( (buy_short[len(buy_short)-1] - (buy_short[len(buy_short)-1] * commission)) * (balance_short[b] / buy_short[len(buy_short)-1])) / buy_short[len(buy_short)-1])-(commission*(((buy_short[len(buy_short)-1] -  (buy_short[len(buy_short)-1] * commission)) * (balance_short[b] / buy_short[len(buy_short)-1])) / buy_short[len(buy_short)-1] ) ) )  # zysk wyrażony w ilorazie, (np. 1.25)
        #
        ###   liczby dążą do granic - niskończoność ####  BŁĄD 
        # ########### ########### ########### ########### ########### ########### ########### ###########
        #
        #
        #
        # del(buy_long[0])  
        # del(buy_short[0]) # przeniosłem na koniec
        #
        #
        #
        #
        # time_sell_long.append(time_balance_long[b])
        # time_sell_short.append(time_balance_short[b])
        #
        #
        #
        #
        # if profit_long[len(profit_long)-1] >= 0 and profit_long[len(profit_long)-1 > profit_short[len(profit_short)-1]:
        if profit_long[len(profit_long)-1] >= 1 and profit_long[len(profit_long)-1] > profit_short[len(profit_short)-1]:
            #
            #
            #
            # buy_and_sell_balanc_long_plus_short.append(balance_long[b] + balance_short[b])
            #
            #
            #
            # print(" profit_long[len(profit_long)-1]  = " f'{profit_long[len(profit_long)-1]}' )
            # long_capital_after_balancing.append( long_capital_after_balancing[j-1]  + ((profit_long[len(profit_long)-1]) * (int(1) - indicator_balancing)) )
            # short_capital_after_balancing.append( (short_capital_after_balancing[j-1] + profit_short[len(profit_short)-1]) + (profit_long[len(profit_long)-1] * indicator_balancing))   #   włącznie  z  stratą  shorta
            #
            #
            #
            ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### 
            long_capital_before_balancing.append( long_capital_after_balancing[j-1]  * profit_long[len(profit_long)-1] )   #  wyrażony w  $ 
            long_capital_after_balancing.append( long_capital_after_balancing[j-1]  * (1 + ( (profit_long[len(profit_long)-1] - 1) * (int(1) - indicator_balancing) )) )  # OK 
            #
            #
            # print(" LONG_capital_after_balancing[ j - 1 ]   = " f'{long_capital_after_balancing[j-1]}')
            # print(" profit_long[len(profit_short)-1]   = " f'{profit_long[len(profit_short)-1]}')
            
            # long_capital_after_balancing.append( long_capital_after_balancing[j-1]  * profit_long[len(profit_long)-1] ) 
            ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### 
            #
            #
            #
            # print(long_capital_before_balancing)
            # print(long_capital_after_balancing)
            # print(j)
            #
            #
            #
            ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### 
            short_capital_after_balancing.append( (short_capital_after_balancing[j-1] * profit_short[len(profit_short)-1]) + (((long_capital_before_balancing[len(long_capital_before_balancing)-1] - long_capital_after_balancing[j])) ))    #    ....................    * indicator_balancing))   # ??  .......  ???? 
            #
            #
            # print(" SHORT_capital_after_balancing[ j - 1 ]   = " f'{short_capital_after_balancing[j-1]}')
            # print(" profit_short[len(profit_short)-1]   = " f'{profit_short[len(profit_short)-1]}')            
            # #
            # short_capital_after_balancing.append( short_capital_after_balancing[j-1] * profit_short[len(profit_short)-1] )
            ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### 
            #
            #
            #
            time_sell_long.append(time_balance_long[b])
            time_sell_short.append(time_balance_short[b])
            #
            #
            #
            j+=1
            
        # elif profit_short[len(profit_short)-1] >= 0 and profit_short[len(profit_short)-1] > profit_long[len(profit_long)-1]:
        elif profit_short[len(profit_short)-1] >= 1 and profit_short[len(profit_short)-1] > profit_long[len(profit_long)-1]:
            #
            #
            #
            # buy_and_sell_balanc_long_plus_short.append(balance_long[b] + balance_short[b])
            #
            #
            #
            # print(" profit_short[len(profit_short)-1]  = " f'{profit_short[len(profit_short)-1]}' )
            # short_capital_after_balancing.append( short_capital_after_balancing[j-1] + ((profit_short[len(profit_short)-1]) * (int(1) - indicator_balancing)) )
            # long_capital_after_balancing.append( (long_capital_after_balancing[j-1] + profit_long[len(profit_long)-1]) + (profit_short[len(profit_short)-1] * indicator_balancing) )   # włącznie  z  stratą   longa
            #
            #
            #
            ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### 
            short_capital_before_balancing.append( short_capital_after_balancing[j-1]  * profit_short[len(profit_short)-1] )
            short_capital_after_balancing.append( short_capital_after_balancing[j-1] * (1 + ( (profit_short[len(profit_short)-1] - 1 ) * (int(1) - indicator_balancing))) ) # OK
            #
            #
            # print(" SHORT_capital_after_balancing[ j - 1 ]   = " f'{short_capital_after_balancing[j-1]}')
            # print(" profit_short[len(profit_short)-1]   = " f'{profit_short[len(profit_short)-1]}')
            # #
            # short_capital_after_balancing.append( short_capital_after_balancing[j-1] * profit_short[len(profit_short)-1] )
            ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### 
            #
            #
            #
            # print(short_capital_before_balancing)
            # print(short_capital_after_balancing)
            # print(j)
            #
            #
            #
            ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### 
            long_capital_after_balancing.append( (long_capital_after_balancing[j-1] * profit_long[len(profit_long)-1] ) + (((short_capital_before_balancing[len(short_capital_before_balancing)-1] - short_capital_after_balancing[j]))  ))   #   ..................  * indicator_balancing) )   # ??  ...... ???? 
            #
            #
            # print(" LONG_capital_after_balancing[ j - 1 ]   = " f'{long_capital_after_balancing[j-1]}')
            # print(" profit_long[len(profit_short)-1]   = " f'{profit_long[len(profit_short)-1]}')
            # #
            # long_capital_after_balancing.append( long_capital_after_balancing[j-1]  * profit_long[len(profit_long)-1] )  # OK
            ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ###########             
            #
            #
            #
            time_sell_long.append(time_balance_long[b])
            time_sell_short.append(time_balance_short[b])
            #
            #
            #
            j+=1
            #
        elif profit_long[len(profit_long)-1] == profit_short[len(profit_short)-1]:    #  w ilorazie 
            #
            #
            #
            # buy_and_sell_balanc_long_plus_short.append(balance_long[b] + balance_short[b])
            #
            #
            #
            short_capital_after_balancing.append( short_capital_after_balancing[j-1] * profit_short[len(profit_short)-1] )
            #
            ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ###########  
            # print(" SHORT_capital_after_balancing[ j - 1 ]   = " f'{short_capital_after_balancing[j-1]}')
            # print(" profit_short[len(profit_short)-1]   = " f'{profit_short[len(profit_short)-1]}')
            ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ###########  
            #
            #
            #
            long_capital_after_balancing.append( long_capital_after_balancing[j-1] * profit_long[len(profit_long)-1] )
            #
            ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ###########  
            # print(" LONG_capital_after_balancing[ j - 1 ]   = " f'{long_capital_after_balancing[j-1]}')
            # print(" profit_long[len(profit_short)-1]   = " f'{profit_long[len(profit_short)-1]}')
            ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ###########  
            #
            #
            #
            time_sell_long.append(time_balance_long[b])
            time_sell_short.append(time_balance_short[b])
            #
            #
            #
        elif profit_long[len(profit_long)-1] < 1 and profit_short[len(profit_short)-1] < 1: 
            #
            #
            short_capital_after_balancing.append( short_capital_after_balancing[j-1] * profit_short[len(profit_short)-1] )
            #
            #
            ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ###########  
            # print(" SHORT_capital_after_balancing[ j - 1 ]   = " f'{short_capital_after_balancing[j-1]}')
            # print(" profit_short[len(profit_short)-1]   = " f'{profit_short[len(profit_short)-1]}')
            ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ###########  
            #
            #
            #
            long_capital_after_balancing.append( long_capital_after_balancing[j-1] * profit_long[len(profit_long)-1] )
            #
            #
            ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ###########  
            # print(" LONG_capital_after_balancing[ j - 1 ]   = " f'{long_capital_after_balancing[j-1]}')
            # print(" profit_long[len(profit_short)-1]   = " f'{profit_long[len(profit_short)-1]}')
            ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ########### ###########  
            #
            #
            #
            time_sell_long.append(time_balance_long[b])
            time_sell_short.append(time_balance_short[b])
            #
            j+=1
            #
            #
        del(buy_long[0]) 
        del(buy_short[0]) 
    # 
    #    
    b+=1
    i+=1 


    
    
print(" " * 30)
print("short_capital_after_balancing  = " f'{short_capital_after_balancing}' )
print(" " * 30)
print("  len(short_capital_after_balancing)  = " f'{len(short_capital_after_balancing)}' )
print(" " * 30)
print("long_capital_after_balancing  = " f'{long_capital_after_balancing}' )
print(" " * 30)
print("  len(long_capital_after_balancing)  = " f'{len(long_capital_after_balancing)}' )
print(" " * 30)


print("CZAS  KUPNA  balance LONG and  SHORT")
print(time_buy_long)
print(len(time_buy_long))
print(time_buy_short)
print(len(time_buy_short))
print(" " * 30)

print("CZAS  SPRZEDAŻY  balance LONG and  SHORT")
print(time_sell_long)
print(len(time_sell_long))
print(time_sell_short)
print(len(time_sell_short))
print(" " * 30)

######    BALANCING   END   #######
# END