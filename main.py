from flask import Flask, render_template, request,redirect,url_for, jsonify
from concurrent.futures import ThreadPoolExecutor
import http.client
import json
# from finance import data
import ast
import pickle
import base64
import time
import boto3
import paramiko
from paramiko import SSHClient
from boto.manage.cmdshell import sshclient_from_instance

aws_access_key_id="ASIAYB7NMG74GA7GQ26C"
aws_secret_access_key="2KVJ2AUQmYsNUBVa7By1V8FCxoguiupcYw2yAZkQ"
aws_session_token="FwoGZXIvYXdzEP///////////wEaDOVO6RYCFFYZx2aOWCLEAcDq5FQUPko27uOrEoUqq66egdONcOyM72XTkS7ZTcNUu/JyeMImuuIRNfgYYE4ZZ4APy/EiNyQUTQCHlMwngklmEVUHffwlMJXEVgEDxRCAbc6lW8wXJBFiiMQYYtSbXBDsjXXqACIumjEK2QuMWpAAaF7fezIGtD3odYk6jSyC7rPL7wCETLT3FdNCKdTKEsSPLr6NybyvBeB57jQ3JFHgEc9bYFopFAV1Bpb2oXHJREsbE68Gc+1o6LTQjt4iyj4kubIo48OhiAYyLXaAfFFzvG0dqbBvw/Aw9DS3X47wTh/CssFG631vl4TnIqMn4POv0GOAj1HFrA=="
# aws_secret_access_key=BmlktIDPEOadgSntyMil+7A0viRhy60pfLiMfwxN
# aws_access_key_id=ASIAYB7NMG74LFSHYR6G



user_data = '''#!/bin/bash
sudo apt-get update &&
sudo apt-get install python3 &&
cd /home/ubuntu/ &&
git clone https://github.com/evans123456/trading_signals_ec2 &&
cd trading_signals_ec2 &&
sudo apt install --yes python3-pip &&
pip install -r requirements.txt'''

# user_data = '''#!/bin/bash
# echo 'test' > /tmp/hello'''

# user_data = '''#!/bin/bash
# sudo apt-get update &&
# sudo apt-get install python3 &&
# cd /home/ubuntu/ &&
# git clone https://github.com/evans123456/ec2 &&
# cd ec2'''


def create_ec2_instance():
    try:
        print ("Creating EC2 instance")
        resource_ec2 = boto3.client("ec2",region_name='us-east-1',aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token,)
        resource_ec2.run_instances(
            ImageId="ami-09e67e426f25ce0d7", #ubuntu
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.micro",
            UserData=user_data, 
            KeyName="mykeypair",
            SecurityGroupIds=['sg-0f7bd768e32d6f5d6'],            
        )
        print("end of request")
    except Exception as e:
        print(e)



def describe_ec2_instance():
    instance_ids = []
    try:
        print ("Describing EC2 instance")
        resource_ec2 = boto3.client("ec2",region_name="us-east-1",aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)
        for i in resource_ec2.describe_instances()["Reservations"]:

            print(i["Instances"][0]["InstanceId"])
            instance_ids.append(i["Instances"][0]["InstanceId"])
        
        print("DONE")

        # print(resource_ec2.describe_instances()["Reservations"][0]["Instances"][0]["InstanceId"])
        return instance_ids
    except Exception as e:
        print(e)

def get_public_ip(instance_id):
    ec2_client = boto3.client("ec2", region_name="us-east-1",aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)
    reservations = ec2_client.describe_instances(InstanceIds=[instance_id]).get("Reservations")

    for reservation in reservations:
        for instance in reservation['Instances']:
            print(instance.get("PublicIpAddress"))
            if instance.get("PublicIpAddress") == None:
                continue
            else:    
                return instance.get("PublicIpAddress")

def get_values_from_ec2(hosts,h,d,t):
    
    # host="100.26.143.241"
    values=[]
    times=[]
    user="ubuntu"
    key=paramiko.RSAKey.from_private_key_file("./mykeypair.pem")
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # client.load_system_host_keys()
    for host in hosts:
        print("fetching...",host)
        client.connect(host, username=user,pkey=key)
        stdin, stdout, stderr = client.exec_command(f'cd /home/ubuntu/ && cd trading_signals_ec2/ && python3 finance.py {int(h)} {int(d)} {int(t)}')
        # print ("stderr: ", stderr.readlines())
        vals = json.loads(stdout.readlines()[5])
        values.append(vals['values'])
        times.append(vals['elapsed_time'])


    print("values: ",values)
    print("time: ",times)
    # print("type: ",type(vals))


    return values




