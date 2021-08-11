import time
import boto3
import paramiko
import json
from paramiko import SSHClient
import paramiko
import ast
from concurrent.futures import ThreadPoolExecutor
import http.client

aws_access_key_id="ASIAQ7O6D2IRSPAPHS5K"
aws_secret_access_key="UNQCBnmbja+GLPYhQAQMBV0IKAh51hgSWm3yRvtt"
aws_session_token="FwoGZXIvYXdzEMT//////////wEaDPsvIWs1f6CuOrQg1CLEAdggEVAUkK2WhvLw1tcMO6uscZwaDn9b8Zqz+gZQIwHFoloYF1xJn0rdGFpN3EX2Vj3DmmpbzDrGvHvay/+PHUP42Cnp9QKZqe2j9VV4/saNwKSPKXl/eutfH78kcE2Zq4Rtwuljb7SEhnkSlDzKZT3VC6145S0IlEzjSExIrP6lSxlyfQ+H7kMsQ9sBfreADHYmukfQzy2zgmr+TZE3BM8n07yW6fZy9/lI4l0jmSKPZMjTgB5kErD25b+gDu6kGOySwAUotvbMiAYyLWMRSbit2WbOUY1WKa3t3hRnrwAAMXTRdRRnCoI/NC8ecq/9RfK45ZaUxV3Akg=="




region_name="us-east-1"


UserData = '''#!/bin/bash
sudo apt-get update &&
sudo apt-get install python3 &&
cd /home/ubuntu/ &&
git clone https://github.com/evans123456/ec2code &&
cd ec2code &&
sudo apt install --yes python3-pip &&
pip install -r requirements.txt'''




def CreateEC2():
    try:
        print ("initializing EC2")
        resource_ec2 = boto3.client("ec2",region_name=region_name,aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token,)
        resource_ec2.run_instances(
            ImageId="ami-09e67e426f25ce0d7", 
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.micro",
            UserData=UserData, 
            KeyName="financeKeyPair",
            SecurityGroupIds=['sg-0e4bbf9a98276bc3e'],            
        )
    except Exception as e:
        print(e)



def EC2Describe():
    instance_ids = []
    try:
        print ("Describing EC2 instance")
        resource_ec2 = boto3.client("ec2",region_name=region_name,aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)
        for i in resource_ec2.describe_instances()["Reservations"]:

            print(i["Instances"][0]["InstanceId"])
            instance_ids.append(i["Instances"][0]["InstanceId"])
        
        print("DONE")

        # print(resource_ec2.describe_instances()["Reservations"][0]["Instances"][0]["InstanceId"])
        return instance_ids
    except Exception as e:
        print(e)

def EC2GetPublicIP(instance_id):
    ec2_client = boto3.client("ec2", region_name=region_name,aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)
    reservations = ec2_client.describe_instances(InstanceIds=[instance_id]).get("Reservations")

    for reservation in reservations:
        for instance in reservation['Instances']:
            print(instance.get("PublicIpAddress"))
            if instance.get("PublicIpAddress") == None:
                continue
            else:    
                return instance.get("PublicIpAddress")



def WarmUpResources(num,resource):
    current_state = ""
    val=0
    ec2 = boto3.resource('ec2',region_name=region_name,aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,aws_session_token=aws_session_token)

    print("EC2 Warm up")
    
    if resource == 0:

        for i in range(num):
            CreateEC2()

        while current_state != 'ok':
            
            for status in ec2.meta.client.describe_instance_status()['InstanceStatuses']:
                current_state = status['SystemStatus']['Status']
                if current_state=="ok":
                    print("COMPLETED!!!: Status -> ",current_state)
                    val = val+1
                    if val == num:
                        break
                    else:
                        continue
                else:
                    print(current_state)
                    time.sleep(8)


        print("ec2 warmed")
    else:
        print("Warming up!!!")
        # send demo text to lambda
        demo = {
            "d": 100000,
            "h": 200,
            "t": 1,
            "closeColumn": [
                3148.729,

            ],
            "data": [
                [
                "10/18/2011",
                200.50,
                244.50,
                236.50,
                243.50,
                243.50,
                4609700,
                0,
                0
                ],
                
            ]
            }

        fetchLambda(1,demo["h"],demo["d"],demo["t"],demo["closeColumn"],demo["data"])

        print("lambda warmed")


def fetchLambda(r,h,d,t,closeColumn,whole_data):
    risk_values = []
    run_time=[]


    with ThreadPoolExecutor() as executor:
        for i in range(int(r)):
            try:    
                host = "ergl1u2bx4.execute-api.us-east-1.amazonaws.com"        
                c = http.client.HTTPSConnection(host)      
                obj = {
                    "closeColumn":closeColumn,
                    "data":whole_data,
                    "h":h,
                    "d":d,
                    "t":t
                }
                print("resource with id: ",i) 

                    
                c.request("POST", "/default/myLambdaresource", json.dumps(obj))        
                response = c.getresponse()        


                data = json.loads(response.read().decode('utf-8') ) 
                print(f"Lambda resource {i} returned {data} ")
                risk_values.append(ast.literal_eval(data["risk_values"]))
                run_time.append(data['elapsedtime'])
                # find average
                
            

            except IOError:        
                print( 'Failed to open ', host ) # Is the Lambda address correct?    
                print(data+" from "+str(i)) # May expose threads as completing in a different order    
                return "page "+str(i)
            
    return (risk_values,run_time)



def fetchEc2(ip_addresses,h,d,t):
    
    ec2_values=[]
    time_taken=[]
    user="ubuntu"

    key=paramiko.RSAKey.from_private_key_file("./financeKeyPair.pem")
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for ip_address in ip_addresses:

        print("----->",ip_address)

        client.connect(ip_address, username=user,pkey=key)

        stdin, stdout, stderr = client.exec_command(f'cd /home/ubuntu/ec2code/ && python3 ec2.py {int(h)} {int(d)} {int(t)}')

        vals = json.loads(stdout.readlines()[5])

        ec2_values.append(vals['risk_values'])
        time_taken.append(vals['ElapsedTime'])


    print("Time taken array: ",time_taken)


    return (ec2_values,time_taken)