 * Create an AWS account and set up billing.
 * Following the EC2 Linux tutorial: 
    * Create a user called 'ec2-admin' or similar. Make a note of the access key ID and secret key, which will be used to access the API.
    * Give the user the "AmazonEC2FullAccess" policy. You can attach the policies directly to the user; no need to create groups just yet. 
    * Create a key pair, say 'andyljones-key-pair-us-east-1'. Save it locally. This'll be used to connect to container instances via ssh
    * Create a security group that allows inbound access through port 22, say 'andyljones-ssh'. 
    * Create a security group that allows all inbound traffic from the same group, say 'mutual-access-1'.
 * Install the AWS CLI using `pip install awscli`
 * Set up a default configuration by calling `aws configure`. Pass it the ID and secret you got when creating the 'ec2-admin' user. Set the default region to whatever the default region for the key pair was (probably us-east).
 * Install boto3 with `conda install boto3`
 * Install dask.distributed with `conda install distributed -c conda-forge`
 * Edit the `KEY_PAIR, SSH_GROUP, MUTUAL_ACCESS_GROUP` constants in `scratch.py` to match whatever you called your keys/groups.
 * Start an ipython console and run `from scratch import *`. 
 * From the ipython console, start a dask.distributed scheduler and worker using
 
 ```python
 scheduler = get_or_create_scheduler()
 workers = get_or_create_workers()
 ```
 
 * Establish SSH tunnels to both the scheduler and the scheduler's webpage using
 
 ```python
 scheduler_tunnel = create_tunnel(scheduler.public_dns_name, '8785', '8785')
 http_tunnel = create_tunnel(scheduler.public_dns_name, '2000', '80')
 ```
 
 * Then you can submit work using 
 
 ```python
 client = distributed.Client('127.0.0.1:8785')
 future = client.submit(lambda: return 'hello world!')
 print(future.result())
 ```

 * You can also submit shell commands to each worker using ```run_command```.
    