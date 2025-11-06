Here is a comprehensive, enterprise-level procedure for deploying a Jenkins server on an EC2 instance using CloudFormation.

This approach correctly uses an IAM Instance Profile (IAM Role) instead of hard-coded AWS credentials. This is the industry best practice for security, as it allows the EC2 instance (and thus Jenkins) to securely interact with other AWS services using temporary, automatically-rotated credentials.

We will create a template that builds:

An IAM Role for Jenkins with permissions for common CI/CD tasks (ECS, ECR, S3).

An EC2 Security Group to allow access for SSH (port 22) and Jenkins (port 8080).

An EC2 Instance that automatically:

Uses the latest Amazon Linux 2 AMI.

Installs Java 17, Jenkins, Git, and Docker.

Starts Jenkins and Docker, and adds the jenkins user to the docker group.

1. The CloudFormation Template
Save the following code as jenkins-server-cfn.yml

What You Must Change
You need to find these values in your AWS account and replace the Default values in the template before you run it (or override them in the CloudFormation UI when you create the stack).

VPCId: 'vpc-0a1b2c3d4e5f67890'

Find yours: Go to the VPC Console in AWS. Your "default" VPC is a good choice. Copy its VPC ID.

SubnetId: 'subnet-0123456789abcdef0'

Find yours: In the VPC Console, go to Subnets. Pick a public subnet (one that has an Internet Gateway in its Route Table) that is inside your chosen VPC. Copy its Subnet ID.

MyIP: '12.34.56.78/32'

Find yours: Google "what is my ip". If your IP is 88.99.100.101, you would enter 88.99.100.101/32.

KeyName: 'my-ec2-keypair'

Find yours: Go to the EC2 Console and look under Key Pairs in the "Network & Security" section. Use the name of a key pair you have the .pem file for.

2. How to Deploy the Template
Find Your VPC and Subnet:

Go to the AWS VPC console.

Note the VPC ID of your default or preferred VPC.

Go to "Subnets" and find a Public Subnet within that VPC (one that has a route to an Internet Gateway). Note its Subnet ID.

Find Your IP Address:

Google "what is my ip" to get your public IP address. You'll need this for the MyIP parameter (e.g., 103.22.15.120/32).

Warning: Using the default 0.0.0.0/0 will make your Jenkins server open to the entire internet, which is a major security risk. Always use your specific IP.

Ensure You Have an EC2 KeyPair:

Go to the EC2 console and look under "Key Pairs".

Make sure you have a key pair and you have the .pem file for it. Note its KeyName.

Deploy via CloudFormation:

Go to the AWS CloudFormation console.

Click Create stack > With new resources (standard).

Select Upload a template file and choose your jenkins-server-cfn.yml file.

Click Next.

Give your stack a name (e.g., Jenkins-Server-Stack).

Fill in the Parameters section with the VPCId, SubnetId, MyIP (as x.x.x.x/32), and KeyName you gathered.

Click Next through the options pages (the defaults are fine).

On the final page, acknowledge that the stack will create IAM resources, and click Create stack.

The stack will take 3-5 minutes to create. It will be complete when the status shows CREATE_COMPLETE.

3. After Deployment: First-Time Jenkins Setup
Get Your Jenkins URL:

Go to the CloudFormation stack's Outputs tab.

You will see the JenkinsURL. Copy and paste it into your browser (e.g., http://ec2-xx-xx-xx-xx.compute-1.amazonaws.com:8080).

It may take a minute for Jenkins to fully start. If you get a "site can't be reached" error, wait 60 seconds and refresh.

Get the Initial Admin Password:

From the Outputs tab, copy the SSHCommand.

Open your terminal, replace <your-key.pem> with the path to your key file, and connect to the instance.

Once connected, run the command from the InitialPasswordCommand output:

Bash

sudo cat /var/lib/jenkins/secrets/initialAdminPassword
This will print a long alphanumeric string. Copy it.

Complete the Setup:

Paste the password into the "Unlock Jenkins" screen in your browser.

Click "Install suggested plugins".

Create your first admin user.

You now have a fully functional, secure Jenkins server ready to build Docker images and deploy to ECS, all managed as code.
