import json
import boto3 
import pandas as pd 
def lambda_handler(event, context):
    # TODO implement
    bucket=event['Records'][0]['s3']['bucket']['name']
    key=event['Records'][0]['s3']['object']['key']
    
    #s3 cilent
    s3_client=boto3.client('s3')
    response=s3_client.get_object(
        Bucket=bucket,
        Key=key
    )
    print(response)
   # Read and decode the body
    content = response['Body'].read().decode('utf-8')
    print("Content",content)

    json_dicts = content.strip().split('\n')
    print("JSON", json_dicts)

    data = []
    for line in json_dicts:
        py_dict=json.loads(line)
        if py_dict['status']=='delivered':
            data.append(py_dict)

    #convert to dataframe 
    df=pd.DataFrame(data)
    print("DATAFRAME head",df.head())
    print("DATAFRAME",df)
    # Now you can work with `data` as a list of dictionaries
    df.to_csv('/tmp/processed.csv',index=False)
    s3_client.upload_file('/tmp/processed.csv', 'doordash-target-zn-12', 'processed.csv')
    print("Successfull upload ")

    # triggerin the SNS
    sns=boto3.client('sns')
    sns.publish(
        TopicArn='arn:aws:sns:eu-north-1:304783065894:airbnb-notification',
        Subject='Doordash',
        Message='Doordash data processed and uploaded to S3'
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
