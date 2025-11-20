### I want to run Jenkins on a custom domain: jenkins.devopscloudai.com.  
To achieve this, I have set up the following components:

1.  EC2 Instance – Hosts the Jenkins server.
2.  Jenkins Installation – Installed and configured on the EC2 instance.
3.  CloudFront – Distributes traffic for the custom domain jenkins.devopscloudai.com.
4.  Route 53 – Provides DNS configuration to make the domain globally accessible.
5.  AWS Lambda + EventBridge – Automates the reassignment of EC2 public IPs for Jenkins instances running on EC2. When an EC2 instance transitions from a stopped to a running state, EventBridge triggers a Lambda function. This function executes a predefined Python script that updates the CloudFront origin, replacing the old endpoint (e.g., ec2-15-204-145-134.ap-south-1.compute.amazonaws.com) with the new one (e.g., ec2-13-204-157-132.ap-south-1.compute.amazonaws.com).

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
    
   
let’s extend your Jenkins installation guide with the **initial setup steps** after the service is running. 

# Jenkins Installation Guide (RedHat/CentOS)

## Prerequisites
- Ensure **Java** is installed (Jenkins requires Java).
- Jenkins runs on **port 8080** by default.

---

## Step 1: Add Jenkins Repository
```bash
sudo wget -O /etc/yum.repos.d/jenkins.repo \
    https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
sudo yum upgrade
```

---

## Step 2: Install Dependencies
```bash
dnf install fontconfig -y
```

---

## Step 3: Install Java
```bash
dnf install java-21-amazon-corretto -y
```

---

## Step 4: Install Jenkins
```bash
dnf install jenkins -y
```

---

## Step 5: Enable and Start Jenkins
Enable Jenkins service immediately:
```bash
systemctl enable jenkins --now
```

Or start and then enable:
```bash
systemctl start jenkins
systemctl enable jenkins
```

---

## Step 6: Verify Jenkins Service
```bash
systemctl status jenkins
```
- Access Jenkins at: **http://<public-ip>:8080**

---

## Step 7: Initial Jenkins Setup

### Unlock Jenkins
- When you first access Jenkins, it asks for an **initial admin password**.
- Retrieve it from:
```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```
- Copy and paste this password into the web UI.

---

### Install Suggested Plugins
- Jenkins will prompt to install plugins.
- Choose **Install suggested plugins** for a standard setup.
- Alternatively, select specific plugins based on your project needs.

---

### Create Admin User
- After plugins are installed, Jenkins asks you to create the first admin user.
- Provide:
  - **Username**
  - **Password**
  - **Full name**
  - **Email address**

---

### Configure Instance
- Confirm Jenkins URL (e.g., `http://<Public-IP>:8080`).
- Save and finish setup.

![alt text](<Screenshot 2025-11-20 at 9.02.24 PM.png>)

---

## ✅ Jenkins is Ready
You can now:
- Log in with your admin account.
- Start creating jobs, pipelines, and configuring integrations.


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
    **Here is the setup pic**:
    ![alt text](<Screenshot 2025-11-20 at 8.59.56 PM.png>)

3. **Create EventBridge Rule**:
    - Create a new EventBridge rule that triggers on EC2 instance state changes (specifically when the instance enters the "running" state).
    - Set the target of the rule to the Lambda function created in the previous step.

    ![alt text](<Screenshot 2025-11-20 at 8.59.33 PM.png>)
    
4. **Route 53**: 
    - Add CloudFront 'Domain Name' in in Route 53 with A Record
    ![alt text](<Screenshot 2025-11-20 at 9.00.55 PM.png>)

5. **CloudFront**:
    - Create Distribution in cloudFront with subdomain ie. jenkins.devopscloudai.com
    ![alt text](<Screenshot 2025-11-20 at 9.00.28 PM.png>)

5. **Test the Setup**:
    - Start the Jenkins EC2 instance and verify that the Lambda function is triggered.
    - Check the CloudFront distribution to ensure that the origin has been updated with the new public DNS of the Jenkins instance.
## Conclusion
By following these steps, you can automate the assignment of a public IP to your Jenkins EC2 instances using AWS Lambda and EventBridge. This setup enhances accessibility and reduces manual configuration efforts.

## Cleanup
To avoid incurring unnecessary charges, remember to delete the resources created during this setup when they are
no longer needed.
1. Delete the EC2 instance.
2. Delete the Lambda function.
3. Delete the EventBridge rule.

