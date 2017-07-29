"""Sail away to chat island."""

import boto3
import random


SNAPSHOT:str = 'public-irssi-1'
KEYPAIR:str = 'awsmish'
BUNDLE_ID:str = 'micro_1_0'
INIT:str = """
apt-get –y update
"""

lightsail:int = session.client('lightsail', region_name='eu-central-1')

def gen_name():
    return f"chatbox-{random.randint(1, 100000000)}"

def new_island():
    response = lightsail.create_instances_from_snapshot(
        instanceNames=[gen_name()],
        instanceSnapshotName=SNAPSHOT,
        availabilityZone='eu-central-1a',
        bundleId=BUNDLE_ID,
        userData=INIT,
        keyPairName=KEYPAIR,
    )
    print("Booting...")

    print(response)
