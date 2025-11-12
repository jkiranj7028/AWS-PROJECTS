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