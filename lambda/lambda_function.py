import json
import math
import random
from datetime import date, timedelta
import pickle
import base64

def lambda_handler(event, context):
    minhistory = 200
    shots = 100000
    j=0
    print(event["data"])
    print(event["H"])
    print(event["D"])
    print(event["T"])
    data = event["data"]
    h = event["H"]
    d = event["D"]
    t = event["T"]


    data = bytes(data,'utf-8')
    
    data = pickle.loads(base64.b64decode(data)) 

    confidence_values = []
    for i in range(minhistory, len(data)):
        if data.Buy[i]==1: # if we’re interested in Buy signals
    
    
            mean=data.Close[i-minhistory:i].pct_change(1).mean()
            std=data.Close[i-minhistory:i].pct_change(1).std()
            # generate much larger random number series with same broad characteristics
            simulated = [random.gauss(mean,std) for x in range(shots)]
            # sort and pick 95% and 99%  - not distinguishing long/short here
            simulated.sort(reverse=True)
            var95 = simulated[int(len(simulated)*0.95)]
            var99 = simulated[int(len(simulated)*0.99)]
            confidence_values.append((var95, var99))
            j=j+1
            # print(j,i,var95, var99) # so you can see what is being produced
    return {
        'statusCode': 200,
        'status': "Working",
        'body': json.dumps(confidence_values)
    }