import boto3

PROFILE:str = 'default'
REGION:str = 'eu-central-1'

session:boto3.session = boto3.Session(profile_name=PROFILE)

def get_client(service:str) -> boto3.client:
    return session.client(service, region_name=REGION)

def get_resource(res:str) -> boto3.resource:
    return session.resource(res, region_name=REGION)
