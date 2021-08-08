import sys


import json
import statistics
import random

def lambda_handler(event, context):

    # print(event)
    print(event['d'])
    print(event['h'])
    print(event['t'])
    print(type(event['data']))
    print(type(event['data_list']))
    op = []
    df = event['data']
    data_list = event['data_list']
    
    minhistory = 200
    shots = 100000
    j=0
    for i in range(minhistory, len(df)):
        if df[i][7]==1:
            p = data_list[i-minhistory:i]
            pct = [(b-a)/b for a,b in zip(p, p[1:])]
            mean = sum(pct) / len(pct)
            std = statistics.stdev(pct)
    #         print(i,mean,std)
            print(df[i])
            simulated = [random.gauss(mean,std) for x in range(shots)]
            simulated.sort(reverse=True)
            var95 = simulated[int(len(simulated)*0.95)]
            var99 = simulated[int(len(simulated)*0.99)]
            op.append([df[i][0],var95, var99])
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'op': json.dumps(op),
    }


sys.stdout.write(lambda_handler(int(sys.argv[1]),""))