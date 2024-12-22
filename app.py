import boto3 #this is from aws to invoke python
import botocore.config
import json
from datetime import datetime


def blog_generator_bedrock(message:str):
    prompt=f"Write a 100 words creative blog on the topic {blogtopic}"

    body={
        "prompt": prompt,
        "parameters":{
            "max_new_tokens":512,
            "top_p":0.9,
            "temperature":0.6
        }
    }

    try:
        bedrock=boto3.client("bedrock-runtime",region_name="us-east-1",
                             config=botocore.config.Config(read_timeout=300,retries={"max_attempts":3}))
        response = bedrock.invoke_model(body=json.dumps(body),modelId="meta.llama3-2-1b-instruct-v1:0")              
        response_content = response.get('body').read()
        res_data=json.loads(response_content)
        blog_details=res_data['generation']
        return blog_details
    except Exception as e:
        print(f"Error",{e})

    

def save_to_s3(s3_key,s3_name,blog):
    s3=boto3.client('s3')

    try:
        s3.put_object(Bucket = s3_name, Key=s3_key, Body=blog)
        print("Code saved to s3")
    except Exception as e:
        print(f"Error in s3", {e})




def lambda_handler(event, context):
    # TODO implement
    event = json.loads(event['body'])
    blogtopic = event['blog_topic']

    blog_gen=blog_generator_bedrock(blogtopic=blogtopic)

    if blog_gen:
        current_time=datetime.now().strftime('%H%M%S')
        s3_bucket_key=f"blog-bucket/{current_time}.txt"
        s3_bucket_name="first_bedrock"
        save_to_s3(s3_bucket_key,s3_bucket_name, blog_gen)

    else:
        print("No blogs generated")


    return{
        'status':200,
        "body": json.dumps("Blog Generated")
    }




