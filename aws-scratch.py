#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 17:01:14 2016

@author: andyjones
"""

import distributed
import yaml
import boto3
import subprocess
from contextlib import contextmanager
from time import sleep

KEYPAIR = 'andyljones-key-pair-us-east-1'

def generate_config(scheduler_ip=None):
    config = yaml.load(open('cloud-config.yaml'))
    if scheduler_ip is None:
        config['runcmd'].append('nohup dask-scheduler --bokeh-port 80 --port 8785')
        config['runcmd'].append('nohup dask-worker --worker-port 8784 127.0.0.1:8785')
    else:
        config['runcmd'].append('nohup dask-worker --worker-port 8784 {}:8785'.format(scheduler_ip))
        
    config_string = '#cloud-config\n' + yaml.dump(config)
    return config_string

def create_instance(ec2, config, count=1):
    return ec2.create_instances(ImageId='ami-b73b63a0', 
                                MinCount=count, 
                                MaxCount=count, 
                                KeyName=KEYPAIR,
                                UserData=config,
                                SecurityGroups=['andyljones-ssh'],
                                InstanceType='t2.small')

def create_tunnel(public_dns_name, local_port, remote_port):
    destination = 'ec2-user@' + public_dns_name
    tunnel = str(local_port) + ':' + public_dns_name + ':' + str(remote_port)
    key_pair = KEYPAIR + '.pem'
    tunnel = subprocess.Popen(['ssh', '-i', key_pair, '-N', '-L', tunnel, destination])
    return tunnel
        
def run():
    ec2 = boto3.resource('ec2')
    
    [scheduler] = create_instance(ec2, generate_config())
    workers = create_instance(ec2, generate_config(scheduler.private_ip_address))
    
    scheduler_tunnel = create_tunnel(scheduler.public_dns_name, '8785', '8785')
    http_tunnel = create_tunnel(scheduler.public_dns_name, '2000', '80')
    
    executor = distributed.Executor('127.0.0.1:8785')
    future = executor.submit(lambda n: sum(range(1, n)), 10000)
    print(future.result())
    
    scheduler_tunnel.terminate()
    http_tunnel.terminate()
    scheduler.terminate()
    for w in workers:
        w.terminate()
    