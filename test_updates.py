import os
import requests

TOKEN = os.environ["BALE_TOKEN"]

url = f"https://tapi.bale.ai/bot{TOKEN}/getUpdates"

response = requests.get(url, timeout=30)
print(response.status_code)
print(response.text)