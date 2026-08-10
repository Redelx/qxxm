def handler(event, context):
    return {
        "statusCode": 200,
        "body": '{"message": "API is working!"}',
        "headers": {
            "Content-Type": "application/json"
        }
    }