# -----------------------------------------------------------------------------------------------------------------------
app = Flask(__name__)


@app.route('/',methods = ["POST","GET"])
def home():
    if request.method == "POST":
        service = request.form["service"]
        resource = int(request.form["resources"])

        # print(data)
        print(service,resource)

        if service == "ec2":
            warm_up_resources(resource,0)
            return redirect(url_for("risk_analysis",srv=service,r=resource))
        else: #if lambda
            warm_up_resources(resource,1)
            return redirect(url_for("risk_analysis",srv=service,r=resource))
        


    else:
        return render_template("home.html")



def warm_up_resources(num_resources,resource):
    current_state = ""
    val=0
    ec2 = boto3.resource('ec2',region_name="us-east-1",aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)

    print("Warming up resources...")
    
    if resource == 0:
        print("creating ec2 instances...")

        for i in range(num_resources):
            create_ec2_instance()

        while current_state != 'ok':
            
            for status in ec2.meta.client.describe_instance_status()['InstanceStatuses']:
                current_state = status['SystemStatus']['Status']
                if current_state=="ok":
                    print("Resource OK!: ",current_state)
                    val = val+1
                    if val == num_resources:
                        break
                    else:
                        continue
                else:
                    print("The status: ",current_state)
                    time.sleep(10)


        print("EC2 instances created successfully!")
    else:
        print("Warming up lambda...")
        # send demo text to lambda

        print("Lambda warmed up successfully")




@app.route("/<srv>/<r>",methods = ["POST","GET"])
def risk_analysis(srv,r):
    ip=[]
    values=[]
    if request.method == "POST":
        d = request.form["d"]    
        h = request.form["h"]   
        t = request.form["t"]   
        print("D H T -> ",d,h,t)

        


        ids = describe_ec2_instance()
        print("instance_ids",ids)

        for i in ids:

            ip.append(get_public_ip(i))

        res = [x for x in ip if x is not None]
        print(res)

        values = get_values_from_ec2(res,h,d,t)
        
        
        print("Results should be back",values)
        return redirect(url_for("lastPage",d=d,h=h,t=t,values=values))

        
    else:
        return render_template("risk_analysis.html",content=srv)


@app.route("/<d>/<h>/<t>/<values>/",methods = ["POST","GET"])
def lastPage(d,h,t,values):
    final = []
    values = ast.literal_eval(values)
    print("The values: ",values)
    print("hubee: ",values[0])
    for index,i in enumerate(values):
        print("------> ",i)
        for j in i:
            # print(index,"what we want-> ",j)
            final.append(j)
    return render_template("output.html",content=final)



def fetch_stuff():
    global data
    with ThreadPoolExecutor() as executor:

        host = "wi0m4i6mlc.execute-api.us-east-1.amazonaws.com"        
        c = http.client.HTTPSConnection(host) 
        
        # df = data.head().to_json()  
        pickled = pickle.dumps(data.head())
        pickled_b64 = base64.b64encode(pickled)
        hug_pickled_str = pickled_b64.decode('utf-8')
        print(hug_pickled_str)

        obj = {
            "data":hug_pickled_str,
            "H":200,
            "D":100000,
            "T":1
        }   
            
        c.request("POST", "/default/lsa", json.dumps(obj))        
        response = c.getresponse()        


        data = json.loads(response.read().decode('utf-8') ) 
        print("From AWS: ",data)
        print()
        # print("body: ",json.loads(ast.literal_eval(data["body"])["data"]))

















































@app.route("/audit",methods = ["GET"])
def audit():
    items = []
    # docs = db.collection("history").get()
    # for doc in docs:
    #     items.append(doc.to_dict())

    # items = reversed(items)
    return render_template("audit.html",vals=items)







# Default port:
if __name__ == '__main__':
    # fetch_stuff()
    app.run(debug=True)
    

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''