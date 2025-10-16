Okay, let's create a real-time project using the AWS CDK (Cloud Development Kit) CLI with TypeScript. This project will set up a simple serverless backend that allows users to create, read, update, and delete (CRUD) items. We'll use:

AWS Lambda: For backend logic (our API handlers).

Amazon API Gateway: To create a REST API endpoint.

Amazon DynamoDB: A NoSQL database to store our items.

TypeScript: For writing our CDK constructs and Lambda code.

This project will demonstrate:

CDK Project Setup: Initializing a CDK project.

Infrastructure as Code: Defining Lambda functions, DynamoDB tables, and API Gateway using TypeScript.

Lambda Code Deployment: Packaging and deploying TypeScript Lambda code.

CRUD Operations: Basic API for managing items.

Project: Serverless CRUD API with CDK, Lambda, and DynamoDB
Goal: Build a serverless API where users can manage a list of notes (or any simple item).

Features:

POST /notes: Create a new note.

GET /notes: Get all notes.

GET /notes/{id}: Get a specific note by ID.

PUT /notes/{id}: Update an existing note.

DELETE /notes/{id}: Delete a note.

Step-by-Step Implementation
1. Prerequisites:

Before you start, make sure you have:

Node.js and npm (or yarn): Installed on your machine.

AWS CLI: Configured with credentials for an AWS account.

AWS CDK CLI: Installed globally (npm install -g aws-cdk).

Git: (Optional, but good for version control).

2. Initialize a New CDK Project

Create a new directory for your project and initialize the CDK:

Bash
mkdir cdk-serverless-crud
cd cdk-serverless-crud
cdk init app --language typescript

This command creates a new CDK project with a basic structure, including lib/cdk-serverless-crud-stack.ts (where your infrastructure will be defined) and bin/cdk-serverless-crud.ts (the entry point for your CDK app).

3. Define the DynamoDB Table

Edit lib/cdk-serverless-crud-stack.ts to define your DynamoDB table.

TypeScript

// lib/cdk-serverless-crud-stack.ts
import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs';
import { Construct } from 'constructs';
import * as path from 'path';

export class CdkServerlessCrudStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // 1. Create a DynamoDB Table
    const notesTable = new dynamodb.Table(this, 'NotesTable', {
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      tableName: 'Notes', // A friendly name for the table
      removalPolicy: cdk.RemovalPolicy.DESTROY, // NOT for production! Deletes table on stack deletion.
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST, // Serverless billing
    });

    // We will add Lambda and API Gateway here later.
  }
}
Explanation:

partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING }: Defines the primary key for our notes, which will be a unique string id.

tableName: 'Notes': Gives our table a human-readable name.

removalPolicy: cdk.RemovalPolicy.DESTROY: CAUTION! This is great for development as it cleans up the table when you cdk destroy. For production, you'd typically use cdk.RemovalPolicy.RETAIN or SNAPSHOT to prevent accidental data loss.

billingMode: dynamodb.BillingMode.PAY_PER_REQUEST: A serverless billing model, you only pay for what you use.

4. Create Lambda Functions for CRUD Operations

We'll create a single Lambda function that handles all CRUD operations and routes requests based on the HTTP method and path. This is a common pattern often called a "proxy" or "catch-all" Lambda.

First, create a new directory for your Lambda code:

Bash

mkdir lambda
Now, create the Lambda function's TypeScript code:

TypeScript

// lambda/notesHandler.ts
import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, GetCommand, PutCommand, DeleteCommand, ScanCommand, UpdateCommand } from '@aws-sdk/lib-dynamodb';
import { v4 as uuidv4 } from 'uuid'; // For generating unique IDs

const ddbClient = new DynamoDBClient({});
const ddbDocClient = DynamoDBDocumentClient.from(ddbClient);

const TABLE_NAME = process.env.TABLE_NAME || 'Notes'; // Our table name will be passed as an environment variable

