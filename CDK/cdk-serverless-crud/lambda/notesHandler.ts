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
