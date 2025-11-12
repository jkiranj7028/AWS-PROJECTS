# AWS Lambda automation that automatically updates your CloudFront origin domain whenever your EC2 instance starts or gets a new public IP / DNS.

## This is the best long-term, zero-maintenance solution — no need to log into EC2 or manually edit CloudFront ever again.
Trigger:
EventBridge (CloudWatch) rule → EC2 state change (running)

Action:
Lambda function →
    1.	Detect EC2’s new public DNS name
    2.	Fetch CloudFront distribution config
    3.	Update the origin domain name
    4.	Save new config with versioning

Prerequisites
Before deployment, need below parameters:
EC2_INSTANCE_ID
CLOUDFRONT_DISTRIBUTION_ID
REGION

## Step 1: Create IAM Role for Lambda
Create a role named lambda-cloudfront-updater-role with the following IAM policy in JSON,
Attach this role to the Lambda function:


        {
        "Version": "2012-10-17",
        "Statement": [
            {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "cloudfront:GetDistributionConfig",
                "cloudfront:UpdateDistribution"
            ],
            "Resource": "*"
            }
        ]
        }
    

## Step 2: Create the Lambda Function
Use Python 3.9 or newer runtime.
Function name: update-cloudfront-origin
Runtime: Python 3.9
Timeout: 1 minute
Execution role: lambda-cloudfront-updater-role
Paste the following code: python

## Step 3: Add Environment Variables
In the Lambda Configuration → Environment Variables section:

Key : EC2_INSTANCE_ID
Value: (your EC2 instance ID)
Key : CLOUDFRONT_DISTRIBUTION_ID
Value: (your CloudFront distribution ID)

## Step 4: Create EventBridge Rule (Trigger)
Go to Amazon EventBridge → Rules → Create Rule
Name: ec2-start-update-cloudfront
Event Source: AWS events
Event Pattern in JSON:
(Replace the instance ID with yours.)
        
            {
            "source": ["aws.ec2"],
            "detail-type": ["EC2 Instance State-change Notification"],
            "detail": {
                "state": ["running"],
                "instance-id": ["EC2_INSTANCE_ID"]
            }
            }
        
## Step 5: Test the Flow
1.	Stop and start your EC2 instance.
2.	Wait ~1 minute.
3.	Go to CloudFront → Distribution → Origins —
You should see:
Origin Domain: ec2-NEW-PUBLIC-DNS.ap-south-1.compute.amazonaws.com
4.  CloudFront will deploy the updated config automatically (~1–2 minutes).
