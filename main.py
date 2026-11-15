import os
import requests

token = os.environ["BALE_TOKEN"]
url = f"https://tapi.bale.ai/bot{token}/sendMessage"

response = requests.post(url, json={
    "chat_id": "@afsaneh_gardeshgari_sarina",
    "text": "تست اتصال خودکار سارینا ❤️"
})

print(response.status_code)
print(response.text)