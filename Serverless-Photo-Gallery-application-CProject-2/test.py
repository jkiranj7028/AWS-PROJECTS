import boto3
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    source_bucket = os.environ['SOURCE_BUCKET']
    destination_bucket = os.environ['DESTINATION_BUCKET']

    response = s3.list_objects_v2(Bucket=source_bucket)
    if 'Contents' in response:
        for obj in response['Contents']:
            key = obj['Key']
            s3.copy_object(CopySource={'Bucket': source_bucket, 'Key': key}, Bucket=destination_bucket, Key=key)
            s3.delete_object(Bucket=source_bucket, Key=key)
            print(f"Moved: {key}")
    else:
        print("No files found in the source bucket.")
    return {
        'statusCode': 200,
        'body': f"Successfully moved files from {source_bucket} to {destination_bucket}"
    }