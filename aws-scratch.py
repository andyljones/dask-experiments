#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 17:01:14 2016

@author: andyjones
"""

import boto3

def run():
    ec2 = boto3.resource('ec2')
    instances = ec2.create_instances(ImageId='ami-b73b63a0', 
                                     MinCount=1, 
                                     MaxCount=1, 
                                     KeyName='andyljones-key-pair-us-east-1',
                                     UserData=open('cloud-config.yaml').read(),
                                     SecurityGroups=['andyljones-ssh'],
                                     InstanceType='t2.small')
    instance = instances[0]