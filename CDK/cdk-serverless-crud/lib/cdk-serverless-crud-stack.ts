// lib/cdk-serverless-crud-stack.ts
import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs';
import { Construct } from 'constructs';
import * as path from 'path';

// lib/cdk-serverless-crud-stack.ts (continued)
// ... (imports and NotesTable definition as before)

// ...existing code...

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
      runtime: lambda.Runtime.NODEJS_18_X,
      entry: path.join(__dirname, '../lambda/notesHandler.ts'),
      handler: 'handler',
      environment: {
        TABLE_NAME: notesTable.tableName,
      },
      bundling: {
        forceDockerBundling: false,
      }
    });

    // 3. Grant Lambda permissions to read/write to the DynamoDB table
    notesTable.grantReadWriteData(notesLambda);

    // 4. Create an API Gateway REST API
    const api = new apigw.RestApi(this, 'NotesApi', {
      restApiName: 'Notes Service',
      description: 'This service serves notes.',
      deployOptions: {
        stageName: 'dev',
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigw.Cors.ALL_ORIGINS,
        allowMethods: apigw.Cors.ALL_METHODS,
        allowHeaders: [
          'Content-Type',
          'X-Amz-Date',
          'Authorization',
          'X-Api-Key',
          'X-Amz-Security-Token'
        ],
      }
    });

    // Create a proxy resource that routes all paths to the Lambda function
    const notesResource = api.root.addResource('notes');
    const notesIdResource = notesResource.addResource('{id}');

    // Integrate the Lambda function
    const notesIntegration = new apigw.LambdaIntegration(notesLambda);

    // Add methods for /notes
    notesResource.addMethod('GET', notesIntegration);
    notesResource.addMethod('POST', notesIntegration);

    // Add methods for /notes/{id}
    notesIdResource.addMethod('GET', notesIntegration);
    notesIdResource.addMethod('PUT', notesIntegration);
    notesIdResource.addMethod('DELETE', notesIntegration);

    // Output the API URL for easy access
    new cdk.CfnOutput(this, 'ApiUrl', {
      value: api.url,
      description: 'The URL of the API Gateway endpoint',
    });
  }
}