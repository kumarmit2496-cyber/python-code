import boto3

#1.Connect to bedrock(must enabled in your aws account)
client = boto3.client(
     "bedrock-runtime",
     region_name="us-east-1",
)
#print("Amazon Bedrock client created sucessfully")
#2.pick the model (must be enabled in your AWS account)
MODEL_ID = "amazon.nova-micro-v1:0"

#Function: takes question ,return answer
def ask_bot(question):
    response = client.converse(
         model_id=MODEL_ID,
        message=[
            {
                "role":"user",
                "content":[{"text":question}],


            }
        ]
    )
    return response["output"]["message"]["content"][0]["text"]


#4. use it
if __name__ == "__main__":
    answer = ask_bot("What is GEN AI?")
    print(answer)