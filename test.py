import boto3
import paramiko
from paramiko import SSHClient
import json
import ast

aws_access_key_id="ASIAYB7NMG74NDUDX57B"
aws_secret_access_key="Bw5236CrQ7cvCZ+gYCsnlLq1Ylb9EyxjVGo9wMpY"
aws_session_token="FwoGZXIvYXdzEPj//////////wEaDMsSFoGAdA7yKAKXiCLEAe6SWIQE6ENmTXP5G7FxiwNHI/GyDE6tgTgu9lm98oSH7C6ytrhL6Sr3zGufx97JiIRo54kQO8uuE3DVRGZVUskeinH2mHGGYwAFf3Way4qdL3aAeNlO91Eiz6ai8pls4mMnK672UE+zn0+geatE8BzhyfDaQhjWttrtwCanYItHdk33jFKBP7LKNe4T7iFLDpx09rLMYjjy2c94jFFuQTUugEnWJ+B+qWsFI+IxU4TdQo5VVF9fiSwzOZv6nTj6d9AtQXwo5pGgiAYyLfrdrSnwLzHPt+MoZLIdg2A+JBMT8XlFCklR2//mwGZ6v6CI3ak+qbH7Yh2JHQ=="

user_data = '''#!/bin/bash
sudo apt-get update &&
sudo apt-get install python3 &&
sudo apt install python3-pip &&
cd /home/ubuntu/ &&
git clone https://github.com/evans123456/trading_signals_ec2 &&
cd trading_signals_ec2 &&
pip3 install -r requirements.txt'''

def create_ec2_instance():
    global aws_access_key_id,aws_secret_access_key
    try:
        print ("Creating EC2 instance")
        resource_ec2 = boto3.client("ec2",region_name='us-east-1',aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token,)
        
        print("-> ",resource_ec2)
        resource_ec2.run_instances(
            ImageId="ami-09e67e426f25ce0d7", #ubuntu
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.micro",
            SecurityGroupIds=['sg-0f7bd768e32d6f5d6'],
            UserData=user_data, 
            KeyName="mykeypair",
            
        )
        print("end of request")
    except Exception as e:
        print(e)


# create_ec2_instance()
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

# create_ec2_instance()


# ip=[]

# create_ec2_instance()


ip=[]


ids = describe_ec2_instance()
print("instance_ids",ids)

for i in ids:
    ip.append(get_public_ip(i))

res = [x for x in ip if x is not None]
print(res)

h=200
d=100000
t=1


get_values_from_ec2(res,h,d,t)

