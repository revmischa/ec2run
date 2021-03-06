import boto3
import time
from .session import get_client, get_resource

# you'll want to change these...
AMI:str = 'ami-e316ba8c'  # chat2
SUBNET:str = 'subnet-782d2710'  # chat-1a
SECURITY_GROUP:str = 'sg-2dd7f546'  # chat
IAM_INSTANCE_ROLE_ARN:str = 'arn:aws:iam::178183757879:instance-profile/chatbox'

USERDATA:str = """
yum -y update
"""

def client() -> boto3.client:
    return get_client('ec2')

def get_instance(instance_id:str):
    ec2 = get_resource('ec2')
    return ec2.Instance(instance_id)    

def run_instance():
    response = client().run_instances(
        ImageId=AMI,
        InstanceType='t2.nano',
        KeyName='awsmish',
        SecurityGroupIds=[SECURITY_GROUP],
        SubnetId=SUBNET,
        InstanceInitiatedShutdownBehavior='terminate',
        UserData=USERDATA,
        MinCount=1,
        MaxCount=1,
        IamInstanceProfile={'Arn': IAM_INSTANCE_ROLE_ARN},
    )
    instances = response['Instances']
    instance = instances[0]
    instance_id = instance['InstanceId']

    print("*** Booting...")

    # wait..
    try:
        waiter = client().get_waiter('instance_status_ok')
        waiter.wait(
            InstanceIds=[instance_id],
            Filters=[
                {'Name': 'instance-state-name', 'Values': ['running']},
            ]
        )
    except Exception as ex:
        instance = get_instance(instance_id)
        print("*** Terminating")
        if instance:
            instance.terminate()
        raise Exception from ex

    print("*** Booted")

    instance = get_instance(instance_id)
    return instance

