import boto3 #this is from aws to invoke python
import botocore.config
import json
from datetime import datetime


def topic_generator_bedrock(topic:str):
    prompt=f"Provide information with proper details for {topic}"

#as per the model that we are using it requires the body

    body={
        "prompt": prompt,
        "parameters":{
            "max_new_tokens":512,
            "top_p":0.9,
            "temperature":0.6
        }
    }

#Using boto3 you can use the aws by calling it's client
    try:
        bedrock=boto3.client("bedrock-runtime",region_name="us-east-1",
                             config=botocore.config.Config(read_timeout=300,retries={"max_attempts":3}))
        response = bedrock.invoke_model(body=json.dumps(body),modelId="meta.llama3-2-1b-instruct-v1:0")              
        response_content = response.get('body').read()
        res_data=json.loads(response_content)
        topic_details=res_data['generation']
        return topic_details
    except Exception as e:
        print(f"Error",{e})


#whatever the response we get it will be stored in S3 bucket, we can verify this in cloudwatch too.

def save_to_s3(s3_key,s3_name,topic):
    s3=boto3.client('s3')

    try:
        s3.put_object(Bucket = s3_name, Key=s3_key, Body=topic)
        print("Code saved to s3")
    except Exception as e:
        print(f"Error in s3", {e})



#using lambda function to generate the connection. In the AMC i have added the API gateway to trigger the lambda function
def lambda_handler(event, context):
    event = json.loads(event['body'])
    topic = event['topic_']

    topic_gen=topic_generator_bedrock(topic=topic)

    if topic_gen:
        current_time=datetime.now().strftime('%H%M%S')
        s3_bucket_key=f"topic-bucket/{current_time}.txt"
        s3_bucket_name="first_bedrock"
        save_to_s3(s3_bucket_key,s3_bucket_name, topic_gen)

    else:
        print("No topics generated")


    return{
        'status':200,
        "body": json.dumps("topic Generated")
    }




