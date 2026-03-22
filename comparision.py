import os
import json
import base64
import io
from groq import Groq 
from PIL import Image
from state import ClaimState
from dotenv import load_dotenv
import boto3
load_dotenv()
api=os.environ.get("GROQ")
client = Groq(api_key=api)

def comparison_node(state: ClaimState):
    print("comparision")
    
    def resized(url):
        
        s3 = boto3.client('s3',region_name="ap-south-1")
        response = s3.get_object(Bucket="claimguard", Key=url)
        img = Image.open(io.BytesIO(response['Body'].read()))
        img.thumbnail((1024, 1024)) 
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        temp=base64.b64encode(buffer.getvalue())
        return temp.decode('utf-8')
        

    try:
        check_in =resized(state['check_in_url'])
        check_out  = resized(state['check_out_url'])

        
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "Compare these 'Before' and 'After' images. Return ONLY a JSON list of new damages: [{'item': 'string', 'issue': 'string', 'severity': 'Low/Medium/High'}]"
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{check_in}"}
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{check_out}"}
                        }
                    ]
                }
            ],
            temperature=0.1, 
            response_format={"type": "json_object"}
        )

      
        raw_content = completion.choices[0].message.content
        
       
        ai_data = json.loads(raw_content)
        
        
        if isinstance(ai_data, dict) and "damages" in ai_data:
            anamolies = ai_data["damages"]
        else:
            anamolies = [ai_data] if ai_data else []

        print(f"detected {len(anamolies)} issues.")
        return {"anamolies": anamolies, "status": "Groq Comparison Done"}

  

    except Exception as e:
        print(f"Groq Error: {e}")
        return {"status": f"Error in Groq: {str(e)}", "anamolies": []}
