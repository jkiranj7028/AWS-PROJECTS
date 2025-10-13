# Welcome to your CDK TypeScript project

This is a blank project for CDK development with TypeScript.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

## Useful commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `npx cdk deploy`  deploy this stack to your default AWS account/region
* `npx cdk diff`    compare deployed stack with current state
* `npx cdk synth`   emits the synthesized CloudFormation template


--------------

Serverless Web App with AWS CDK (TypeScript)

This project uses the AWS Cloud Development Kit (CDK) with TypeScript to deploy a serverless architecture on AWS. It includes:

- API Gateway for HTTP endpoints  
- Lambda function for backend logic  
- DynamoDB table for data storage  
- Optional: S3 bucket for static frontend hosting

Project Structure:
serverless-app/
├── bin/                      # Entry point for CDK app
├── lib/                      # Stack definitions
├── lambda/                   # Lambda function code
├── package.json              # Project metadata
├── tsconfig.json             # TypeScript config
└── cdk.json                  # CDK config

Setup Instructions:

1. Install AWS CDK CLI
npm install -g aws-cdk

2. Initialize CDK Project
mkdir serverless-app && cd serverless-app
cdk init app -l typescript

3. Install Required Packages
npm install @aws-cdk/aws-lambda @aws-cdk/aws-dynamodb @aws-cdk/aws-apigateway

Define Infrastructure (lib/serverless-app-stack.ts):

import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';

export class ServerlessAppStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const table = new dynamodb.Table(this, 'ItemsTable', {
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
    });

    const handler = new lambda.Function(this, 'ItemsHandler', {
      runtime: lambda.Runtime.NODEJS_18_X,
      code: lambda.Code.fromAsset('lambda'),
      handler: 'index.handler',
      environment: {
        TABLE_NAME: table.tableName,
      },
    });

    table.grantReadWriteData(handler);

    new apigateway.LambdaRestApi(this, 'Endpoint', {
      handler,
    });
  }
}

Lambda Function Code (lambda/index.js):

const AWS = require('aws-sdk');
const db = new AWS.DynamoDB.DocumentClient();
const tableName = process.env.TABLE_NAME;

exports.handler = async (event) => {
  const data = await db.scan({ TableName: tableName }).promise();
  return {
    statusCode: 200,
    body: JSON.stringify(data.Items),
  };
};

Deploy the Stack:
npm run build
cdk synth
cdk deploy

Verify Deployment:
After deployment, CDK will output an API Gateway endpoint. You can test it using:
curl https://your-api-id.execute-api.region.amazonaws.com/

Notes:
- You can extend the Lambda to support POST/PUT methods.
- Add authentication using Cognito or IAM if needed.
- For frontend hosting, add an S3 bucket and deploy static assets.

Resources:
- AWS CDK Docs: https://docs.aws.amazon.com/cdk/v2/guide/home.html
- TypeScript CDK Tutorial: https://bobbyhadz.com/blog/aws-cdk-tutorial-typescript

Author:
Created by J — blending DevOps mastery with creative education.
Feel free to fork, extend, or remix for your own learning dashboards!

Result:

You’ll get a public API endpoint that returns data from DynamoDB via Lambda. You can extend this with POST/PUT methods, add authentication, or connect it to a frontend hosted in S3.
---------------
Extra Explaination:

When you're building a serverless application, a common pattern involves using AWS services like API Gateway, Lambda, and DynamoDB. Let's break down the flow and then visualize it with a diagram.

Here's how data typically flows from a public API endpoint to DynamoDB via Lambda, and how you can extend it:

1. The Core Data Flow (GET Request)

Public API Endpoint (AWS API Gateway): This is the entry point for your application. When a user or client sends an HTTP request (like a GET request to retrieve data), it first hits this endpoint. API Gateway acts as a "front door" for your serverless applications. It handles routing, security, and traffic management.

Lambda Function (AWS Lambda): API Gateway is configured to trigger a specific Lambda function in response to certain API requests. When a GET request comes in, Lambda executes your code without you having to provision or manage servers. This function contains the logic to interact with your database.

DynamoDB (AWS DynamoDB): This is your fully managed NoSQL database. The Lambda function will contain code to query or scan DynamoDB tables to retrieve the requested data. DynamoDB is highly scalable and performant.

