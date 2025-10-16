# Deployment Guide - Serverless-Photo-Gallery-application

## Checklist
- [ ] IAM role created with correct permissions
- [ ] DynamoDB table created and active
- [ ] Photo storage bucket created with CORS and public read policy
- [ ] Website hosting bucket created with public read policy
- [ ] Both Lambda functions created and deployed
- [ ] API Gateway created with GET/POST methods and CORS enabled
- [ ] API Gateway deployed to prod stage
- [ ] Frontend HTML updated with correct URLs
- [ ] Frontend uploaded to website bucket
- [ ] Website accessible and functional


## Step 1: Create IAM Role for Lambda

### 1.1 Create Lambda Execution Role
1. Go to **IAM Console** → **Roles** → **Create role**
2. Select **AWS service** → **Lambda** → **Next**
3. Attach the following policies:
   - `AWSLambdaBasicExecutionRole`
   - `AmazonDynamoDBFullAccess`
   - `AmazonS3FullAccess`
4. Role name: `photo-gallery-lambda-role`
5. **Create role**

## Step 2: Create DynamoDB Table

### 2.1 Create Table
1. Go to **DynamoDB Console** → **Create table**
2. **Table name**: `PhotoGallery`
3. **Partition key**: `photoId` (String)
4. **Table settings**: Use default settings
5. **Create table**

Wait for table status to become **Active** before proceeding.

## Step 3: Create S3 Buckets

### 3.1 Create Photo Storage Bucket
1. Go to **S3 Console** → **Create bucket**
2. **Bucket name**: `photo-gallery-bucket-mumbai-[your-unique-suffix]`
3. **Region**: Asia Pacific (Mumbai) ap-south-1
4. **Block Public Access**: Keep default (all blocked for now)
5. **Create bucket**

### 3.2 Configure CORS for Photo Bucket
1. Select your photo bucket → **Permissions** → **CORS**
Link: https://docs.aws.amazon.com/AmazonS3/latest/userguide/ManageCorsUsing.html
2. Add this configuration:
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": ["ETag"],
        "MaxAgeSeconds": 3000
    }
]
```
3. **Save changes**

### 3.3 Make Photo Bucket Publicly Readable
1. Select photo bucket → **Permissions** → **Block public access**
2. **Edit** → Uncheck all boxes → **Save changes**
3. Type `confirm` when prompted
4. Go to **Bucket policy** → **Edit**
5. Add this policy (replace bucket name):
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::photo-gallery-bucket-mumbai-[your-suffix]/*"
        }
    ]
}
```
6. **Save changes**

### 3.4 Create Website Hosting Bucket
1. **Create bucket** → **Bucket name**: `photo-gallery-website-mumbai-[your-suffix]`
2. **Region**: Asia Pacific (Mumbai) ap-south-1
3. **Block Public Access**: Keep default for now
4. **Create bucket**

### 3.5 Configure Website Hosting
1. Select website bucket → **Properties** → **Static website hosting**
2. **Edit** → **Enable**
3. **Index document**: `index.html`
4. **Error document**: `index.html`
5. **Save changes**
6. Note the **Bucket website endpoint** URL

### 3.6 Make Website Bucket Public
1. **Permissions** → **Block public access** → **Edit**
2. Uncheck all boxes → **Save changes** → Type `confirm`
3. **Bucket policy** → **Edit** → Add this policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::photo-gallery-website-mumbai-[your-suffix]/*"
        }
    ]
}
```
4. **Save changes**

## Step 4: Create Lambda Functions

### 4.1 Create listPhotos Function
1. Go to **Lambda Console** → **Create function**
2. **Function name**: `listPhotos`
3. **Runtime**: Python 3.9
4. **Execution role**: Use existing role → `photo-gallery-lambda-role`
5. **Create function**

6. Replace the default code with the code i have shared
7. **Deploy**

### 4.2 Create uploadPhoto Function
1. **Create function** → **Function name**: `uploadPhoto`
2. **Runtime**: Python 3.9
3. **Execution role**: Use existing role → `photo-gallery-lambda-role`
4. **Create function**

5. Replace code with (update bucket name):

Replace the default code with the code i have shared

6. **Deploy**

## Step 5: Create API Gateway

### 5.1 Create REST API
1. Go to **API Gateway Console** → **Create API**
2. **REST API** → **Build**
3. **API name**: `PhotoGalleryAPI`
4. **Region**: ap-south-1
5. **Create API**

### 5.2 Create /photos Resource
1. **Actions** → **Create Resource**
2. **Resource Name**: `photos`
3. **Create Resource**

### 5.3 Create GET Method
1. Select `/photos` → **Actions** → **Create Method** → **GET**
2. **Integration type**: Lambda Function
3. **Lambda Region**: ap-south-1
4. **Lambda Function**: `listPhotos`
5. **Save** → **OK** (to add permission)

### 5.4 Create POST Method
1. Select `/photos` → **Actions** → **Create Method** → **POST**
2. **Integration type**: Lambda Function
3. **Lambda Region**: ap-south-1
4. **Lambda Function**: `uploadPhoto`
5. **Save** → **OK**

### 5.5 Enable CORS
1. Select `/photos` → **Actions** → **Enable CORS**
2. **Access-Control-Allow-Origin**: `*`
3. **Access-Control-Allow-Headers**: `Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token`
4. **Access-Control-Allow-Methods**: Select GET, POST, OPTIONS
5. **Enable CORS and replace existing CORS headers**

### 5.6 Deploy API
1. **Actions** → **Deploy API**
2. **Deployment stage**: New Stage
3. **Stage name**: `prod`
4. **Deploy**
5. **Note the Invoke URL** (e.g., `https://abc123.execute-api.ap-south-1.amazonaws.com/prod`)


## Step 6: Create Frontend

### 6.1 Create index.html
Create a file named `index.html` with this content (update API_URL and bucket name):

Use Index.html webpage

### 6.2 Update Frontend Configuration
Before uploading, update these values in the HTML:
1. **Line 185**: Replace `YOUR-API-ID` with your actual API Gateway ID
2. **Line 295**: Replace `[your-suffix]` with your actual bucket suffix

### 6.3 Upload Frontend to S3
1. Go to your website bucket → **Upload**
2. **Add files** → Select your `index.html` file
3. **Upload**
