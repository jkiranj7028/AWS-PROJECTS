### This project demonstrates how to automatically assign a public IP to Jenkins instances running in EC2 using AWS Lambda and EventBridge. This setup ensures that Jenkins instances can be accessed externally without manual intervention.


## Architecture Overview

### The architecture consists of the following components:
1. **Jenkins EC2 Instances**: Jenkins servers running in AWS EC2.
2. **AWS Lambda Function**: A serverless function that assigns a public IP to Jenkins instance when they are launched
3. **AWS EventBridge**: Monitors EC2 instance launch events and triggers the Lambda function.
4. **IAM Role and Policies**: Permissions required for the Lambda function to interact with EC2 instances.
## Prerequisites
- An AWS account with necessary permissions to create and manage EC2, Lambda, EventBridge, and IAM resources.
- Basic knowledge of AWS services and Lambda functions.
- AWS CLI installed and configured on your local machine.
## Deployment Steps
1. **Create IAM Role for Lambda**: Create an IAM role with policies that allow the Lambda function to describe and modify EC2 instances.
2. **Create Lambda Function**: Write and deploy the Lambda function that assigns a public IP to Jenkins EC2 Instance.
3. **Set Up EventBridge Rule**: Create an EventBridge rule that triggers the Lambda function on EC2 instance launch events.
4. **Test the Setup**: Launch a Jenkins EC2 instance and verify that it receives
a public IP address automatically.

## Lambda Function Code Example
Here is a sample Python code for the Lambda function:

```python
import boto3
import json
import os

def lambda_handler(event, context):
    ec2_client = boto3.client('ec2')
    cf_client = boto3.client('cloudfront')
    
    EC2_INSTANCE_ID = os.environ['EC2_INSTANCE_ID']
    CLOUDFRONT_DISTRIBUTION_ID = os.environ['CLOUDFRONT_DISTRIBUTION_ID']
    
    # --- Get EC2 Public DNS ---
    reservations = ec2_client.describe_instances(InstanceIds=[EC2_INSTANCE_ID])['Reservations']
    instance = reservations[0]['Instances'][0]
    public_dns = instance.get('PublicDnsName')
    
    if not public_dns:
        print("No public DNS found. Instance may not be running.")
        return
    
    print(f"EC2 Public DNS: {public_dns}")

    # --- Get CloudFront Distribution Config ---
    response = cf_client.get_distribution_config(Id=CLOUDFRONT_DISTRIBUTION_ID)
    dist_config = response['DistributionConfig']
    etag = response['ETag']

    # --- Update Origin Domain Name ---
    old_origin = dist_config['Origins']['Items'][0]['DomainName']
    dist_config['Origins']['Items'][0]['DomainName'] = public_dns

    # --- Save Updated Config ---
    result = cf_client.update_distribution(
        Id=CLOUDFRONT_DISTRIBUTION_ID,
        IfMatch=etag,
        DistributionConfig=dist_config
    )

    print(f"✅ CloudFront origin updated from {old_origin} → {public_dns}")
    return {
        'statusCode': 200,
        'body': json.dumps(f"CloudFront origin updated from {old_origin} to {public_dns}")
    }
``` 
## Conclusion
By following this guide, you can automate the assignment of public IP addresses to Jenkins EC2 instances using AWS Lambda and EventBridge. This setup enhances accessibility and reduces manual configuration efforts.



