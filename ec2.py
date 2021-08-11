#!/usr/bin/env python3

import math
import random
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
from pandas_datareader import data as pdr
import sys
import random
import time
import json


def fetch_data():
    
    # override yfinance with pandas – seems to be a common step
    yf.pdr_override()

    # Get stock data from Yahoo Finance – here, asking for about 10 years of Amazon
    today = date.today()
    decadeAgo = today - timedelta(days=3652)

    data = pdr.get_data_yahoo('AMZN', start=decadeAgo, end=today).reset_index()
    # Other symbols: CSCO – Cisco, NFLX – Netflix, INTC – Intel, TSLA - Tesla
    # print(data)
    data["Date"] = data["Date"].apply(lambda x: pd.Timestamp(x).date().strftime('%m/%d/%Y'))


    # Add two columns to this to allow for Buy and Sell signals
    # fill with zero
    data['Buy']=0
    data['Sell']=0
    # print("*"*50)
    # print(data)
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
    
    # print("Sell: ",data.Sell.value_counts())
    # print("Buy: ",data.Buy.value_counts())
        
    return data


def ec2_risk_calculation(h,d,t):
    start = time.time()
    values=[]
    data = fetch_data()
    minhistory = h
    
    shots = d
    j=0
    for i in range(minhistory, len(data)):
        if data.Buy[i]==t: # if we’re interested in Buy signals

            # print("the date - ",data["Date"][i])
            mean=data.Close[i-minhistory:i].pct_change(1).mean()
            std=data.Close[i-minhistory:i].pct_change(1).std()
            # generate much larger random number series with same broad characteristics
            simulated = [random.gauss(mean,std) for x in range(shots)]
            # sort and pick 95% and 99%  - not distinguishing long/short here
            simulated.sort(reverse=True)
            var95 = simulated[int(len(simulated)*0.95)]
            var99 = simulated[int(len(simulated)*0.99)]
            values.append([str(data["Date"][i]),var95, var99])
            # j=j+1
            # print(j,i,var95, var99) # so you can see what is being produced


    elapsed_time = str(time.time() - start)
    
    return json.dumps({
        "values":values,
        "elapsed_time": elapsed_time,
    })



print ('# Args:', len(sys.argv))
print ('Argument List:', str(sys.argv))

print(sys.argv)
print(sys.argv[1],sys.argv[2],sys.argv[3])



sys.stdout.write(ec2_risk_calculation(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])))