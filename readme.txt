 * Create an AWS account and set up billing.
 * Following the EC2 Linux tutorial: 
    * Create a user called 'ec2-admin' or similar. Make a note of the access key ID and secret key, which will be used to access the API.
    * Give the user the "AmazonEC2FullAccess" policy. You can attach the policies directly to the user; no need to create groups just yet. 
    * Create a key pair, say 'andyljones-key-pair-us-east-1'. Save it locally. This'll be used to connect to container instances via ssh
    * Create a security group that allows inbound access through port 22, say 'andyljones-ssh'. Also create another rule that allows all inbound traffic from the same security group.
 * Install the AWS CLI using "pip install awscli"
 * Set up a default configuration using "aws configure". Pass it the ID and secret you got when creating the 'ec2-admin' user. Set the default region to whatever the default region for the key pair was (probably us-east).
 * Install boto3.
 * Start an instance containing a dask scheduler using something like
 
'''
import boto3

ec2 = boto3.resource('ec2')
instances = ec2.create_instances(ImageId='ami-b73b63a0', 
                                 MinCount=1, 
                                 MaxCount=1, 
                                 KeyName='andyljones-key-pair-us-east-1',
                                 UserData=open('cloud-config.yaml').read(),
                                 SecurityGroups=['andyljones-ssh'],
                                 InstanceType='t2.small')
instance = instances[0]
'''

 * This might take a few minutes. You can check progress by running 
 
'''
print(instance.console_output()['Output'])
'''

 * Once it's done, get the instance's public DNS name using ''instance.public_dns_name''.
 * Create a SSH tunnel from your machine to the instance using
 
'''
import subprocess
destination = 'ec2-user@' + instance.public_dns_name
tunnel = '2000:' + instance.public_dns_name + ':80'
key_pair = 'andyljones-key-pair-us-east-1.pem'
subprocess.Popen(['ssh', '-i', key_pair, '-N', '-L', tunnel, destination])
'''

 * Navigating to ''localhost:2000'' should now throw up the scheduler's monitoring page. Hooray!
 * Terminate the instance with ''instance.terminate()''