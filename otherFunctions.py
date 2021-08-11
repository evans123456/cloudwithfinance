#!/usr/bin/env python3
import pandas as pd
import math
from datetime import date, timedelta
from pandas_datareader import data as pdr
import yfinance as yf


def fetchFinance(company):
    
    # override yfinance with pandas – seems to be a common step
    yf.pdr_override()

    # Get stock data from Yahoo Finance – here, asking for about 10 years of Amazon
    today = date.today()
    decadeAgo = today - timedelta(days=3652)

    data = pdr.get_data_yahoo(company, start=decadeAgo, end=today).reset_index()
    # Other symbols: CSCO – Cisco, NFLX – Netflix, INTC – Intel, TSLA - Tesla
    data["Date"] = data["Date"].apply(lambda x: pd.Timestamp(x).date().strftime('%m/%d/%Y'))


    # Add two columns to this to allow for Buy and Sell signals
    # fill with zero
    data['Buy']=0
    data['Sell']=0

    # Find the 4 different types of signals – uncomment print statements
    # if you want to look at the data these pick out in some another way
    for i in range(len(data)):
        # Hammer
        realbody=math.fabs(data.Open[i]-data.Close[i])
        bodyprojection=0.1*math.fabs(data.Close[i]-data.Open[i])

        if data.High[i] >= data.Close[i] and data.High[i]-bodyprojection <= data.Close[i] and data.Close[i] > data.Open[i] and data.Open[i] > data.Low[i] and data.Open[i]-data.Low[i] > realbody:
            data.at[data.index[i], 'Buy'] = 1
            # print("H", data.Open[i], data.High[i], data.Low[i], data.Close[i])

        # Inverted Hammer
        if data.High[i] > data.Close[i] and data.High[i]-data.Close[i] > realbody and data.Close[i] > data.Open[i] and data.Open[i] >= data.Low[i] and data.Open[i] <= data.Low[i]+bodyprojection:
            data.at[data.index[i], 'Buy'] = 1
            # print("I", data.Open[i], data.High[i], data.Low[i], data.Close[i])

        # Hanging Man
        if data.High[i] >= data.Open[i] and data.High[i]-bodyprojection <= data.Open[i] and data.Open[i] > data.Close[i] and data.Close[i] > data.Low[i] and data.Close[i]-data.Low[i] > realbody:
            data.at[data.index[i], 'Sell'] = 1
            # print("M", data.Open[i], data.High[i], data.Low[i], data.Close[i])

        # Shooting Star
        if data.High[i] > data.Open[i] and data.High[i]-data.Open[i] > realbody and data.Open[i] > data.Close[i] and data.Close[i] >= data.Low[i] and data.Close[i] <= data.Low[i]+bodyprojection:
            data.at[data.index[i], 'Sell'] = 1
            # print("S", data.Open[i], data.High[i], data.Low[i], data.Close[i])
        
    return data



def calculate_row_average(dd):
    print(len(dd))
    averaged = []
    no_resources = len(dd)
    for index,item in enumerate(zip(*dd)):
        print("*"*50)
        print(item)
        sum95 =0
        sum99 =0
        for i in item:
            print(i)
            sum95 = sum95 + i[1]
            sum99 = sum99 + i[2]
        print("Ave: ",[i[0],sum95/no_resources,sum99/no_resources])
        averaged.append([i[0],sum95/no_resources,sum99/no_resources])
    return averaged