Diagram for Core Data Flow (GET Request):

+-------------------+     +-----------------+     +-----------------+
|   Client/User     |     |  API Gateway    |     |    Lambda       |
| (Web/Mobile App)  | --> | (Public API     | --> | (Function Code  |
|                   |     |   Endpoint)     |     |   to get data)  |
+-------------------+     +-----------------+     +-------+---------+
                                                          |
                                                          v
                                                    +-----+-----+
                                                    |  DynamoDB   |
                                                    | (NoSQL DB)  |
                                                    +-------------+
Here's a visual representation:



2. Extending with POST/PUT Methods

To add POST (create new data) and PUT (update existing data) methods:

API Gateway Configuration: You would configure API Gateway to accept POST and PUT requests on specific paths (e.g., /items for POST and /items/{id} for PUT).

New Lambda Functions (or branching logic):

For POST, you'd have a Lambda function that takes the new data from the request body and uses DynamoDB's putItem operation to create a new record.

For PUT, a Lambda function would take an item ID (from the path or query parameters) and the updated data from the request body, then use DynamoDB's updateItem operation.

Note: You could use separate Lambda functions for each HTTP method/path or have a single Lambda function that uses logic to determine the operation based on the incoming request's HTTP method.

Diagram for POST/PUT Extension:

+-------------------+     +-----------------+     +-----------------+     +-----------------+
|   Client/User     |     |  API Gateway    |     |    Lambda       |     |    DynamoDB     |
| (Web/Mobile App)  | --> | (POST /items)   | --> | (Function Code  | --> | (putItem)       |
|                   |     | (PUT /items/{id})| --> |   to add/update)|     |                 |
+-------------------+     +-----------------+     +-----------------+     +-----------------+
3. Adding Authentication

Authentication secures your API endpoints, ensuring only authorized users can access or modify data.

API Gateway Authorizers: API Gateway supports different types of authorizers:

Lambda Authorizers: Your own custom Lambda function that validates tokens (e.g., JWTs from Auth0, Okta, or your own system) or credentials.

Cognito User Pool Authorizers: Integrates directly with AWS Cognito User Pools, a managed service for user sign-up, sign-in, and access control. This is a very common choice for serverless applications.

Diagram for Authentication Extension:

+-------------------+     +-----------------+     +-------------------+     +-----------------+
|   Client/User     |     |  API Gateway    |     | Authentication    |     |    Lambda       |
| (Web/Mobile App)  | --> | (Public API     | --> |  Service          | --> | (Function Code  |
|                   |     |   Endpoint)     |     |  (e.g., Cognito,  |     |   to get data)  |
|                   |     |  (Auth Enabled) |     |  Lambda Authorizer)|     |                 |
+-------------------+     +-----------------+     +-------------------+     +-------+---------+
                                                                                      |
                                                                                      v
                                                                                +-----+-----+
                                                                                |  DynamoDB   |
                                                                                +-------------+
4. Connecting to a Frontend Hosted in S3

For a static website frontend (HTML, CSS, JavaScript), AWS S3 is a perfect hosting solution.

Amazon S3 (Static Website Hosting): You can configure an S3 bucket to serve static website content. When users access your domain (e.g., yourwebapp.com), S3 serves the index.html and other assets.

Frontend-API Interaction: Your JavaScript code in the S3-hosted frontend will make HTTP requests to your API Gateway endpoints to fetch, create, update, or delete data.

Diagram for Frontend Extension:

+-------------------+     +-----------------+     +-----------------+     +-----------------+
|   Client/User     |     |  Amazon S3      |     |  API Gateway    |     |    Lambda       |
| (Web Browser)     | --> | (Static Website | --> | (Public API     | --> | (Function Code) |
|                   |     |   Hosting)      |     |   Endpoint)     |     |                 |
|                   |     |   (index.html,  |     |                 |     |                 |
|                   |     |    app.js)      |     |                 |     |                 |
+-------------------+     +-----------------+     +-----------------+     +-------+---------+
                                                                                      |
                                                                                      v
                                                                                +-----+-----+
                                                                                |  DynamoDB   |
                                                                                +-------------+