export const handler = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
    console.log('Request event: ', event);

    let body;
    let statusCode = 200;
    const headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*', // CORS for local development
        'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT,DELETE',
        'Access-Control-Allow-Headers': 'Content-Type',
    };

    try {
        switch (event.httpMethod) {
            case 'GET':
                if (event.pathParameters && event.pathParameters.id) {
                    // GET /notes/{id}
                    body = await ddbDocClient.send(new GetCommand({
                        TableName: TABLE_NAME,
                        Key: { id: event.pathParameters.id },
                    }));
                } else {
                    // GET /notes
                    body = await ddbDocClient.send(new ScanCommand({
                        TableName: TABLE_NAME,
                    }));
                }
                break;

            case 'POST':
                // POST /notes
                const item = JSON.parse(event.body || '{}');
                item.id = uuidv4(); // Generate a unique ID
                item.createdAt = new Date().toISOString();
                await ddbDocClient.send(new PutCommand({
                    TableName: TABLE_NAME,
                    Item: item,
                }));
                body = { message: 'Item created successfully', item };
                break;

            case 'PUT':
                // PUT /notes/{id}
                const updateId = event.pathParameters?.id;
                const updateData = JSON.parse(event.body || '{}');
                delete updateData.id; // Prevent updating the ID
                
                const updateExpressionParts: string[] = [];
                const expressionAttributeValues: { [key: string]: any } = {};

                for (const key in updateData) {
                    if (Object.prototype.hasOwnProperty.call(updateData, key)) {
                        updateExpressionParts.push(`${key} = :${key}`);
                        expressionAttributeValues[`:${key}`] = updateData[key];
                    }
                }

                if (updateExpressionParts.length === 0) {
                    throw new Error('No update data provided.');
                }

                const updateResult = await ddbDocClient.send(new UpdateCommand({
                    TableName: TABLE_NAME,
                    Key: { id: updateId },
                    UpdateExpression: 'SET ' + updateExpressionParts.join(', '),
                    ExpressionAttributeValues: expressionAttributeValues,
                    ReturnValues: 'ALL_NEW', // Return the updated item
                }));
                body = { message: 'Item updated successfully', item: updateResult.Attributes };
                break;

            case 'DELETE':
                // DELETE /notes/{id}
                await ddbDocClient.send(new DeleteCommand({
                    TableName: TABLE_NAME,
                    Key: { id: event.pathParameters?.id },
                }));
                body = { message: `Item with id ${event.pathParameters?.id} deleted.` };
                break;

            case 'OPTIONS':
                // Handle CORS preflight requests
                statusCode = 204; // No content, just headers
                break;

            default:
                throw new Error(`Unsupported method: ${event.httpMethod}`);
        }
    } catch (err: any) {
        console.error(err);
        statusCode = 400;
        body = { error: err.message };
    } finally {
        body = JSON.stringify(body);
    }

    return {
        statusCode,
        body,
        headers,
    };
};
Dependencies for Lambda Code:

You'll need to install these in your cdk-serverless-crud project's root:

Bash

npm install @aws-sdk/client-dynamodb @aws-sdk/lib-dynamodb uuid @types/aws-lambda @types/uuid
5. Integrate Lambda and API Gateway in CDK Stack

Now, go back to lib/cdk-serverless-crud-stack.ts and add the Lambda function and API Gateway. We'll use @aws-cdk/aws-lambda-nodejs (NodejsFunction) which is great for TypeScript Lambdas as it handles bundling your code with esbuild.

TypeScript

// lib/cdk-serverless-crud-stack.ts (continued)
// ... (imports and NotesTable definition as before)

export class CdkServerlessCrudStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // 1. Create a DynamoDB Table
    const notesTable = new dynamodb.Table(this, 'NotesTable', {
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      tableName: 'Notes',
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
    });

    // 2. Create the Lambda function
    const notesLambda = new NodejsFunction(this, 'NotesHandler', {
      runtime: lambda.Runtime.NODEJS_18_X, // Or latest LTS Node.js
      entry: path.join(__dirname, '../lambda/notesHandler.ts'), // Path to your Lambda code
      handler: 'handler', // The name of the exported function in your code
      environment: {
        TABLE_NAME: notesTable.tableName, // Pass the table name as an environment variable
      },
      bundling: {
        // This ensures uuid is correctly bundled if it has CJS/ESM issues
        // It's good practice for smaller utilities like uuid
        forceDockerBundling: false, // Set to true if you face bundling issues without Docker
      }
    });

    // 3. Grant Lambda permissions to read/write to the DynamoDB table
    notesTable.grantReadWriteData(notesLambda);

    // 4. Create an API Gateway REST API
    const api = new apigw.RestApi(this, 'NotesApi', {
      restApiName: 'Notes Service',
      description: 'This service serves notes.',
      deployOptions: {
        stageName: 'dev', // Our development stage
      },
      defaultCorsPreflightOptions: { // Enable CORS for local development
        allowOrigins: apigw.Cors.ALL_ORIGINS,
        allowMethods: apigw.Cors.ALL_METHODS, // This includes OPTIONS
        allowHeaders: apigw.Cors.DEFAULT_HEADERS,
      }
    });

    // Create a proxy resource that routes all paths to the Lambda function
    // and handles all HTTP methods (GET, POST, PUT, DELETE, OPTIONS)
    const notesResource = api.root.addResource('notes');
    const notesIdResource = notesResource.addResource('{id}');

    // Integrate the Lambda function
    const notesIntegration = new apigw.LambdaIntegration(notesLambda);

    // Add methods for /notes
    notesResource.addMethod('GET', notesIntegration);
    notesResource.addMethod('POST', notesIntegration);
    notesResource.addMethod('OPTIONS', notesIntegration); // For CORS preflight

    // Add methods for /notes/{id}
    notesIdResource.addMethod('GET', notesIntegration);
    notesIdResource.addMethod('PUT', notesIntegration);
    notesIdResource.addMethod('DELETE', notesIntegration);
    notesIdResource.addMethod('OPTIONS', notesIntegration); // For CORS preflight

    // Output the API URL for easy access
    new cdk.CfnOutput(this, 'ApiUrl', {
      value: api.url,
      description: 'The URL of the API Gateway endpoint',
    });
  }
}
Explanation:

