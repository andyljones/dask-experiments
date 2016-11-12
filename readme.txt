 * Create an AWS account and set up billing.
 * Following this tutorial: 
    * Create a user called 'ec2-admin' or similar. Make a note of the access key ID and secret key, which will be used to access the API.
    * Give the user the "AmazonEC2FullAccess" policy. You can attach the policies directly to the user; no need to create groups just yet. 
    * From the EC2 panel, create a key pair, say 'andyljones-key-pair-us-east'. This'll be used to connect to container instances via ssh
    * Also create a security group that allows inbound access through port 22, say 'andyljones-ssh'.
 * Install the AWS CLI using "pip install awscli"
 * Set up a default configuration using "aws configure". Pass it the ID and secret you got when creating the 'ec2-admin' user. Set the default region to whatever the default region for the key pair was (probably us-east).
 * Install boto3.