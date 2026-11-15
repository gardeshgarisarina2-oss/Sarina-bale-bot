import os
import requests

token = os.environ["BALE_TOKEN"]
url = f"https://tapi.bale.ai/bot{token}/sendMessage"

response = requests.post(url, json={
    "chat_id": "@afsaneh_gardeshgari_sarina",
    "text": "تست اتصال خودکار سارینا ❤️"
})

print("Status:", response.status_code)
print("Response:", response.text)

response.raise_for_status()