NodejsFunction: This construct automatically bundles your TypeScript Lambda code using esbuild.

if any issue happened run this:
Check your environment:
Ensure you have esbuild installed locally (required for local bundling):
npm install --save-dev esbuild

entry: Points to your notesHandler.ts file.

handler: The name of the exported function (handler) in notesHandler.ts.

environment: Passes the DynamoDB table name to the Lambda function.

notesTable.grantReadWriteData(notesLambda): This is crucial! It automatically creates the necessary IAM policy permissions for your Lambda function to interact with your DynamoDB table.

apigw.RestApi: Defines your API Gateway.

defaultCorsPreflightOptions: Important for web applications; enables Cross-Origin Resource Sharing (CORS) so your frontend (e.g., running on localhost:3000) can talk to your API.

api.root.addResource('notes'): Creates the /notes path.

notesResource.addResource('{id}'): Creates the /notes/{id} path, where {id} is a path parameter.

apigw.LambdaIntegration(notesLambda): Connects the API Gateway method to your Lambda function.

addMethod('GET', notesIntegration): Configures API Gateway to trigger notesLambda for GET requests on /notes and /notes/{id}. We do this for all relevant HTTP methods.

CfnOutput: Prints the API Gateway URL to your console after deployment, making it easy to test.

6. Install CDK Dependencies

Make sure you have all necessary CDK packages installed:

Bash

npm install aws-cdk-lib @aws-cdk/aws-lambda-nodejs constructs
npm install --save-dev @types/node @types/aws-lambda @types/uuid typescript
7. Bootstrap Your AWS Environment (First Time Only)

If you haven't used CDK in this AWS account/region before, you need to bootstrap it:

Bash

cdk bootstrap aws://YOUR_AWS_ACCOUNT_ID/YOUR_AWS_REGION
Replace YOUR_AWS_ACCOUNT_ID and YOUR_AWS_REGION with your actual AWS account ID and desired region (e.g., us-east-1).

8. Deploy the Stack

Now, deploy your infrastructure!

Bash

cdk deploy
The CDK CLI will show you the changes it's about to make and ask for confirmation. Type y and press Enter.

This will:

Compile your TypeScript Lambda code.

Create a CloudFormation stack.

Provision the DynamoDB table, Lambda function, and API Gateway.

Output the API Gateway URL.

9. Test Your API

Once cdk deploy completes, you'll see an ApiUrl output. Copy that URL (e.g., https://xxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/).

You can use curl, Postman, Insomnia, or a simple JavaScript fetch in a browser console to test.

Example curl commands (replace YOUR_API_URL):

Create a Note (POST):

Bash

curl -X POST -H "Content-Type: application/json" -d '{"title": "My First Note", "content": "This is the content of my first note."}' YOUR_API_URL/notes
Create another Note (POST):

Bash

curl -X POST -H "Content-Type: application/json" -d '{"title": "Groceries", "content": "Milk, Eggs, Bread."}' YOUR_API_URL/notes
Get All Notes (GET):

Bash

curl YOUR_API_URL/notes
You should see an array of your notes. Copy one of the id values for the next tests.

Get a Specific Note (GET by ID):

Bash

curl YOUR_API_URL/notes/COPIED_NOTE_ID # Replace COPIED_NOTE_ID with an actual ID
Update a Note (PUT by ID):

Bash

curl -X PUT -H "Content-Type: application/json" -d '{"content": "Updated content for my first note!", "status": "completed"}' YOUR_API_URL/notes/COPIED_NOTE_ID
Delete a Note (DELETE by ID):

Bash

curl -X DELETE YOUR_API_URL/notes/COPIED_NOTE_ID
10. Clean Up

When you're done, you can remove all the deployed resources using:

Bash

cdk destroy
This will delete the CloudFormation stack, including the DynamoDB table, Lambda function, and API Gateway. Since we used cdk.RemovalPolicy.DESTROY for the table, the data will also be deleted.