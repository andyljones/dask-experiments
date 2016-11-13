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

KEYPAIR = 'andyljones-key-pair-us-east-1'

EC2 = boto3.resource('ec2')

def generate_config(scheduler_ip=None):
    config = yaml.load(open('cloud-config.yaml'))
    if scheduler_ip is None:
        config['runcmd'].append('nohup dask-scheduler --bokeh-port 80 --port 8785 &')
        config['runcmd'].append('nohup dask-worker --worker-port 8784 127.0.0.1:8785 &')
    else:
        config['runcmd'].append('nohup dask-worker --worker-port 8784 {}:8785 &'.format(scheduler_ip))
        
    config_string = '#cloud-config\n' + yaml.dump(config)
    return config_string

def create_instance(name, config):
    return EC2.create_instances(ImageId='ami-b73b63a0', 
                                MinCount=1, 
                                MaxCount=1, 
                                KeyName=KEYPAIR,
                                UserData=config,
                                SecurityGroups=['andyljones-ssh', 'mutual-access-1'],
                                InstanceType='t2.small')

def set_name(instance, name):
    EC2.create_tags(Resources=[instance.id], Tags=[{'Key': 'Name', 'Value': name}])
    
def as_dict(tags):
    return {t['Key']: t['Value'] for t in tags}
    
def list_instances():
    instances = {}
    for i in EC2.instances.all():
        instances.setdefault(as_dict(i.tags)['Name'], []).append(i)
    return instances

def get_or_create_scheduler():
    instances = list_instances()
    if 'scheduler' in instances:
        return instances['scheduler'][0]
    
    [scheduler] = create_instance('scheduler', generate_config())
    set_name(scheduler, 'scheduler')
    return scheduler
    
def get_or_create_workers():
    instances = list_instances()
    if 'worker' in instances:
        return instances['worker']
    
    scheduler = get_or_create_scheduler()
    workers = create_instance('worker', generate_config(scheduler.private_ip_address))
    for worker in workers:
        set_name(worker, 'worker')
    return workers
    
def create_tunnel(public_dns_name, local_port, remote_port):
    destination = 'ec2-user@' + public_dns_name
    tunnel = str(local_port) + ':' + public_dns_name + ':' + str(remote_port)
    key_pair = KEYPAIR + '.pem'
    return subprocess.Popen(['ssh', '-i', key_pair, '-N', '-L', tunnel, destination])
        
def run():
    scheduler = get_or_create_scheduler()
    workers = get_or_create_workers()
    
    scheduler_tunnel = create_tunnel(scheduler.public_dns_name, '8785', '8785')
    http_tunnel = create_tunnel(scheduler.public_dns_name, '2000', '80')
    
    client = distributed.Client('127.0.0.1:8785')
    future = client.submit(lambda n: sum(range(1, n)), 10000)
    print(future.result())
    
    scheduler_tunnel.terminate()
    http_tunnel.terminate()
    scheduler.terminate()
    for w in workers:
        w.terminate()
    