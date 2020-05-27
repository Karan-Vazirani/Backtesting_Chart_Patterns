import numpy as np
import pandas as pd
import pandas_datareader.data as web
from Companies import list_of_companies
import matplotlib.pyplot as plt
pd.options.mode.chained_assignment = None

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def algorithm(stk):

    stock = web.DataReader(name=stk, data_source='yahoo', start='2018-1-1', end='2020-3-17')
    stock['Signals'] = np.zeros(len(stock.index))
    stock['Vol_Ma'] = stock.Volume.rolling(50).mean()
    stock['Above_Vol'] = stock.Volume > stock.Vol_Ma
    stock['Returns'] = np.log(stock['Close'] / stock['Open'])
    stock['Up_Day'] = stock.Close > stock.Close.shift(1)
    stock['Inside_Ranges'] = (stock.High < stock.High.shift(1)) & (stock.Low > stock.Low.shift(1))
    stock['Up_Day_Intraday'] = stock.Close > stock.Open
    stock['Down_Volume'] = stock.Volume < stock.Volume.shift(1)
    stock['Gap'] = stock.Open > stock.Close.shift(1)
    stock = stock.dropna()

    consolidation_days = 2

    days = len(stock.index) - 3

    for n in range(days):
        consolidated = stock['Inside_Ranges'].values[n: consolidation_days + n]
        #  down_volume = stock['Down_Volume'].values[n: consolidation_days + n]
        up = stock.iloc[n + 2]['Up_Day']
        up_intra = stock.iloc[n + 2]['Up_Day_Intraday']
        gap_1 = stock.iloc[n + 2]['Gap']
        gap_2 = stock.iloc[n + 3]['Gap']
        above_avg_vol = stock.iloc[n + 2]['Above_Vol']
        console = np.all(consolidated)
        #  vol = np.all(down_volume)

        if console and up and above_avg_vol and gap_1 and gap_2 and up_intra:
            open_of_day = stock.iloc[n + 3]['Open']
            stop = open_of_day + open_of_day * -.03
            if stop < stock.iloc[n + 3]['Low']:
                stock['Signals'][n + 3] = stock.iloc[n + 3]['Returns'] * 10000

            else:
                stock['Signals'][n + 3] = -.03 * 10000

    print(stk)
    print(stock.loc[stock['Signals'] != 0])
    return stock[['Signals']]


accumulated_results = algorithm('ADBE')

for chosen_stock in list_of_companies:
    ret = algorithm(chosen_stock)
    accumulated_results = accumulated_results.add(ret, fill_value=0)

accumulated_results.iloc[0] += 100000
accumulated_results['Signals'] = accumulated_results['Signals'].cumsum()

accumulated_results.plot(y='Signals')
plt.show()

