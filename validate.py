import boto3
from state import ClaimState
client=boto3.client('rekognition',region_name='ap-south-1')

def input_validation_node(state:ClaimState):
    
    keys = [state['check_in_url'], state['check_out_url']]

    for key in keys:
            response = client.detect_labels(
                Image={'S3Object': {'Bucket': 'claimguard', 'Name': key}},
                MaxLabels=5,
                MinConfidence=75
            )
    
            if len(response['Labels'])>0:
                print(f"validation successful : Found{response['Labels'][0]['Name']}")
                return {"is_image_clear":True,"status":"Valid image Detected"}
            
            else:
                print("Validation Fail")
                return {"is_image_clear":False,"status":"invalid image"}