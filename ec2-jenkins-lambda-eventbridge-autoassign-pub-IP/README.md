### I want to run Jenkins on a custom domain: jenkins.devopscloudai.com.  
To achieve this, I have set up the following components:

1.  EC2 Instance – Hosting the Jenkins server.
2.  Jenkins Installation – Installed and configured on the EC2 instance.
3.  CloudFront – Used to serve traffic for jenkins.devopscloudai.com.
4.  Route 53 – Configured DNS to make the domain accessible globally.
5.  AWS Lambda + EventBridge – Automates the assignment of public IPs to Jenkins instances running in EC2.

This project demonstrates how to integrate these AWS services to ensure Jenkins is always accessible externally on the custom domain, without requiring manual intervention.

## EC2 Jenkins Lambda EventBridge Auto-Assign Public IP
This project demonstrates how to automatically assign a public IP to Jenkins instances running in EC2 using AWS Lambda and EventBridge. This setup ensures that Jenkins instances can be accessed externally without manual intervention.
## Architecture Overview
The architecture consists of the following components:
1. **EC2 Instance**: Hosts the Jenkins server.
2. **AWS Lambda Function**: A serverless function that assigns a public IP to the Jenkins EC2 instance when it is launched.
3. **Amazon EventBridge**: Monitors EC2 instance state changes and triggers the Lambda function when a Jenkins instance is started.
## Prerequisites
- An AWS account with necessary permissions to create EC2 instances, Lambda functions, and EventBridge
- AWS CLI installed and configured
- Basic knowledge of AWS services like EC2, Lambda, and EventBridge
## Setup Instructions
1. **Launch EC2 Instance**:
    - Launch an EC2 instance with Jenkins installed. Ensure that the instance has the necessary IAM role to allow Lambda to modify its network settings.
2. **Create Lambda Function**:
    - Create a new Lambda function in the AWS Management Console.
    - Use the following Python code for the Lambda function:
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
    - Set environment variables `EC2_INSTANCE_ID` and `CLOUDFRONT_DISTRIBUTION_ID'.
3. **Create EventBridge Rule**:
    - Create a new EventBridge rule that triggers on EC2 instance state changes (specifically when the instance enters the "running" state).
    - Set the target of the rule to the Lambda function created in the previous step.
4. **Test the Setup**:
    - Start the Jenkins EC2 instance and verify that the Lambda function is triggered.
    - Check the CloudFront distribution to ensure that the origin has been updated with the new public DNS of the Jenkins instance.
## Conclusion
By following these steps, you can automate the assignment of a public IP to your Jenkins EC2
    instances using AWS Lambda and EventBridge. This setup enhances accessibility and reduces manual configuration efforts.
## Cleanup
To avoid incurring unnecessary charges, remember to delete the resources created during this setup when they are
no longer needed.
1. Delete the EC2 instance.
2. Delete the Lambda function.
3. Delete the EventBridge rule.
## Additional Resources
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Amazon EventBridge Documentation](https://docs.aws.amazon.com/eventbridge/)
- [Amazon EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Amazon CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)
    instance using AWS Lambda and EventBridge. This setup enhances accessibility and reduces manual configuration efforts.


