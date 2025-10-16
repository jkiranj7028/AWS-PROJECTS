import json
import boto3
import uuid
from datetime import datetime

# Configure S3 client with regional endpoint
s3 = boto3.client('s3', 
                  region_name='ap-south-1',
                  config=boto3.session.Config(
                      s3={'addressing_style': 'virtual'},
                      region_name='ap-south-1'
                  ))
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('PhotoGallery')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        photo_id = str(uuid.uuid4())
        filename = body['filename']
        
        # Generate presigned URL for S3 upload with regional endpoint
        presigned_url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': 'photo-gallery-data-bucket', 
                'Key': photo_id,
                'ContentType': 'image/jpeg'
            },
            ExpiresIn=300
        )
        
        # Store metadata in DynamoDB
        table.put_item(
            Item={
                'photoId': photo_id,
                'filename': filename,
                'uploadDate': datetime.now().isoformat(),
                's3Key': photo_id
            }
        )
        
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'photoId': photo_id,
                'uploadUrl': presigned_url
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
