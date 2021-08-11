from flask import Flask,redirect,url_for,render_template, request
import time
import boto3

import json
from flask import session
import ast
from otherFunctions import fetchFinance,calculate_row_average
from AWSFunctions import EC2Describe,EC2GetPublicIP,fetchEc2,fetchLambda, WarmUpResources,region_name,aws_access_key_id,aws_secret_access_key,aws_session_token


app = Flask(__name__)


@app.route('/',methods = ["POST","GET"])
def index():
    if request.method == "POST":
        s = request.form["type_of_service"]
        r = request.form["num_of_resources"]
        

        print(r,s)
        r = int(r)

        if s == "ec2":
            WarmUpResources(r,0)
            return redirect(url_for("getOtherValues",srv=s,r=r))
        else: #if lambda
            WarmUpResources(r,1)
            return redirect(url_for("getOtherValues",srv=s,r=r))
        
    else:
        return render_template("index.html")








@app.route("/<srv>/<r>",methods = ["POST","GET"])
def getOtherValues(srv,r):
    ip=[]
    values=[]
    print(request.form)
    if request.method == "POST":

        d = request.form["d"]    
        t = request.form["t"] 
        h = request.form["h"]   
        
         

        print("D H T -> ",d,h,t)

        data = fetchFinance("INTC")
        data_list = data.Close.values.tolist()
        df = data.values.tolist()


              

        if srv == "ec2":
            instance_ids = EC2Describe()
            for instance_id in instance_ids:
                ip_address = EC2GetPublicIP(instance_id)
                ip.append(ip_address)

            ips_without_none_values = [x for x in ip if x is not None]

            ec2_values,time_taken = fetchEc2(ips_without_none_values,h,d,t)
            values = calculate_row_average(ec2_values)
            session['risk_values'] = values

            

        else: 
            print("to lambda")
            the_values,time_taken = fetchLambda(r,h,d,t,data_list,df)

            values = calculate_row_average(the_values)

            session['risk_values'] = values

        print("returned-> ",values)


            
        # sum95 = 0
        # sum99 = 0
        # for i in values:
        #     sum95 = sum95 + i[1]
        #     sum99 = sum99 + i[2]
        
        # ave95 = sum95/len(values)
        # ave99 = sum99/len(values)
        # time=0
        # for i in times:
        #     time = time + float(i)
        
        # avgtime = time/len(times)

        # #save to db
        # db.collection("history").add({
        #     "s":srv, 
        #     "r":r,
        #     "d":d,
        #     "t":t,
        #     "95":ave95,
        #     "99":ave99,
        #     "compute_time":avgtime}
        # )

            
        return redirect(url_for("results",d=d,h=h,t=t,srv=srv))

        
    else:
        return render_template("getOtherValues.html")


@app.route("/<d>/<h>/<t>/<srv>/",methods = ["GET","POST"])
def results(d,h,t,srv):
    risk_values = session['risk_values']
    session['srv'] = srv

    return render_template("results.html",srv=srv,content=risk_values,d=d,h=h,t=t)

@app.route("/reset",methods = ["POST"])
def reset_analysis():
    risk_values = []
    srv = session['srv']
    return render_template("results.html",srv=srv,content=risk_values)



@app.route("/terminateInstances",methods = ["POST"])
def terminateInstances():
    global aws_access_key_id,aws_secret_access_key
    instances = EC2Describe()
    for instance in instances:
        try:
            print ("Terminating {instance}")

            resource_ec2 = boto3.client(
                "ec2",
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token)


            resource_ec2.stop_instances(InstanceIds=[instance])

            print("{} Terminated".format(instance))
        except Exception as e:
            print(e)
    return render_template("terminate.html",instance_ids=instances)













































@app.route("/audit",methods = ["GET"])
def audit():
    items = []
    # docs = db.collection("history").get()
    # for doc in docs:
    #     items.append(doc.to_dict())

    # items = reversed(items)
    return render_template("audit.html",vals=items)








    

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

if __name__ == '__main__':
    app.secret_key = 'supersecretkey'
    app.run(debug=True)